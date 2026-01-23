import streamlit as st
import pytesseract
import pdfplumber
import json
import re
from PIL import Image
import io

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Standard reference ranges for blood parameters (example values, adjust as needed)
HEALTH_REFERENCE_RANGES = {
    'hemoglobin': {'female': (12.0, 16.0), 'male': (13.5, 17.5), 'unit': 'g/dL'},
    'glucose': (70, 100, 'mg/dL'),
    'cholesterol': (0, 200, 'mg/dL'),
    'triglycerides': (0, 150, 'mg/dL'),
    'hdl': (40, 60, 'mg/dL'),  # for females
    'ldl': (0, 100, 'mg/dL'),
    'creatinine': {'female': (0.6, 1.1), 'male': (0.7, 1.2), 'unit': 'mg/dL'},
    'bun': (7, 20, 'mg/dL'),
    'sodium': (135, 145, 'mEq/L'),
    'potassium': (3.5, 5.0, 'mEq/L'),
}

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_image(file):
    img = Image.open(file)
    text = pytesseract.image_to_string(img)
    return text

def extract_blood_parameters(text):
    extracted_parameters = {}
    # Regex patterns for common blood test parameters
    BLOOD_TEST_PATTERNS = {
        'hemoglobin': r'hemoglobin[:\s]*(\d+\.?\d*)\s*(g/dL|g/L)',
        'glucose': r'glucose[:\s]*(\d+\.?\d*)\s*(mg/dL|mmol/L)',
        'cholesterol': r'cholesterol[:\s]*(\d+\.?\d*)\s*(mg/dL|mmol/L)',
        'triglycerides': r'triglycerides[:\s]*(\d+\.?\d*)\s*(mg/dL|mmol/L)',
        'hdl': r'hdl[:\s]*(\d+\.?\d*)\s*(mg/dL|mmol/L)',
        'ldl': r'ldl[:\s]*(\d+\.?\d*)\s*(mg/dL|mmol/L)',
        'creatinine': r'creatinine[:\s]*(\d+\.?\d*)\s*(mg/dL|µmol/L)',
        'bun': r'bun[:\s]*(\d+\.?\d*)\s*(mg/dL|mmol/L)',
        'sodium': r'sodium[:\s]*(\d+\.?\d*)\s*(mEq/L|mmol/L)',
        'potassium': r'potassium[:\s]*(\d+\.?\d*)\s*(mEq/L|mmol/L)',
    }
    
    for param, pattern in BLOOD_TEST_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = match.group(2) if len(match.groups()) > 1 else ''
            extracted_parameters[param] = {'value': value, 'unit': unit}
    
    return extracted_parameters

def normalize_measurement_units(extracted_parameters):
    # Simple unit conversions (add more as needed)
    UNIT_CONVERSIONS = {
        'glucose': {'mmol/L': lambda x: x * 18, 'mg/dL': lambda x: x},
        'cholesterol': {'mmol/L': lambda x: x * 38.67, 'mg/dL': lambda x: x},
    }
    
    for param, data in extracted_parameters.items():
        if param in UNIT_CONVERSIONS and data['unit'] in UNIT_CONVERSIONS[param]:
            data['value'] = UNIT_CONVERSIONS[param][data['unit']](data['value'])
            data['unit'] = 'mg/dL'  # standardize to mg/dL
    
    return extracted_parameters

def classify_parameter_status(param, value, gender='female'):
    if param not in HEALTH_REFERENCE_RANGES:
        return 'Unknown'
    
    ref = HEALTH_REFERENCE_RANGES[param]
    if isinstance(ref, dict):
        low, high = ref[gender]
    else:
        low, high = ref[0], ref[1]
    
    if value < low:
        return 'Low'
    elif value > high:
        return 'High'
    else:
        return 'Normal'

def main():
    st.title("Blood Parameter Analysis System")
    
    st.header("Input Interface & Parser")
    uploaded_file = st.file_uploader("Upload a file (PDF, Image, or JSON)", type=['pdf', 'png', 'jpg', 'jpeg', 'json'])
    
    if uploaded_file is not None:
        file_type = uploaded_file.type
        
        st.header("Data Extraction Engine")
        if file_type == 'application/pdf':
            text = extract_text_from_pdf(uploaded_file)
            st.subheader("Extracted Text from PDF:")
        elif file_type.startswith('image/'):
            text = extract_text_from_image(uploaded_file)
            st.subheader("Extracted Text from Image:")
            st.image(uploaded_file, caption='Uploaded Image')
        elif file_type == 'application/json':
            data = json.load(uploaded_file)
            text = json.dumps(data)  # For parsing, treat as text
            st.subheader("JSON Data:")
            st.json(data)
        else:
            st.error("Unsupported file type")
            return
        
        st.text_area("Raw Text", text, height=200)
        
        st.header("Data Validation & Standardization Module")
        extracted_parameters = extract_blood_parameters(text)
        if extracted_parameters:
            st.subheader("Extracted Parameters:")
            st.json(extracted_parameters)
            
            standardized_parameters = normalize_measurement_units(extracted_parameters)
            st.subheader("Standardized Parameters:")
            st.json(standardized_parameters)
            
            st.header("Model 1: Parameter Interpretation")
            gender = st.selectbox("Select Gender", ['female', 'male'])
            
            parameter_classifications = {}
            for param, data in standardized_parameters.items():
                classification = classify_parameter_status(param, data['value'], gender)
                parameter_classifications[param] = {
                    'value': data['value'],
                    'unit': data['unit'],
                    'classification': classification
                }
            
            st.subheader("Classifications:")
            st.json(parameter_classifications)
            
            # Display in a table
            st.table(pd.DataFrame.from_dict(parameter_classifications, orient='index'))
        else:
            st.warning("No blood parameters detected in the text.")

if __name__ == "__main__":
    import pandas as pd
    main()