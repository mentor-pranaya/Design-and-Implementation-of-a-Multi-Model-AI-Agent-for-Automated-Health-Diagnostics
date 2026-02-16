from src.extraction.parameter_extractor import extract_parameters_from_text
from src.data_cleaning.data_cleaner import clean_and_structure_data
from src.validation.standardizer import standardize_units
from src.validation.data_validator import validate_parameters
from src.analysis.model_1 import analyze_report

def test_pipeline():
    print("--- Testing Full Pipeline (Milestone 1) ---")
    
    # Simulating extracted text including some variation in units and potentially invalid values
    text_input = """
    Hemoglobin 13.5 gdl
    WBC 6500
    Platelets 250000
    Glucose 105 mg/dl
    Cholesterol 200 mgdl
    Creatinine 1.1
    Sodium 140 mmol/L
    TestInvalid -5
    """
    
    print(f"Input Text:\n{text_input}\n")
    
    # 1. Extraction
    extracted = extract_parameters_from_text(text_input)
    print(f"1. Extracted:\n{extracted}\n")
    
    # 2. Cleaning
    cleaned = clean_and_structure_data(extracted)
    print(f"2. Cleaned:\n{cleaned}\n")
    
    # 3. Standardization
    standardized = standardize_units(cleaned)
    print(f"3. Standardized:\n{standardized}\n")
    
    # 4. Validation
    validated, issues = validate_parameters(standardized)
    print(f"4. Validated:\n{validated}\n")
    print(f"Issues Found:\n{issues}\n")
    
    # 5. Model 1 Analysis
    analysis = analyze_report(validated)
    print(f"5. Analysis (Model 1):\n{analysis}\n")

if __name__ == "__main__":
    test_pipeline()
