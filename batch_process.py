"""
Batch Medical Report Processor
Processes all medical report PDFs in the directory and generates a summary
"""
from extractor import extract_text
from ocr_extractor import extract_text_with_ocr
from cleaner import extract_parameters
from model1 import interpret
from risk_model import assess_risk
from context_model import apply_context
from health_risk_explainer import explain_health_risks
import os
from pathlib import Path

def process_report(pdf_path):
    """Process a single medical report and return results"""
    try:
        # Try standard PDF extraction first
        text = extract_text(pdf_path)
        if not text.strip():
            raise ValueError("Empty text")
    except:
        # Fall back to OCR for scanned documents
        text = extract_text_with_ocr(pdf_path)

    parameters = extract_parameters(text)
    interpretation = interpret(parameters)
    risk = assess_risk(parameters)
    final_risk = apply_context(risk, age=50, gender="female")
    health_risks = explain_health_risks(parameters, final_risk)
    
    return {
        'file': os.path.basename(pdf_path),
        'parameters': parameters,
        'interpretation': interpretation,
        'risk': risk,
        'contextual_risk': final_risk,
        'health_risks': health_risks
    }

if __name__ == "__main__":
    # Find all PDF files in current directory
    pdf_files = list(Path(".").glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in current directory.")
        exit(1)
    
    print(f"\nFound {len(pdf_files)} PDF file(s)\n")
    
    results = []
    for pdf_file in sorted(pdf_files):
        print(f"Processing: {pdf_file.name}...", end=" ")
        try:
            result = process_report(str(pdf_file))
            results.append(result)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"BATCH PROCESSING SUMMARY - {len(results)} report(s) processed")
    print(f"{'='*70}\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['file']}")
        if result['parameters']:
            print(f"   Parameters: {result['parameters']}")
            print(f"   Risk Level: {max(result['risk'].values()) if result['risk'] else 'N/A'}")
        else:
            print(f"   No parameters extracted")
        print()
