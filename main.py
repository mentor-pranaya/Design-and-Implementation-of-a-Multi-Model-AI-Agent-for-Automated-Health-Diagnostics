from extractor import extract_text
from ocr_extractor import extract_text_with_ocr
from cleaner import extract_parameters
from model1 import interpret
from risk_model import assess_risk
from context_model import apply_context
from health_risk_explainer import explain_health_risks
import sys
import os

def process_report(pdf_path):
    """Process a single medical report and return results"""
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*60}\n")
    
    try:
        # Try standard PDF extraction first
        text = extract_text(pdf_path)
        if not text.strip():
            raise ValueError("Empty text")
        print("Using standard PDF extraction...")
    except:
        # Fall back to OCR for scanned documents
        print("Using OCR (scanned document)...")
        text = extract_text_with_ocr(pdf_path)

    parameters = extract_parameters(text)
    print("Extracted Parameters:", parameters)

    interpretation = interpret(parameters)
    print("Interpretation:", interpretation)

    risk = assess_risk(parameters)
    print("Risk Assessment:", risk)

    final_risk = apply_context(risk, age=50, gender="female")
    print("Contextual Risk:", final_risk)

    health_risks = explain_health_risks(parameters, final_risk)
    print("\nPotential Health Risks:")
    for r in health_risks:
        print("-", r)
    
    return {
        'file': os.path.basename(pdf_path),
        'parameters': parameters,
        'interpretation': interpretation,
        'risk': risk,
        'contextual_risk': final_risk,
        'health_risks': health_risks
    }

if __name__ == "__main__":
    # Allow command-line argument for PDF file, or use default
    if len(sys.argv) > 1:
        pdf_files = sys.argv[1:]
    else:
        # Default: process test report
        pdf_files = ["OCR_Test_Scanned_Report.pdf"]
    
    results = []
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            result = process_report(pdf_file)
            results.append(result)
        else:
            print(f"Error: File not found - {pdf_file}")

    print(f"\n{'='*60}")
    print(f"Processing Complete - {len(results)} report(s) processed")
    print(f"{'='*60}\n")
