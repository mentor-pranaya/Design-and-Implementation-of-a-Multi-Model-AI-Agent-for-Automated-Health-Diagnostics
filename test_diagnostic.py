"""
Quick diagnostic test to check why patterns aren't being detected for John Doe.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'core_phase3'))

from core_phase3.evaluation.evaluator import ParameterEvaluator


def load_john_doe():
    """Load John Doe's report."""
    file_path = Path(__file__).parent / 'data' / 'sample_reports' / 'sample_blood_report_1.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    report = load_john_doe()
    
    # Convert to evaluation format
    params = []
    for param in report['parameters']:
        params.append({
            'parameter': param['name'],
            'value': param['value'],
            'unit': param.get('unit', '')
        })
    
    # Evaluate
    evaluator = ParameterEvaluator()
    patient_info = report['patient_info']
    if 'gender' in patient_info and 'sex' not in patient_info:
        patient_info['sex'] = patient_info['gender']
    
    results = evaluator.evaluate_parameters(params, patient_info)
    
    print("\n=== John Doe's Lab Results ===")
    print(f"Total evaluated: {results['total_parameters_evaluated']}")
    print(f"Abnormal: {len(results['abnormal_findings'])}")
    print(f"Critical: {len(results['critical_findings'])}")
    
    print("\n=== Parameter Details ===")
    for eval in results['evaluations']:
        status = eval['status']
        if hasattr(status, 'value'):
            status = status.value
        severity = eval.get('severity', 'None')
        print(f"{eval['parameter']:20} {eval['value']:8} {status:15} (Severity: {severity})")
    
    print("\n=== Pattern Flags ===")
    flags = results.get('flags_for_pattern_recognition', [])
    print(f"Pattern flags detected: {len(flags)}")
    for flag in flags:
        print(f"  - {flag['pattern_type']}: triggered by {flag['triggered_by']}")
    
    print("\n=== Abnormal Findings ===")
    for finding in results['abnormal_findings']:
        print(f"  {finding['parameter']}: {finding['status']} ({finding['severity']})")


if __name__ == "__main__":
    main()
