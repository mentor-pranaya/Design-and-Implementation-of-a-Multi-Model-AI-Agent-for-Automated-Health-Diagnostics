"""
Model 1 Diagnostic Tool - Detailed Classification Analysis

This script analyzes classification errors in detail to identify:
- Threshold boundary errors
- Unit normalization issues
- Sex-specific range misapplication
- Reference range source conflicts
"""

import json
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core_phase3'))

from core_phase3.main import Phase3RecommendationPipeline


def analyze_single_parameter(param_name: str, value: float, unit: str, patient_info: dict, 
                            expected_classification: str, expected_severity: str = None):
    """
    Detailed analysis of a single parameter classification.
    """
    print(f"\n{'='*80}")
    print(f"DIAGNOSTIC: {param_name}")
    print(f"{'='*80}")
    print(f"Value: {value} {unit}")
    print(f"Patient: {patient_info.get('age')}yo {patient_info.get('sex')}")
    print(f"Expected: {expected_classification}", end="")
    if expected_severity:
        print(f" ({expected_severity} severity)")
    else:
        print()
    
    # Run pipeline
    pipeline = Phase3RecommendationPipeline()
    extracted_params = [{"parameter": param_name, "value": value, "unit": unit}]
    
    try:
        result = pipeline.process_extracted_parameters(extracted_params, patient_info)
        
        # Find evaluation
        evaluations = result.get("phase_3a_evaluation", {}).get("evaluations", [])
        param_eval = next((e for e in evaluations if e.get("parameter") == param_name), None)
        
        if param_eval:
            print(f"\nActual Classification:")
            print(f"  Status: {param_eval.get('status')}")
            print(f"  Severity: {param_eval.get('severity')}")
            print(f"  Reference Range: {param_eval.get('reference_range')}")
            print(f"  Source: {param_eval.get('source', 'Unknown')}")
            print(f"  Confidence: {param_eval.get('confidence_level', 'Unknown')}")
            
            # Check if correct
            actual_status = str(param_eval.get('status')).lower().replace('_', ' ')
            expected_status = expected_classification.lower().replace('_', ' ')
            
            if actual_status == expected_status:
                print(f"\n✓ CORRECT")
            else:
                print(f"\n✗ MISMATCH")
                print(f"  Expected: {expected_classification}")
                print(f"  Got: {param_eval.get('status')}")
                
                # Diagnose why
                print(f"\nDiagnostic Analysis:")
                ref_range = param_eval.get('reference_range', {})
                
                if isinstance(ref_range, dict):
                    # Check threshold boundaries
                    if 'low' in ref_range and 'high' in ref_range:
                        low_threshold = ref_range['low']
                        high_threshold = ref_range['high']
                        print(f"  Using ABIM format: low={low_threshold}, high={high_threshold}")
                        
                        if value < low_threshold:
                            print(f"  {value} < {low_threshold} → Should be LOW")
                        elif value > high_threshold:
                            print(f"  {value} > {high_threshold} → Should be HIGH")
                        else:
                            print(f"  {low_threshold} ≤ {value} ≤ {high_threshold} → Should be NORMAL")
                    
                    elif 'min' in ref_range and 'max' in ref_range:
                        min_val = ref_range['min']
                        max_val = ref_range['max']
                        print(f"  Using legacy format: min={min_val}, max={max_val}")
                        
                        if value < min_val:
                            print(f"  {value} < {min_val} → Should be LOW")
                        elif value > max_val:
                            print(f"  {value} > {max_val} → Should be HIGH")
                        else:
                            print(f"  {min_val} ≤ {value} ≤ {max_val} → Should be NORMAL")
                
                # Check if unit mismatch
                if unit and isinstance(value, str) and unit in str(value):
                    print(f"  ⚠ WARNING: Unit '{unit}' appears in value '{value}' - possible string comparison")
                
                # Check for inclusive/exclusive boundary issue
                print(f"\\n  Boundary Check:")
                if isinstance(ref_range, dict):
                    if 'low' in ref_range and abs(value - ref_range['low']) < 0.01:
                        print(f"    Value {value} is AT lower boundary {ref_range['low']}")
                        print(f"    Check if using > vs >= (inclusive/exclusive)")
                    if 'high' in ref_range and abs(value - ref_range['high']) < 0.01:
                        print(f"    Value {value} is AT upper boundary {ref_range['high']}")
                        print(f"    Check if using < vs <= (inclusive/exclusive)")
        else:
            print(f"\n✗ Parameter not found in evaluation results")
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


def diagnose_all_errors():
    """Diagnose all classification errors from validation dataset."""
    print("\n" + "="*80)
    print("MODEL 1 DIAGNOSTIC REPORT")
    print("="*80)
    
    validation_dir = project_root / "validation_dataset"
    
    # Focus on known problem cases
    problem_cases = [
        {
            "file": "case_01/ground_truth.json",
            "focus_parameters": ["HbA1c", "Glucose", "LDL"]
        },
        {
            "file": "case_03/ground_truth.json",
            "focus_parameters": ["HbA1c", "Glucose", "HDL", "AST"]
        }
    ]
    
    for case_info in problem_cases:
        gt_file = validation_dir / case_info["file"]
        
        with open(gt_file, 'r') as f:
            ground_truth = json.load(f)
        
        # Load source report
        source_path = project_root / ground_truth["source_report"].replace("../../", "")
        with open(source_path, 'r') as f:
            report_data = json.load(f)
        
        patient_info = report_data["patient_info"].copy()
        if 'gender' in patient_info:
            patient_info['sex'] = patient_info['gender']
        
        print(f"\n{'#'*80}")
        print(f"Case: {ground_truth['case_id']} - {ground_truth['description']}")
        print(f"{'#'*80}")
        
        # Analyze focus parameters
        for param_name in case_info["focus_parameters"]:
            if param_name in ground_truth["true_parameters"]:
                value = ground_truth["true_parameters"][param_name]
                expected_class = ground_truth["true_classification"][param_name]
                expected_sev = ground_truth.get("true_severity", {}).get(param_name)
                
                # Get unit from source data
                unit = ""
                for p in report_data.get("parameters", []):
                    if p.get("name") == param_name:
                        unit = p.get("unit", "")
                        break
                
                analyze_single_parameter(param_name, value, unit, patient_info, 
                                       expected_class, expected_sev)


def check_hba1c_thresholds():
    """Specifically check HbA1c threshold logic."""
    print("\n" + "="*80)
    print("HbA1c THRESHOLD VERIFICATION")
    print("="*80)
    print("\nClinical Guidelines (ADA):")
    print("  < 5.7%  → Normal")
    print("  5.7-6.4% → Prediabetes (should be classified as High/Mild)")
    print("  ≥ 6.5%  → Diabetes (should be classified as High/Severe)")
    
    test_cases = [
        (5.6, "Normal"),
        (5.7, "High"),  # At prediabetes threshold
        (6.2, "High"),  # Prediabetes
        (6.4, "High"),  # Upper prediabetes
        (6.5, "High"),  # Diabetes threshold
        (7.8, "High"),  # Uncontrolled diabetes
    ]
    
    patient_info = {"age": 45, "sex": "male", "known_conditions": []}
    
    print(f"\n{'Value':8} | Expected | Actual | Match")
    print("-" * 45)
    
    for value, expected in test_cases:
        pipeline = Phase3RecommendationPipeline()
        extracted_params = [{"parameter": "HbA1c", "value": value, "unit": "%"}]
        
        result = pipeline.process_extracted_parameters(extracted_params, patient_info)
        evaluations = result.get("phase_3a_evaluation", {}).get("evaluations", [])
        param_eval = next((e for e in evaluations if e.get("parameter") == "HbA1c"), None)
        
        if param_eval:
            actual = str(param_eval.get('status')).replace('_', ' ')
            match = "✓" if actual.lower() == expected.lower() else "✗"
            print(f"{value:6.1f}% | {expected:8} | {actual:8} | {match}")
        else:
            print(f"{value:6.1f}% | {expected:8} | NOT FOUND | ✗")


if __name__ == "__main__":
    # Run targeted diagnostics
    check_hba1c_thresholds()
    print("\n")
    diagnose_all_errors()
