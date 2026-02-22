
import re
import pandas as pd
import pdfplumber
import json
import os



# Tesseract OCR Configuration
# Resolves the executable path from system PATH or fallback directories.
tesseract_cmd_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\LENOVO\AppData\Local\Tesseract-OCR\tesseract.exe"
]

try:
    from PIL import Image, ImageEnhance
    import pytesseract
    
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        for path in tesseract_cmd_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
except ImportError:
    pass

# 1. HELPER CLASSES


class Preprocessor:
    def __init__(self):
        self.column_mapping = {
            # CBC
            'hb': 'Haemoglobin', 'hemoglobin': 'Haemoglobin', 'hgb': 'Haemoglobin', 'hbg': 'Haemoglobin',
            'platelets': 'Platelets', 'platelet count': 'Platelets', 'plt': 'Platelets', 'thrombocytes': 'Platelets',
            'wbc': 'White Blood Cells', 'white blood cells': 'White Blood Cells', 'tlc': 'White Blood Cells', 'total leucocyte count': 'White Blood Cells',
            'rbc': 'RBC Count', 'red blood cells': 'RBC Count', 'erythrocytes': 'RBC Count',
            'pcv': 'Packed Cell Volume', 'hct': 'Packed Cell Volume', 'hematocrit': 'Packed Cell Volume',
            'mcv': 'Mean Corpuscular Volume',
            'mch': 'Mean Corpuscular Hemoglobin',
            'mchc': 'Mean Corpuscular Hemoglobin Concentration',
            'rdw': 'Red Cell Distribution Width', 'rdw-cv': 'Red Cell Distribution Width', 'rdw-sd': 'Red Cell Distribution Width',
            'esr': 'Erythrocyte Sedimentation Rate',
            
            # Differential
            'neutrophils': 'Neutrophils', 'neu': 'Neutrophils', 'neuts': 'Neutrophils', 'polymorphs': 'Neutrophils', 'poly': 'Neutrophils', 'gra': 'Neutrophils', # Approximate GRA as Neutrophils for this dataset
            'lymphocytes': 'Lymphocytes', 'lym': 'Lymphocytes', 'lymphs': 'Lymphocytes', 'lymp': 'Lymphocytes',
            'monocytes': 'Monocytes', 'mon': 'Monocytes', 'monos': 'Monocytes', 'mono': 'Monocytes',
            'eosinophils': 'Eosinophils', 'eos': 'Eosinophils',
            'basophils': 'Basophils', 'bas': 'Basophils', 'basos': 'Basophils',
            
            # Diabetes / Metabolic
            'glucose': 'Glucose', 'fbs': 'Glucose', 'rbs': 'Glucose', 'blood sugar': 'Glucose', 'sugar': 'Glucose',
            'hba1c': 'HbA1c', 'glycated hemoglobin': 'HbA1c', 'a1c': 'HbA1c',
            
            # Lipid Profile
            'cholesterol': 'Total Cholesterol', 'total cholesterol': 'Total Cholesterol', 't.chol': 'Total Cholesterol',
            'triglycerides': 'Triglycerides', 'tg': 'Triglycerides', 'tgl': 'Triglycerides',
            'hdl': 'HDL Cholesterol', 'hdl cholesterol': 'HDL Cholesterol', 'hdl-c': 'HDL Cholesterol',
            'ldl': 'LDL Cholesterol', 'ldl cholesterol': 'LDL Cholesterol', 'ldl-c': 'LDL Cholesterol',
            
            # Kidney Function
            'creatinine': 'Creatinine', 's.creatinine': 'Creatinine', 'serum creatinine': 'Creatinine', 'creat': 'Creatinine',
            'urea': 'Urea', 'blood urea': 'Urea', 'bun': 'Urea', 'b.u.n': 'Urea',
            'uric acid': 'Uric Acid', 's.uric acid': 'Uric Acid',
            
            # Liver Function
            'bilirubin': 'Total Bilirubin', 'total bilirubin': 'Total Bilirubin', 't.bil': 'Total Bilirubin',
            'sgot': 'AST (SGOT)', 'ast': 'AST (SGOT)', 'aspartate aminotransferase': 'AST (SGOT)',
            'sgpt': 'ALT (SGPT)', 'alt': 'ALT (SGPT)', 'alanine aminotransferase': 'ALT (SGPT)',
            'alp': 'Alkaline Phosphatase', 'alkaline phosphatase': 'Alkaline Phosphatase', 'alk phos': 'Alkaline Phosphatase',
            
            # Thyroid
            'tsh': 'TSH', 'thyroid stimulating hormone': 'TSH',
            't3': 'Total T3', 'triiodothyronine': 'Total T3',
            't4': 'Total T4', 'thyroxine': 'Total T4',

            # Electrolytes
            'sodium': 'Sodium', 'na': 'Sodium', 'na+': 'Sodium', 'na++': 'Sodium',
            'potassium': 'Potassium', 'k': 'Potassium', 'k+': 'Potassium',
            'chloride': 'Chloride', 'cl': 'Chloride', 'cl-': 'Chloride', 'cl+': 'Chloride',
            'calcium': 'Calcium', 'ca': 'Calcium', 'ca++': 'Calcium', 'ca+': 'Calcium',
            
            # Coagulation
            'pt': 'PT', 'prothrombin time': 'PT',
            'ptt': 'PTT', 'partial thromboplastin time': 'PTT', 'aptt': 'APTT',
            'inr': 'INR',
            
            # Other
            'albumin': 'Albumin', 'serum albumin': 'Albumin',
            'total protein': 'Total Protein'
        }

    def normalize_column_names(self, df):
        if df.empty: return df
        # Ensure strings
        df.columns = [str(col).strip() for col in df.columns]
        new_cols = {}
        for col in df.columns:
            lower_col = col.lower()
            if lower_col in self.column_mapping:
                new_cols[col] = self.column_mapping[lower_col]
        return df.rename(columns=new_cols)

class DataValidator:
    def __init__(self):
        self.rules = {
            # CBC
            "Haemoglobin": {"min": 12.0, "max": 18.0, "critical_min": 6.0, "critical_max": 20.0, "unit": "g/dL"},
            "White Blood Cells": {"min": 5000, "max": 10000, "critical_min": 2000, "critical_max": 30000, "unit": "/cumm"},
            "RBC Count": {"min": 4.2, "max": 6.1, "unit": "mill/cumm"},
            "Platelets": {"min": 150000, "max": 400000, "critical_min": 40000, "critical_max": 999000, "unit": "/cumm"},
            "Packed Cell Volume": {"min": 37, "max": 52, "critical_min": 18, "critical_max": 60, "unit": "%"},
            "Mean Corpuscular Volume": {"min": 80, "max": 100, "unit": "fL"},
            "Mean Corpuscular Hemoglobin": {"min": 27, "max": 32, "unit": "pg"},
            "Mean Corpuscular Hemoglobin Concentration": {"min": 32, "max": 36, "unit": "g/dL"},
            "Red Cell Distribution Width": {"min": 11.5, "max": 14.5, "unit": "%"},
            "Erythrocyte Sedimentation Rate": {"min": 0, "max": 20, "unit": "mm/hr"},
            "Neutrophils": {"min": 40, "max": 75, "unit": "%"},
            "Lymphocytes": {"min": 20, "max": 45, "unit": "%"},
            "Monocytes": {"min": 2, "max": 10, "unit": "%"},
            "Eosinophils": {"min": 1, "max": 6, "unit": "%"},
            "Basophils": {"min": 0, "max": 1, "unit": "%"},
            
            # Diabetes
            "Glucose": {"min": 70, "max": 110, "critical_min": 40, "critical_max": 450, "unit": "mg/dL"},
            "HbA1c": {"min": 4.0, "max": 5.6, "unit": "%"},
            
            # Lipids
            "Total Cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
            "Triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
            "HDL Cholesterol": {"min": 40, "max": 60, "unit": "mg/dL"},
            "LDL Cholesterol": {"min": 0, "max": 100, "unit": "mg/dL"},
            
            # Kidney
            "Creatinine": {"min": 0.7, "max": 1.3, "critical_max": 4.0, "unit": "mg/dL"},
            "Urea": {"min": 10, "max": 20, "critical_max": 80, "unit": "mg/dL"},
            "Uric Acid": {"min": 3.5, "max": 7.2, "unit": "mg/dL"},
            
            # Liver
            "Total Bilirubin": {"min": 0.1, "max": 1.2, "unit": "mg/dL"},
            "AST (SGOT)": {"min": 12, "max": 31, "unit": "U/L"},
            "ALT (SGPT)": {"min": 7, "max": 40, "unit": "U/L"},
            "Alkaline Phosphatase": {"min": 44, "max": 147, "unit": "U/L"},
            "Albumin": {"min": 3.5, "max": 5.0, "unit": "g/dL"},
            "Total Protein": {"min": 6.4, "max": 8.3, "unit": "g/dL"},
            
            # Thyroid
            "TSH": {"min": 0.4, "max": 4.0, "unit": "mIU/L"},
            "Total T3": {"min": 80, "max": 200, "unit": "ng/dL"},
            "Total T4": {"min": 5.0, "max": 12.0, "unit": "ug/dL"},

            # Electrolytes
            "Sodium": {"min": 136, "max": 145, "critical_min": 120, "critical_max": 160, "unit": "mmol/L"},
            "Potassium": {"min": 3.5, "max": 5.0, "critical_min": 2.8, "critical_max": 6.2, "unit": "mmol/L"},
            "Chloride": {"min": 98, "max": 106, "critical_min": 80, "critical_max": 115, "unit": "mEq/L"},
            "Calcium": {"min": 9.0, "max": 10.5, "critical_min": 6.0, "critical_max": 13.0, "unit": "mg/dL"},

            # Coagulation
            "PT": {"min": 11.0, "max": 12.5, "critical_max": 80.0, "unit": "sec"},
            "PTT": {"min": 60.0, "max": 70.0, "critical_max": 70.0, "unit": "sec"},
            "INR": {"min": 0.9, "max": 1.2, "critical_max": 6.0, "unit": ""}
        }

class CommonInterpreter:
    def read_file(self, file_path, file_obj=None):
        # Support passing file object directly (for Streamlit)
        if file_obj is not None:
             if file_path.lower().endswith('.json'): return self.read_json(file_obj)
            # For Streams (like Streamlit uploads), we rely on physical paths 
            # for PDF/Image processing to ensure library stability (pdfplumber/Tesseract).
            
        if file_path.lower().endswith('.csv'): return pd.read_csv(file_path if file_obj is None else file_obj)
        elif file_path.lower().endswith('.pdf'): return self.read_pdf(file_path if file_obj is None else file_obj)
        elif file_path.lower().endswith(('.jpg', '.png', '.jpeg')): return self.read_image(file_path)
        elif file_path.lower().endswith('.json'): return self.read_json(file_path if file_obj is None else file_obj)
        return pd.DataFrame()

    def read_pdf(self, file_path_or_obj):
        all_data = []
        try:
            with pdfplumber.open(file_path_or_obj) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        parsed = self.parse_text_to_data(text)
                        if parsed: all_data.append(pd.DataFrame([parsed]))
            return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return pd.DataFrame()

    def read_image(self, file_path):
        try:
            img = Image.open(file_path).convert('L')
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img = img.point(lambda x: 255 if x > 200 else 0, mode='1')
            
            # Default OCR
            text = pytesseract.image_to_string(img)
            parsed = self.parse_text_to_data(text)
            
            # Retry with PSM 6 (Single block of text) if parsing failed
            if not parsed:
                text = pytesseract.image_to_string(img, config='--psm 6')
                parsed = self.parse_text_to_data(text)
                
            return pd.DataFrame([parsed]) if parsed else pd.DataFrame()
        except: return pd.DataFrame()

    def read_json(self, file_path_or_obj):
        """Reads a JSON file and converts it to a DataFrame."""
        try:
            if isinstance(file_path_or_obj, str):
                with open(file_path_or_obj, 'r') as f:
                    data = json.load(f)
            else:
                data = json.load(file_path_or_obj)
            
            # Expecting JSON in a format like {"Haemoglobin": 13.5, ...} or [{"Haemoglobin": 13.5}, ...]
            if isinstance(data, dict):
                return pd.DataFrame([data])
            elif isinstance(data, list):
                # Check for "Gender" as 0/1 and "Age" in keys to ensure we map them correctly later if needed
                # The Preprocessor handles column names, but Context needs explicit extraction from ROW if it's a dataset
                # The generic logic later takes "Age" and "Gender" from the context extractor which works on TEXT.
                # If we have structured data, we should probably set context from the first row if it exists.
                return pd.DataFrame(data)
            return pd.DataFrame()

        except Exception as e:
            print(f"Error reading JSON: {e}")
            return pd.DataFrame()

    def parse_text_to_data(self, text):
        """
        Extracts specific biomarkers from raw text using regex patterns.
        
        The patterns are designed to be robust against common OCR errors:
        - Case-insensitivity ((?i))
        - Flexible separators between name and value ([: . -])
        - Handling of noisy characters in value fields
        """
        data = {}
        # Structure: { Parameter Name: [List of Regex Patterns] }
        patterns = {
            # --- CBC PANEL ---
            # Exclude HbA1c matches when looking for Haemoglobin
            "Haemoglobin": [r"(?i)(?:Haemoglobin|Hemoglobin|Hbg|Hb(?![\s\-\.]*A[1I]c))[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            "White Blood Cells": [r"(?i)(?:WBC|White\s+Blood\s+Cells?|Total\s+Leucocyte\s+Count|TLC)[\s\:\.\-\(a-zA-Z]*?(\d{1,5}(?:[\.,]\d+)?)"],
            "RBC Count": [r"(?i)(?:RBC|Red\s+Blood\s+Cells?|Erythrocytes)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            "Platelets": [r"(?i)(?:Platelets?|PLT|Thrombocytes)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}(?:[\.,]\d+)?)"],
            "Packed Cell Volume": [r"(?i)(?:PCV|HCT|Hematocrit)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            "Mean Corpuscular Volume": [r"(?i)(?:MCV\b)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "Mean Corpuscular Hemoglobin": [r"(?i)(?:MCH\b)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "Mean Corpuscular Hemoglobin Concentration": [r"(?i)(?:MCHC)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            "Red Cell Distribution Width": [r"(?i)(?:RDW)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            "Erythrocyte Sedimentation Rate": [r"(?i)(?:ESR)[\s\:\.\-\(a-zA-Z]*?(\d{1,3})"],
            
            # --- DIFFERENTIAL COUNT ---
            "Neutrophils": [r"(?i)(?:Neutrophils?|NEU|Polymorphs|Poly|Neuts)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "Lymphocytes": [r"(?i)(?:Lymphocytes?|LYM|Lymphs)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "Monocytes": [r"(?i)(?:Monocytes?|MON|Monos)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "Eosinophils": [r"(?i)(?:Eosinophils?|EOS|Eos)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "Basophils": [r"(?i)(?:Basophils?|BAS|Basos)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            
            # --- METABOLIC / DIABETES ---
            "Glucose": [r"(?i)(?:Glucose|FBS|RBS|Blood\s+Sugar)[\s\:\.\-\(a-zA-Z]*?(\d{2,3}\.?\d*)"],
            "HbA1c": [r"(?i)(?:HbA[1I]c|Glycated\s+Hemoglobin|Glycosylated)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            
            # --- LIPID PROFILE ---
            "Total Cholesterol": [r"(?i)(?:Total\s+Cholesterol|Cholesterol)[\s\:\.\-\(a-zA-Z]*?(\d{2,3}\.?\d*)"],
            "Triglycerides": [r"(?i)(?:Triglycerides?|TGL)[\s\:\.\-\(a-zA-Z]*?(\d{2,3}\.?\d*)"],
            "HDL Cholesterol": [r"(?i)(?:HDL|High\s+Density\s+Lipoprotein)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "LDL Cholesterol": [r"(?i)(?:LDL|Low\s+Density\s+Lipoprotein)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            
            # --- RENAL (KIDNEY) PROFILE ---
            "Creatinine": [r"(?i)(?:Creatinine|S\.Creatinine)[\s\:\.\-\(a-zA-Z]*?(\d{0,2}\.?\d*)"],
            "Urea": [r"(?i)(?:Urea|Blood\s+Urea|BUN)[\s\:\.\-\(a-zA-Z]*?(\d{2,3}\.?\d*)"],
            "Uric Acid": [r"(?i)(?:Uric\s+Acid)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],

            # --- LIVER FUNCTION ---
            "Total Bilirubin": [r"(?i)(?:Total\s+Bilirubin|Bilirubin\s+Total)[\s\:\.\-\(a-zA-Z]*?(\d{0,2}\.?\d*)"],
            "AST (SGOT)": [r"(?i)(?:AST|SGOT|Aspartate\s+Aminotransferase)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "ALT (SGPT)": [r"(?i)(?:ALT|SGPT|Alanine\s+Aminotransferase)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "Albumin": [r"(?i)(?:Albumin|Serum\s+Albumin)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            "Total Protein": [r"(?i)(?:Total\s+Protein|Protein)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            
            # --- THYROID ---
            "TSH": [r"(?i)(?:TSH|Thyroid\s+Stimulating\s+Hormone)[\s\:\.\-\(a-zA-Z]*?(\d{0,2}\.?\d*)"],

            # --- ELECTROLYTES ---
            "Sodium": [r"(?i)(?:Sodium|\bNa\b|\bNa\+)[\s\:\.\-\(a-zA-Z]*?(\d{2,3}\.?\d*)"],
            "Potassium": [r"(?i)(?:Potassium|\bK\b|\bK\+)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],
            "Chloride": [r"(?i)(?:Chloride|\bCl\b|\bCl\-)[\s\:\.\-\(a-zA-Z]*?(\d{2,3}\.?\d*)"],
            "Calcium": [r"(?i)(?:Calcium|\bCa\b|\bCa\+\+?)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"],

            # --- COAGULATION ---
            "PT": [r"(?i)(?:Prothrombin\s+Time|\bPT\b)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "PTT": [r"(?i)(?:Partial\s+Thromboplastin\s+Time|\bPTT\b|\bAPTT\b)[\s\:\.\-\(a-zA-Z]*?(\d{1,3}\.?\d*)"],
            "INR": [r"(?i)(?:\bINR\b)[\s\:\.\-\(a-zA-Z]*?(\d{1,2}\.?\d*)"]
        }
        
        for param, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, text)
                if match:
                    try: 
                        val_str = match.group(1).replace(',', '')
                        # Correct common OCR error where decimals might be doubled (e.g., 14..5)
                        if val_str.count('.') > 1:
                             val_str = val_str.replace('.', '', 1) 
                        val = float(val_str)
                        
                        # Unit normalization heuristics for different formats
                        if param == "Platelets":
                            if val < 15: # e.g., 1.75 means Lakhs
                                val = val * 100000
                            elif val < 1000: # e.g., 150 means thousands
                                val = val * 1000
                        elif param == "White Blood Cells":
                            if val < 100: # e.g., 4.5 means thousands
                                val = val * 1000
                        
                        data[param] = val
                    except: continue
        return data

    def extract_text_from_pdf(self, file_path_or_obj):
        text_content = ""
        try:
            with pdfplumber.open(file_path_or_obj) as pdf:
                for page in pdf.pages:
                    text_content += (page.extract_text() or "") + "\n"
        except: pass
        return text_content

    def extract_text_from_image(self, file_path):
        try:
            img = Image.open(file_path).convert('L')
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img = img.point(lambda x: 255 if x > 200 else 0, mode='1')
            return pytesseract.image_to_string(img)
        except: return ""


# 2. INTELLIGENCE MODELS (M3 Scope)

class PatientContextExtractor:
    """
    Extracts patient demographic information (Age, Gender) from the header text of medical reports.
    """
    def extract(self, text):
        context = {'age': None, 'gender': None}
        if not text: return context

        # Primary extraction strategy: Search for specific "Age" labels
        # Matches formats like: "Age: 20", "Age/Gender: 20", "AgeGender: 20"
        # Uses \D to flexibly skip delimiters like colons, spaces, or OCR noise.
        age_match = re.search(r"(?i)(?:Age|Yrs?)(?:[\s\/]*Gender)?\D{0,15}(\d{1,3})", text)
        
        # Secondary extraction strategy: Search for raw values with units
        # Matches formats like: "20 Years", "20 yrs", "20y"
        if not age_match:
             age_match = re.search(r"(?i)(\d+)\s*y[a-z]*", text)
        
        if age_match: context['age'] = int(age_match.group(1))

        # Gender extracted via keyword search in header text
        if re.search(r"(?i)\b(?:Female|Woman|Mrs\.|Ms\.)\b", text): context['gender'] = "Female"
        elif re.search(r"(?i)\b(?:Male|Man|Mr\.)\b", text): context['gender'] = "Male"
        elif re.search(r"(?i)(?:Sex|Gender)[\s\:\-\/]+F\b", text): context['gender'] = "Female"
        elif re.search(r"(?i)(?:Sex|Gender)[\s\:\-\/]+M\b", text): context['gender'] = "Male"
        elif re.search(r"(?i)\/F\b", text): context['gender'] = "Female"
        
        return context

class ContextualAnalysisModel:
    def adjust_rules(self, base_rules, age, gender):
        adj_rules = {k: v.copy() for k, v in base_rules.items()}
        
        # Only adjust if gender is known
        if gender:
            if 'Haemoglobin' in adj_rules:
                if gender.lower().startswith('f'):
                    adj_rules['Haemoglobin'].update({'min': 12.0, 'max': 15.5})
                elif gender.lower().startswith('m'):
                    adj_rules['Haemoglobin'].update({'min': 13.5, 'max': 17.5})
        
        # Only adjust if age is known
        if age and 'Glucose' in adj_rules and age > 60:
            adj_rules['Glucose']['max'] = 140
            
        return adj_rules

class BiomarkerCorrelationEngine:
    def __init__(self, kb_path="knowledge_base.json"):
        self.kb_path = kb_path
        self.patterns = self.load_patterns()

    def load_patterns(self):
        try:
            with open(self.kb_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def analyze(self, biomarkers, active_rules):
        # Reload to ensure freshness
        self.patterns = self.load_patterns()
        found = []
        
        for name, data in self.patterns.items():
            rules = data.get('rules', [])
            is_match = True
            evidence = []
            
            if not rules: continue

            for rule in rules:
                param = rule['param']
                op = rule['op']
                threshold = rule['val']
                
                # Check if we have the data
                if param not in biomarkers:
                    is_match = False
                    break
                
                val = biomarkers[param]
                
                # Evaluate Condition
                if op == ">" and not (val > threshold): is_match = False
                elif op == "<" and not (val < threshold): is_match = False
                elif op == ">=" and not (val >= threshold): is_match = False
                elif op == "<=" and not (val <= threshold): is_match = False
                elif op == "==" and not (val == threshold): is_match = False
                
                if not is_match: break
                evidence.append(param)
            
            if is_match:
                found.append({
                    "Pattern": name,
                    "Significance": data.get('significance', "Condition detected based on rules."),
                    "Evidence": evidence
                })
                
        return found

class RecommendationGenerator:
    def __init__(self, kb_path="knowledge_base.json"):
        self.kb_path = kb_path
        self.kb = self.load_kb()

    def load_kb(self):
        try:
            with open(self.kb_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def generate_report(self, risks, context, detailed_biomarkers=None):
        self.kb = self.load_kb()
        advice = []
        
        has_abnormal = False
        if detailed_biomarkers:
            for item in detailed_biomarkers:
                if "Normal" not in item['Status']:
                    has_abnormal = True
                    break

        if not risks and not has_abnormal:
            advice.append("✅ **HEALTHY STATUS**: No complex risk patterns or abnormal biomarkers detected based on the analyzed markers.")

        advice.append("### 🩺 Personalized Health Recommendations")
        advice.append("\n**General Wellness Advice:**")
        advice.append("- 🥗 Maintain a balanced diet rich in fruits and vegetables.")
        advice.append("- 💧 Stay hydrated and exercise regularly.")
        advice.append("- 😴 Ensure 7-8 hours of quality sleep.")
        
        if risks:
            for r in risks:
                name = r['Pattern']
                item = self.kb.get(name)
                
                if item:
                    adv = item.get('advice', {})
                    diet = adv.get('Diet', 'Consult Doctor')
                    lifestyle = adv.get('Lifestyle', 'Consult Doctor')
                else:
                    diet = "Consult Doctor"
                    lifestyle = "Consult Doctor"

                # Contextual Tweaks
                # Age modifier
                if context.get('age') and context['age'] > 60 and "aerobic" in lifestyle.lower():
                    lifestyle += " (Low-impact recommended)"

                advice.append(f"\n**👉 {name.upper()}**")
                advice.append(f"- **Diet**: {diet}")
                advice.append(f"- **Lifestyle**: {lifestyle}")

        # Individual Biomarker Adjustments
        if detailed_biomarkers and has_abnormal:
            advice.append("\n---\n")
            advice.append("### 🔬 Specific Biomarker Alerts")
            for item in detailed_biomarkers:
                status = item['Status']
                if "Normal" not in status:
                    param = item['Parameter']
                    if "LOW" in status:
                        if param in ["Haemoglobin", "RBC Count", "Packed Cell Volume"]:
                            advice.append(f"- **{param} Low**: Increase intake of iron-rich foods (lean meats, leafy greens) and Vitamin C.")
                        elif param in ["White Blood Cells", "Neutrophils"]:
                            advice.append(f"- **{param} Low**: Indicates potentially weakened immunity. Focus on hygiene, rest, and foods rich in Vitamin C and Zinc.")
                        elif param == "Platelets":
                            advice.append(f"- **{param} Low**: Increased bleeding risk. Avoid activities that might cause injury and consult a doctor.")
                        elif param == "Glucose":
                            advice.append(f"- **{param} Low**: Eat regular balanced meals. Carry a fast-acting carbohydrate if prone to hypoglycemia.")
                        elif param in ["Sodium", "Potassium", "Chloride", "Calcium"]:
                            advice.append(f"- **{param} Low**: Electrolyte imbalance. Ensure proper hydration and consult a doctor regarding dietary adjustments.")
                        else:
                            advice.append(f"- **{param} Low**: Please consult a physician for tailored advice.")
                    elif "HIGH" in status:
                        if param in ["Glucose", "HbA1c"]:
                            advice.append(f"- **{param} High**: Focus on low-carb, high-fiber foods and engage in physical activity after meals.")
                        elif param in ["Total Cholesterol", "LDL Cholesterol", "Triglycerides"]:
                            advice.append(f"- **{param} High**: Reduce saturated fats, eliminate trans fats, and increase cardiovascular exercise.")
                        elif param in ["White Blood Cells", "Neutrophils"]:
                            advice.append(f"- **{param} High**: May indicate infection or inflammation. Rest and stay hydrated.")
                        elif param in ["Creatinine", "Urea", "Uric Acid"]:
                            advice.append(f"- **{param} High**: Elevated kidney marker. Ensure adequate hydration and monitor protein intake carefully based on doctor's advice.")
                        elif param in ["AST (SGOT)", "ALT (SGPT)", "Alkaline Phosphatase", "Total Bilirubin", "Albumin", "Total Protein"]:
                            advice.append(f"- **{param} High**: Elevated liver/protein marker. Avoid alcohol completely and limit processed foods.")
                        elif param in ["Sodium", "Potassium", "Chloride", "Calcium"]:
                            advice.append(f"- **{param} High**: Electrolyte imbalance. Ensure proper hydration and consult a doctor regarding dietary adjustments.")
                        else:
                            advice.append(f"- **{param} High**: Please consult a physician for tailored advice.")

        self._append_prev_conditions(advice, context)
        return "\n".join(advice)

    def _append_prev_conditions(self, advice, context):
        # Add logic for Previous Conditions Warning
        prev_conds = context.get('prev_conditions', [])
        if prev_conds:
            advice.append("\n---\n")
            advice.append("### ⚠️ Chronic Condition Considerations")
            for pc in prev_conds:
                if pc == "Diabetes":
                    advice.append("- **Diabetes Alert**: Please ensure you measure your fasting blood sugar daily and adhere to a strict low-glycemic diabetic protocol.")
                elif pc == "Anemia":
                    advice.append("- **Anemia Alert**: Continue taking prescribed iron or B12 supplements and eat iron-rich foods.")
                elif pc == "Hypertension":
                    advice.append("- **Hypertension Alert**: Strictly limit dietary sodium to under 1500mg daily to manage your blood pressure.")
                elif pc == "Heart Disease":
                    advice.append("- **Heart Disease Alert**: Monitor any chest discomfort. Keep total fat and saturated fats extremely low.")
                elif pc == "Kidney Disease":
                    advice.append("- **Kidney Disease Alert**: Carefully monitor your protein and potassium intake as instructed by your nephrologist.")
                elif pc == "Liver Disease":
                    advice.append("- **Liver Disease Alert**: Avoid alcohol entirely, minimize sodium, and report any jaundice or swelling.")
                elif pc == "Thyroid Disorder":
                    advice.append("- **Thyroid Alert**: Ensure consistent iodine intake and take any thyroid medications precisely as prescribed.")
                elif pc == "Obesity":
                    advice.append("- **Obesity Alert**: Focus on a sustained, healthy caloric deficit and joint-friendly cardiovascular exercises.")
                elif pc == "Gout":
                    advice.append("- **Gout Alert**: Avoid purine-rich foods like red meat and alcohol to prevent painful flare-ups.")
                elif pc == "Autoimmune Disease":
                    advice.append("- **Autoimmune Alert**: Focus on an anti-inflammatory diet and report any new flare-up symptoms to your rheumatologist.")
                elif pc == "Bleeding Disorder":
                    advice.append("- **Bleeding Disorder Alert**: Monitor platelet levels carefully and avoid contact sports or activities with injury risk.")
                else:
                    advice.append(f"- **{pc} Alert**: Please continue following your doctor's protocols for {pc}.")

class DiagnosticLearner:
    def __init__(self, kb_path="knowledge_base.json"):
        self.kb_path = kb_path

    def learn_from_report(self, text, current_kb):
        """
        Parses free-text conclusion/diagnosis sections to identify new potential conditions.
        If a new condition is found, it is added to the Knowledge Base for future reference.
        """
        if not text: return current_kb
        
        # Identify lines starting with "Diagnosis:", "Impression:", etc.
        matches = re.finditer(r"(?i)(?:Diagnosis|Impression|Conclusion|Summary)\s*[:\-]\s*(.*)", text)
        
        updates = 0
        for match in matches:
            diagnosis = match.group(1).strip()
            # Sanitize: Remove punctuation and overly long strings
            diagnosis = re.split(r'[.;]', diagnosis)[0].strip()
            
            # Validation: Ignore too short/long strings or generic terms
            if len(diagnosis) < 3 or len(diagnosis) > 50: continue
            if diagnosis.lower() in ["normal", "nil", "correlated", "within normal limits"]: continue
            
            # Check for existence in KB (Case-insensitive)
            exists = False
            for key in current_kb.keys():
                if key.lower() == diagnosis.lower() or diagnosis.lower() in key.lower():
                    exists = True
                    break
            
            if not exists:
                # Add new finding to KB with a "Learned" flag
                print(f"[LEARNING] New diagnosis: {diagnosis}")
                current_kb[diagnosis] = {
                    "rules": [], # Automated rule extraction is disabled for safety
                    "advice": {
                        "Diet": f"Condition '{diagnosis}' detected from report. Consult specific dietary guidelines.",
                        "Lifestyle": "Follow medical advice provided in the report."
                    },
                    "significance": f"Automatically learned from report: {diagnosis}"
                }
                updates += 1
        
        if updates > 0:
            self.save_kb(current_kb)
            
        return current_kb

    def save_kb(self, kb_data):
        try:
            with open(self.kb_path, 'w') as f:
                json.dump(kb_data, f, indent=4)
        except Exception as e:
            print(f"Error saving KB: {e}")



class HealthAgent:
    def __init__(self):
        self.context_extractor = PatientContextExtractor()
        self.context_model = ContextualAnalysisModel()
        self.risk_engine = BiomarkerCorrelationEngine()
        self.recommender = RecommendationGenerator()
        self.validator = DataValidator()
        self.learner = DiagnosticLearner() # Initialize Learner
        self.base_rules = self.validator.rules
        self.interpreter = CommonInterpreter()
        self.preprocessor = Preprocessor()

    def process_data(self, df, raw_text="", prev_conditions=None):
        # Extract context (Age/Gender) from raw text if available
        context = self.context_extractor.extract(raw_text)
        context['prev_conditions'] = prev_conditions or []
        
        # If context is missing from text, try to get it from the DataFrame columns if they exist
        # This handles the CSV/JSON dataset case where Age/Gender are columns
        if (context['age'] is None or context['gender'] is None) and not df.empty:
             # Look for Age
             for col in df.columns:
                 if col.lower() == 'age':
                     vals = pd.to_numeric(df[col], errors='coerce').dropna()
                     if not vals.empty: context['age'] = int(vals.iloc[0])
                     break
             
             # Look for Gender
             for col in df.columns:
                 if col.lower() == 'gender':
                     val = df[col].iloc[0]
                     # Handle 0/1 encoding often found in datasets (0=F, 1=M or vice versa, typically 1=M)
                     # Assuming 1=Male, 0=Female for common datasets, or checking string
                     if str(val) == '1': context['gender'] = 'Male'
                     elif str(val) == '0': context['gender'] = 'Female'
                     elif str(val).lower().startswith('m'): context['gender'] = 'Male'
                     elif str(val).lower().startswith('f'): context['gender'] = 'Female'
                     break

        # Normalize columns for datasets
        df = self.preprocessor.normalize_column_names(df)

        # 1. AUTO-LEARNING STEP
        if raw_text:
            # Sync the Knowledge Base before learning step
            current_kb = self.risk_engine.load_patterns()
            updated_kb = self.learner.learn_from_report(raw_text, current_kb)
            
        active_rules = self.context_model.adjust_rules(self.base_rules, context['age'], context['gender'])

        biomarkers = {}
        if not df.empty:
             for col in df.columns:
                 if col in active_rules:
                      vals = pd.to_numeric(df[col], errors='coerce').dropna()
                      if not vals.empty:
                          val = float(vals.iloc[0])
                          biomarkers[col] = val

        # Logic for status
        detailed_biomarkers = []
        for k, v in biomarkers.items():
            rule = active_rules[k]
            status = "Normal"
            if 'critical_min' in rule and v <= rule['critical_min']:
                status = f"CRITICAL LOW (<={rule['critical_min']})"
            elif 'critical_max' in rule and v >= rule['critical_max']:
                status = f"CRITICAL HIGH (>={rule['critical_max']})"
            elif v < rule['min']: 
                status = f"LOW (<{rule['min']})"
            elif v > rule['max']: 
                status = f"HIGH (>{rule['max']})"
            
            detailed_biomarkers.append({
                "Parameter": k,
                "Value": v,
                "Unit": rule['unit'],
                "Reference Range": f"{rule['min']} - {rule['max']}",
                "Status": status
            })

        risks = self.risk_engine.analyze(biomarkers, active_rules)
        advice_text = self.recommender.generate_report(risks, context, detailed_biomarkers)

        return {
            "patient": context,
            "biomarkers": biomarkers,
            "detailed_biomarkers": detailed_biomarkers,
            "risks": risks,
            "advice": advice_text
        }
