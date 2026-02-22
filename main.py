import argparse
import os
import sys
from extractor import extract_text
from ocr_extractor import extract_text_with_ocr
from cleaner import extract_parameters
from model1 import interpret
from risk_model import assess_risk
from context_model import apply_context
from health_risk_explainer import explain_health_risks
from synthesis_engine import synthesize_findings
from recommendation_generator import generate_recommendations
from report_generator import generate_report


def process_report_complete_pipeline(pdf_path, age=None, gender=None, output_format="text", save_to_file=False):
    """
    Complete processing pipeline for the blood report, returning all intermediate and final results.
    Compatible with the Streamlit UI.
    """
    # 1. Extraction
    text = extract_text(pdf_path)
    if not text or len(text.strip()) < 50:
        text = extract_text_with_ocr(pdf_path)
    
    if not text:
        return {"error": "Could not extract text from the report."}

    # 2. Parameter Extraction
    parameters = extract_parameters(text)
    if not parameters:
        return {"error": "No blood parameters detected."}

    # 3. Model Analysis
    interpretation = interpret(parameters)
    risk_assessment = assess_risk(parameters)
    contextual_risk = apply_context(risk_assessment, age=age, gender=gender)

    # 4. Synthesis & Recommendations
    synthesis = synthesize_findings(parameters, interpretation, risk_assessment, contextual_risk, age=age, gender=gender)
    recommendations = generate_recommendations(synthesis, parameters, interpretation, risk_assessment, age=age, gender=gender)

    # 5. Report Generation
    filename = f"Report_{os.path.basename(pdf_path).split('.')[0]}" if save_to_file else None
    report_content = generate_report(
        synthesis, recommendations, parameters, interpretation,
        risk_assessment, contextual_risk, age=age, gender=gender,
        filename=filename,
        output_format=output_format
    )

    return {
        "report": report_content,
        "synthesis": synthesis,
        "recommendations": recommendations,
        "parameters": parameters,
        "interpretation": interpretation,
        "risk_assessment": risk_assessment,
        "contextual_risk": contextual_risk,
        "text": text
    }


def orchestrate(pdf_path, age=None, gender=None, output_format="text"):
    print(f"--- Starting Orchestration for: {pdf_path} ---")
    result = process_report_complete_pipeline(pdf_path, age=age, gender=gender, output_format=output_format, save_to_file=True)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return False
    
    print(f"--- Orchestration Complete! Report saved. ---")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Model AI Agent for Automated Health Diagnostics")
    parser.add_argument("--pdf", type=str, default="OCR_Test_Scanned_Report.pdf", help="Path to the blood report PDF")
    parser.add_argument("--age", type=int, default=50, help="User age")
    parser.add_argument("--gender", type=str, default="female", help="User gender")
    parser.add_argument("--format", type=str, default="text", choices=["text", "markdown", "html", "json"], help="Output format")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf):
        print(f"Error: File {args.pdf} not found.")
        sys.exit(1)
        
    success = orchestrate(args.pdf, age=args.age, gender=args.gender, output_format=args.format)
    if not success:
        sys.exit(1)
