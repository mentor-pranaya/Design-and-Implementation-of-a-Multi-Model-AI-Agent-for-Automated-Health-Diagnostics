"""Test the evaluation engine with sample blood report data"""
from core_phase3.evaluation.evaluator import evaluate_blood_report
import json

# Sample extracted parameters (from Phase 2)
sample_blood_report = [
    {"parameter": "Hemoglobin", "value": 10.8, "unit": "g/dL"},
    {"parameter": "WBC", "value": 12500, "unit": "cells/µL"},
    {"parameter": "Platelet Count", "value": 180000, "unit": "cells/µL"},
    {"parameter": "Glucose", "value": 128, "unit": "mg/dL"},
    {"parameter": "HbA1c", "value": 6.2, "unit": "%"},
    {"parameter": "LDL", "value": 165, "unit": "mg/dL"},
    {"parameter": "HDL", "value": 38, "unit": "mg/dL"},
    {"parameter": "Triglycerides", "value": 210, "unit": "mg/dL"},
    {"parameter": "Creatinine", "value": 1.1, "unit": "mg/dL"},
]

# Patient information
patient_info = {
    "sex": "male",
    "age": 45
}

print("=" * 60)
print("PHASE 3A: REFERENCE-BASED EVALUATION TEST")
print("=" * 60)

# Perform evaluation
evaluation_report = evaluate_blood_report(sample_blood_report, patient_info)

print(f"\n{'Phase:':<25} {evaluation_report['phase']}")
print(f"{'Status:':<25} {evaluation_report['status']}")
print(f"{'Total Parameters:':<25} {evaluation_report['total_parameters_evaluated']}")
print(f"{'With Reference Ranges:':<25} {evaluation_report['parameters_with_reference']}")
print(f"{'Without Reference:':<25} {evaluation_report['parameters_without_reference']}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Interpretation: {evaluation_report['summary']['interpretation']}")
print(f"\nStatus Breakdown:")
for status, count in evaluation_report['summary']['status_counts'].items():
    if count > 0:
        print(f"  {status.capitalize():<15}: {count}")

if evaluation_report['summary']['severity_counts']:
    print(f"\nSeverity Breakdown:")
    for severity, count in evaluation_report['summary']['severity_counts'].items():
        if count > 0:
            print(f"  {severity.capitalize():<15}: {count}")

print("\n" + "=" * 60)
print("ABNORMAL FINDINGS")
print("=" * 60)
for finding in evaluation_report['abnormal_findings']:
    print(f"\n{finding['parameter']}:")
    print(f"  Value: {finding['value']}")
    print(f"  Status: {finding['status']}")
    print(f"  Severity: {finding['severity']}")

if evaluation_report['critical_findings']:
    print("\n" + "=" * 60)
    print("⚠️  CRITICAL FINDINGS")
    print("=" * 60)
    for finding in evaluation_report['critical_findings']:
        print(f"\n{finding['parameter']}:")
        print(f"  Value: {finding['value']}")
        print(f"  Status: {finding['status']}")
        print(f"  {finding['immediate_action']}")

print("\n" + "=" * 60)
print("PATTERN RECOGNITION FLAGS (for Phase 3B)")
print("=" * 60)
for flag in evaluation_report['flags_for_pattern_recognition']:
    print(f"\n{flag['pattern_type']}:")
    print(f"  Triggered by: {', '.join(flag['triggered_by'])}")
    print(f"  Confidence: {flag['confidence']}")

print("\n" + "=" * 60)
print("DETAILED EVALUATIONS")
print("=" * 60)
for eval_item in evaluation_report['evaluations']:
    if eval_item['reference_available']:
        print(f"\n{eval_item['parameter']}:")
        print(f"  Value: {eval_item['value']} {eval_item['unit']}")
        print(f"  Reference Range: {eval_item['reference_range']}")
        print(f"  Status: {eval_item['status'].value}")
        if eval_item['severity']:
            print(f"  Severity: {eval_item['severity']}")
            if eval_item['deviation_percent'] is not None:
                print(f"  Deviation: {eval_item['deviation_percent']:.1f}%")
