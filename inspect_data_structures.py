"""
Inspect data structures passed to risk engine for redesign.
"""

import json
import sys
from pathlib import Path
from pprint import pprint

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core_phase3'))

from core_phase3.main import Phase3RecommendationPipeline

# Load case_04 (most complex case)
with open("data/sample_reports/sample_blood_report_4.json", 'r') as f:
    report_data = json.load(f)

params_data = report_data.get("parameters", [])
extracted_params = [
    {"parameter": p["name"], "value": p["value"], "unit": p.get("unit", "")}
    for p in params_data
]

patient_info = report_data["patient_info"].copy()
if 'gender' in patient_info:
    patient_info['sex'] = patient_info['gender']

pipeline = Phase3RecommendationPipeline()
result = pipeline.process_extracted_parameters(extracted_params, patient_info)

print("="*80)
print("PATIENT_INFO STRUCTURE")
print("="*80)
pprint(patient_info)

print("\n" + "="*80)
print("PHASE_3A_EVALUATION STRUCTURE (evaluation_results)")
print("="*80)
evaluation_results = result.get("phase_3a_evaluation", {})
print(f"Top-level keys: {list(evaluation_results.keys())}")

if 'evaluations' in evaluation_results:
    evals = evaluation_results['evaluations']
    print(f"\nTotal evaluations: {len(evals)}")
    print(f"\nSample evaluation (first parameter):")
    pprint(evals[0])
    
    print(f"\nAll evaluated parameters:")
    for e in evals:
        severity = e.get('severity', 'None')
        print(f"  {e['parameter']}: {e['value']} {e.get('unit', '')} - Status: {e['status']}, Severity: {severity}")

print("\n" + "="*80)
print("PHASE_3B_PATTERNS STRUCTURE (detected patterns)")
print("="*80)
patterns = result.get("phase_3b_patterns", [])
print(f"Type: {type(patterns)}")
print(f"Total patterns: {len(patterns)}")

if patterns:
    print(f"\nDetected patterns:")
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. Pattern structure:")
        pprint(pattern)

print("\n" + "="*80)
print("WHAT RISK ENGINE RECEIVES")
print("="*80)
print("""
CardiovascularRiskScorer.__init__(
    patient_info={...},        # Full patient context above
    evaluated_params={...}     # Full phase_3a_evaluation dict
)

Access patterns:
- self.patient_info.get('age')
- self.patient_info.get('sex')  
- self.patient_info.get('known_conditions')
- self.patient_info.get('lifestyle')

Access evaluations:
- self.params['evaluations'] → list of evaluation dicts
- Each eval has: parameter, value, unit, status, severity, reference_range

Currently MISSING in risk engine:
- Detected patterns from phase_3b_patterns
- Severity classifications from Model 1
""")

print("\n" + "="*80)
print("SEVERITY DISTRIBUTION (Case 04)")
print("="*80)
severity_counts = {}
for e in evals:
    sev = e.get('severity') or 'None'
    severity_counts[sev] = severity_counts.get(sev, 0) + 1

for severity, count in sorted(severity_counts.items()):
    print(f"  {severity}: {count} parameters")
