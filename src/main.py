import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from input_parser.pdf_parser import extract_text_from_pdf
from extraction.parameter_extractor import extract_parameters
from validation.data_validator import validate_parameters
from models.model_1_parameter_interpretation import interpret_parameters
from models.model_2_pattern_analysis import analyze_patterns
from synthesis.findings_synthesizer import synthesize_findings
from recommendation.recommendation_generator import generate_recommendations
from report.report_generator import generate_report

pdf_path = "data/sample_report/report.pdf"

# 1. Extract text
report_text = extract_text_from_pdf(pdf_path)

# 2. Extract parameters
parameters = extract_parameters(report_text)

# 3. Validate
validated_parameters, validation_issues = validate_parameters(parameters)

# 4. Model-1
interpretation = interpret_parameters(validated_parameters)

# 5. Model-2
risk_patterns = analyze_patterns(validated_parameters, interpretation)

# 6. Synthesis
summary = synthesize_findings(interpretation, risk_patterns)

# 7. Recommendations
recommendations = generate_recommendations(interpretation, risk_patterns)

# 8. Final Report
final_report = generate_report(
    validated_parameters,
    interpretation,
    risk_patterns,
    summary,
    recommendations
)

print("\n" + final_report)

if validation_issues:
    print("\n⚠️ Validation Issues:")
    for issue in validation_issues:
        print("-", issue)
