# Add project root to path
import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.extraction.parameter_extractor import extract_parameters_from_text

def test_extraction():
    test_cases = [
        # Standard format
        "Hemoglobin: 13.5 g/dL",
        # No colon
        "Hemoglobin 13.5",
        # Different casing
        "hemoglobin: 13.5",
        # With other text
        "Patient has Hemoglobin level of 13.5.",
        # Common variations (need to check schema first)
        "Hgb: 13.5",
        "Hb: 13.5",
        # Full report simulation
        """
        BLOOD REPORT
        Patient: John Doe
        Date: 2024-01-01
        
        COMPLETE BLOOD COUNT
        Hemoglobin          14.2 g/dL
        RBC                 4.8  mill/mm3
        WBC                 7500 /mm3
        Platelets           250000 /mm3
        
        LIPID PROFILE
        Total Cholesterol   185 mg/dL
        HDL Cholesterol     45  mg/dL
        LDL Cholesterol     110 mg/dL
        Triglycerides       150 mg/dL
        """,
        # Edge case: embedded in sentences
        "Glucose is 95 and cholesterol is 180"
    ]
    
    print("Testing Parameter Extraction Logic")
    print("==================================")
    
    for i, text in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Input: {text[:50]}..." if len(text) > 50 else f"Input: {text}")
        
        try:
            params = extract_parameters_from_text(text)
            print(f"Extracted: {params}")
            if not params:
                print("FAILED to extract any parameters")
            else:
                print(f"Success ({len(params)} params)")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_extraction()
