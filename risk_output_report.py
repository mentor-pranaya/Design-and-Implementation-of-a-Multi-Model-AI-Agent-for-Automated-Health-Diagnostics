"""
Risk Engine Output Report - All Cases
Shows detailed scoring breakdown for calibration
"""

import json
import sys
from pathlib import Path
from pprint import pprint

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core_phase3'))

from core_phase3.main import Phase3RecommendationPipeline

def process_case(case_file, ground_truth_file):
    """Process single case and return risk details."""
    # Load source report
    with open(case_file, 'r') as f:
        report_data = json.load(f)
    
    # Load ground truth
    with open(ground_truth_file, 'r') as f:
        ground_truth = json.load(f)
    
    # Process parameters
    params_data = report_data.get("parameters", [])
    extracted_params = [
        {"parameter": p["name"], "value": p["value"], "unit": p.get("unit", "")}
        for p in params_data
    ]
    
    patient_info = report_data["patient_info"].copy()
    if 'gender' in patient_info:
        patient_info['sex'] = patient_info['gender']
    
    # Run pipeline
    pipeline = Phase3RecommendationPipeline()
    result = pipeline.process_extracted_parameters(extracted_params, patient_info)
    
    health_risk = result.get("phase_3e_risk_scoring", {})
    
    return {
        "case_id": ground_truth["case_id"],
        "description": ground_truth["description"],
        "patient_age": patient_info.get("age"),
        "patient_sex": patient_info.get("sex"),
        "conditions": patient_info.get("known_conditions", []),
        "health_risk": health_risk,
        "expected_category": ground_truth["true_risk_category"],
        "expected_range": ground_truth.get("true_risk_range", {})
    }

# Process all 4 cases
cases = []
for i in range(1, 5):
    case_num = f"0{i}"
    case_file = f"data/sample_reports/sample_blood_report_{i}.json"
    gt_file = f"validation_dataset/case_{case_num}/ground_truth.json"
    
    try:
        case_result = process_case(case_file, gt_file)
        cases.append(case_result)
    except Exception as e:
        print(f"Error processing case_{case_num}: {e}")

# Generate report
print("="*80)
print("COMPREHENSIVE HEALTH RISK ENGINE - COMPLETE OUTPUT REPORT")
print("="*80)

for case in cases:
    print(f"\n{'='*80}")
    print(f"CASE: {case['case_id']} - {case['description']}")
    print(f"{'='*80}")
    
    print(f"\nPatient: {case['patient_sex'].title()}, Age {case['patient_age']}")
    print(f"Conditions: {', '.join(case['conditions']) if case['conditions'] else 'None'}")
    
    risk = case['health_risk']
    
    if 'error' in risk:
        print(f"\n❌ ERROR: {risk['error']}")
        continue
    
    print(f"\n{'─'*80}")
    print(f"RISK ASSESSMENT")
    print(f"{'─'*80}")
    
    print(f"\n  Total Score: {risk.get('total_score', 0)}")
    print(f"  Category:    {risk.get('risk_category', 'Unknown')} (Expected: {case['expected_category']})")
    
    expected_range = case['expected_range']
    if expected_range:
        print(f"  Expected Range: {expected_range.get('min', 0)}-{expected_range.get('max', 100)}%")
    
    match = "✅ MATCH" if risk.get('risk_category') == case['expected_category'] else "❌ MISMATCH"
    print(f"  Validation: {match}")
    
    print(f"\n  Clinical Urgency: {risk.get('clinical_urgency', 'N/A')}")
    
    print(f"\n  Organ Systems Affected: {', '.join(risk.get('organ_systems_affected', [])) or 'None'}")
    
    print(f"\n{'─'*80}")
    print(f"TOP 5 RISK CONTRIBUTORS")
    print(f"{'─'*80}")
    
    contributors = risk.get('top_contributors', [])
    for i, contrib in enumerate(contributors, 1):
        print(f"  {i}. {contrib['factor']:40} +{contrib['points']:2} points")
    
    print(f"\n{'─'*80}")
    print(f"SCORE BREAKDOWN")
    print(f"{'─'*80}")
    
    breakdown = risk.get('score_breakdown', {})
    if breakdown:
        # Group by category
        demographic = {k: v for k, v in breakdown.items() if 'Demographic' in k or 'Sex' in k}
        parameters = {k: v for k, v in breakdown.items() if any(sev in k for sev in ['Mild', 'Moderate', 'Severe', 'Critical'])}
        patterns = {k: v for k, v in breakdown.items() if k in ['Kidney Disease', 'Metabolic Syndrome', 'Electrolyte Imbalance', 'Diabetes Risk', 'Prediabetes Risk', 'Anemia of Chronic Disease', 'Anemia Indicator', 'Liver Health Alert', 'High Cholesterol']}
        amplifiers = {k: v for k, v in breakdown.items() if 'Organ' in k}
        
        if demographic:
            print(f"\n  Demographic Base:")
            for factor, points in demographic.items():
                print(f"    {factor:35} +{points:2}")
        
        if parameters:
            print(f"\n  Parameter Severity (Model 1):")
            for factor, points in sorted(parameters.items(), key=lambda x: x[1], reverse=True):
                print(f"    {factor:35} +{points:2}")
        
        if patterns:
            print(f"\n  Detected Patterns (Model 2):")
            for factor, points in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"    {factor:35} +{points:2}")
        
        if amplifiers:
            print(f"\n  Multi-Organ Amplifier:")
            for factor, points in amplifiers.items():
                print(f"    {factor:35} +{points:2}")

# Summary
print(f"\n\n{'='*80}")
print("SUMMARY - RISK CATEGORY MATCHES")
print(f"{'='*80}\n")

matches = sum(1 for c in cases if c['health_risk'].get('risk_category') == c['expected_category'])
total = len(cases)

print(f"Total Cases:    {total}")
print(f"Matches:        {matches}")
print(f"Mismatches:     {total - matches}")
print(f"Accuracy:       {matches/total*100:.1f}%")

print(f"\nCase-by-Case:")
for case in cases:
    risk_cat = case['health_risk'].get('risk_category', 'Error')
    expected = case['expected_category']
    score = case['health_risk'].get('total_score', 0)
    status = "✅" if risk_cat == expected else "❌"
    
    print(f"  {case['case_id']}: Score={score:3}, Predicted={risk_cat:12}, Expected={expected:12} {status}")

print(f"\n{'='*80}")
