import sys
import os
import shutil
from fastapi import FastAPI, UploadFile, File

# Add src directory to Python path
SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SRC_PATH)

from input_parser.pdf_parser import extract_text_from_pdf
from extraction.parameter_extractor import extract_parameters
from validation.data_validator import validate_parameters
from models.model_1_parameter_interpretation import interpret_parameters
from models.model_2_pattern_analysis import analyze_patterns
from synthesis.findings_synthesizer import synthesize_findings
from recommendation.recommendation_generator import generate_recommendations
from report.report_generator import generate_report


app = FastAPI(title="Automated Health Diagnostics API")

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/analyze-report/")
async def analyze_report(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Pipeline
    report_text = extract_text_from_pdf(file_path)
    parameters = extract_parameters(report_text)
    validated_parameters, issues = validate_parameters(parameters)
    interpretation = interpret_parameters(validated_parameters)
    risks = analyze_patterns(validated_parameters, interpretation)
    summary = synthesize_findings(interpretation, risks)
    recommendations = generate_recommendations(interpretation, risks)
    final_report = generate_report(
        validated_parameters,
        interpretation,
        risks,
        summary,
        recommendations
    )

    return {
        "parameters": validated_parameters,
        "interpretation": interpretation,
        "risks": risks,
        "summary": summary,
        "recommendations": recommendations,
        "final_report": final_report,
        "validation_issues": issues
    }
