"""
Dataset Generator for Blood Reports
Creates synthetic blood test data in JSON and CSV formats
"""

import json
import random
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

class BloodReportGenerator:
    """Generate synthetic blood reports for testing"""
    
    # Standard reference ranges for common blood parameters
    REFERENCE_RANGES = {
        'Hemoglobin': {'unit': 'g/dL', 'min': 13.0, 'max': 17.0, 'male': (13.5, 17.5), 'female': (12.0, 15.5)},
        'WBC': {'unit': '10^3/μL', 'min': 4.0, 'max': 11.0, 'male': (4.0, 11.0), 'female': (4.0, 11.0)},
        'RBC': {'unit': '10^6/μL', 'min': 4.5, 'max': 5.9, 'male': (4.7, 6.1), 'female': (4.2, 5.4)},
        'Platelets': {'unit': '10^3/μL', 'min': 150, 'max': 400, 'male': (150, 400), 'female': (150, 400)},
        'Glucose': {'unit': 'mg/dL', 'min': 70, 'max': 100, 'male': (70, 100), 'female': (70, 100)},
        'Total_Cholesterol': {'unit': 'mg/dL', 'min': 0, 'max': 200, 'male': (0, 200), 'female': (0, 200)},
        'HDL': {'unit': 'mg/dL', 'min': 40, 'max': 999, 'male': (40, 999), 'female': (50, 999)},
        'LDL': {'unit': 'mg/dL', 'min': 0, 'max': 100, 'male': (0, 100), 'female': (0, 100)},
        'Triglycerides': {'unit': 'mg/dL', 'min': 0, 'max': 150, 'male': (0, 150), 'female': (0, 150)},
        'Creatinine': {'unit': 'mg/dL', 'min': 0.7, 'max': 1.3, 'male': (0.7, 1.3), 'female': (0.6, 1.1)},
        'BUN': {'unit': 'mg/dL', 'min': 7, 'max': 20, 'male': (7, 20), 'female': (7, 20)},
        'ALT': {'unit': 'U/L', 'min': 7, 'max': 56, 'male': (7, 56), 'female': (7, 56)},
        'AST': {'unit': 'U/L', 'min': 10, 'max': 40, 'male': (10, 40), 'female': (10, 40)},
        'TSH': {'unit': 'mIU/L', 'min': 0.4, 'max': 4.0, 'male': (0.4, 4.0), 'female': (0.4, 4.0)},
        'HbA1c': {'unit': '%', 'min': 4.0, 'max': 5.6, 'male': (4.0, 5.6), 'female': (4.0, 5.6)}
    }
    
    def __init__(self, seed=42):
        random.seed(seed)
        
    def generate_value(self, param_name, gender='male', condition='normal'):
        """Generate a value for a parameter based on condition"""
        ref = self.REFERENCE_RANGES[param_name]
        min_val, max_val = ref[gender]
        
        if condition == 'normal':
            # 80% within normal range
            value = random.uniform(min_val + (max_val - min_val) * 0.2, 
                                 max_val - (max_val - min_val) * 0.2)
        elif condition == 'high':
            # Above normal range
            value = random.uniform(max_val * 1.05, max_val * 1.3)
        elif condition == 'low':
            # Below normal range
            value = random.uniform(min_val * 0.7, min_val * 0.95)
        elif condition == 'borderline_high':
            # Near upper limit
            value = random.uniform(max_val * 0.95, max_val * 1.05)
        elif condition == 'borderline_low':
            # Near lower limit
            value = random.uniform(min_val * 0.95, min_val * 1.05)
        else:
            value = random.uniform(min_val, max_val)
        
        # Round based on typical precision
        if ref['unit'] in ['g/dL', 'mg/dL', 'mIU/L', '%']:
            return round(value, 1)
        elif ref['unit'] in ['10^3/μL', '10^6/μL']:
            return round(value, 2)
        else:
            return round(value, 0)
    
    def generate_report(self, report_id, gender=None, profile='normal'):
        """Generate a complete blood report"""
        if gender is None:
            gender = random.choice(['male', 'female'])
        
        # Define profiles with typical abnormalities
        profiles = {
            'normal': {},
            'diabetic': {'Glucose': 'high', 'HbA1c': 'high'},
            'anemic': {'Hemoglobin': 'low', 'RBC': 'low'},
            'high_cholesterol': {'Total_Cholesterol': 'high', 'LDL': 'high', 'Triglycerides': 'high'},
            'kidney_concern': {'Creatinine': 'high', 'BUN': 'high'},
            'liver_concern': {'ALT': 'high', 'AST': 'high'},
            'mixed': {'Glucose': 'borderline_high', 'Total_Cholesterol': 'high', 'Hemoglobin': 'borderline_low'}
        }
        
        profile_conditions = profiles.get(profile, {})
        
        # Generate test date
        test_date = datetime.now() - timedelta(days=random.randint(1, 90))
        
        report = {
            'report_id': f'RPT{report_id:05d}',
            'patient_id': f'PAT{random.randint(10000, 99999)}',
            'test_date': test_date.strftime('%Y-%m-%d'),
            'lab_name': random.choice(['HealthLab Plus', 'MediTest Center', 'QuickDiagnostics', 'CityLab']),
            'gender': gender,
            'age': random.randint(25, 75),
            'parameters': []
        }
        
        # Generate all parameters
        for param_name, ref_data in self.REFERENCE_RANGES.items():
            condition = profile_conditions.get(param_name, 'normal')
            value = self.generate_value(param_name, gender, condition)
            
            param = {
                'name': param_name,
                'value': value,
                'unit': ref_data['unit'],
                'reference_min': ref_data[gender][0],
                'reference_max': ref_data[gender][1]
            }
            report['parameters'].append(param)
        
        return report
    
    def generate_dataset(self, num_reports=20, output_dir='data/raw'):
        """Generate a dataset of blood reports"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        profiles = ['normal', 'diabetic', 'anemic', 'high_cholesterol', 
                   'kidney_concern', 'liver_concern', 'mixed']
        
        reports = []
        for i in range(num_reports):
            # Mix of different profiles
            if i < 8:
                profile = 'normal'
            else:
                profile = random.choice(profiles)
            
            report = self.generate_report(i + 1, profile=profile)
            reports.append(report)
            
            # Save individual JSON files
            json_path = Path(output_dir) / f"report_{i+1:03d}.json"
            with open(json_path, 'w') as f:
                json.dump(report, f, indent=2)
        
        # Create summary CSV
        summary_data = []
        for report in reports:
            row = {
                'report_id': report['report_id'],
                'patient_id': report['patient_id'],
                'test_date': report['test_date'],
                'lab_name': report['lab_name'],
                'gender': report['gender'],
                'age': report['age']
            }
            # Add parameter values
            for param in report['parameters']:
                row[param['name']] = param['value']
            summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        csv_path = Path(output_dir) / 'reports_summary.csv'
        df.to_csv(csv_path, index=False)
        
        print(f"✓ Generated {num_reports} blood reports")
        print(f"✓ JSON files saved to: {output_dir}")
        print(f"✓ Summary CSV saved to: {csv_path}")
        
        return reports, df

if __name__ == '__main__':
    generator = BloodReportGenerator(seed=42)
    reports, df = generator.generate_dataset(num_reports=20)
    
    # Display sample
    print("\n" + "="*60)
    print("Sample Report Preview:")
    print("="*60)
    print(json.dumps(reports[0], indent=2))