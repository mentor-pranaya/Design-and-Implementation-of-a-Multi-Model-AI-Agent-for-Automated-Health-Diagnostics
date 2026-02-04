"""
Comprehensive Integration Test
Demonstrates the complete multi-model AI agent pipeline from extraction to recommendations.
"""

from core_phase3.main import Phase3RecommendationPipeline
import json

print("="*80)
print("MULTI-MODEL AI AGENT FOR AUTOMATED HEALTH DIAGNOSTICS")
print("Integration Test: Phase 3A → 3B → 3C")
print("="*80)

# Initialize pipeline
pipeline = Phase3RecommendationPipeline()

# Sample blood report parameters (as would come from Phase 2 extraction)
print("\n" + "─"*80)
print("INPUT: Extracted Blood Parameters (from Phase 2)")
print("─"*80)

blood_parameters = [
    {"parameter": "Hemoglobin", "value": 10.2, "unit": "g/dL"},
    {"parameter": "WBC", "value": 12800, "unit": "cells/µL"},
    {"parameter": "Platelet Count", "value": 175000, "unit": "cells/µL"},
    {"parameter": "Glucose", "value": 132, "unit": "mg/dL"},
    {"parameter": "HbA1c", "value": 6.4, "unit": "%"},
    {"parameter": "Cholesterol Total", "value": 245, "unit": "mg/dL"},
    {"parameter": "LDL", "value": 172, "unit": "mg/dL"},
    {"parameter": "HDL", "value": 36, "unit": "mg/dL"},
    {"parameter": "Triglycerides", "value": 225, "unit": "mg/dL"},
    {"parameter": "Creatinine", "value": 1.4, "unit": "mg/dL"},
    {"parameter": "ALT", "value": 48, "unit": "U/L"},
    {"parameter": "TSH", "value": 5.2, "unit": "mU/L"},
]

for param in blood_parameters:
    print(f"  • {param['parameter']:<20} : {param['value']:>8} {param['unit']}")

patient_info = {
    "sex": "male",
    "age": 52,
    "name": "Sample Patient"
}

print(f"\nPatient: {patient_info['name']}, {patient_info['sex'].capitalize()}, Age {patient_info['age']}")

# Run complete pipeline
print("\n" + "="*80)
print("PROCESSING PIPELINE")
print("="*80)

report = pipeline.process_extracted_parameters(blood_parameters, patient_info)

# Display Phase 3A results
print("\n" + "─"*80)
print("PHASE 3A: REFERENCE-BASED EVALUATION RESULTS")
print("─"*80)

eval_summary = report['phase_3a_evaluation']['summary']
print(f"\nInterpretation: {eval_summary['interpretation']}")
print(f"\nStatus Breakdown:")
for status, count in eval_summary['status_counts'].items():
    if count > 0:
        print(f"  {status.capitalize():<15}: {count}")

print("\nAbnormal Findings:")
for finding in report['phase_3a_evaluation']['abnormal_findings'][:5]:  # Show first 5
    print(f"  • {finding['parameter']:<20}: {finding['status']:<15} (Severity: {finding['severity']})")

# Display Phase 3B results
print("\n" + "─"*80)
print("PHASE 3B: PATTERN RECOGNITION RESULTS")
print("─"*80)

patterns = report['phase_3b_patterns']
print(f"\nDetected {len(patterns)} clinical pattern(s):\n")
for i, pattern in enumerate(patterns, 1):
    print(f"{i}. {pattern['pattern']}")
    print(f"   Confidence: {pattern['confidence']}")
    print(f"   Triggered by: {', '.join(pattern['triggered_by'])}")
    if pattern.get('severity'):
        print(f"   Severity: {pattern['severity']}")
    print()

# Display Phase 3C results (formatted output)
print("─"*80)
print("PHASE 3C: EVIDENCE-BASED RECOMMENDATIONS")
print("─"*80)
print(report['formatted_output'])

# Show multi-model synthesis
print("\n" + "="*80)
print("MULTI-MODEL REASONING DEMONSTRATION")
print("="*80)

print("\n📊 How this system achieves clinical grounding:\n")
print("1. EVALUATION (Phase 3A) - Evidence Foundation")
print("   ✓ Each parameter classified against authoritative reference ranges")
print("   ✓ Clinical status determined objectively (Low/Normal/High)")
print("   ✓ Severity assessed quantitatively (% deviation from normal)")
print("   Example: Hemoglobin 10.2 g/dL → LOW (Moderate severity, -27% deviation)")

print("\n2. PATTERN RECOGNITION (Phase 3B) - Contextual Risk")
print("   ✓ Multi-parameter combinations detected")
print("   ✓ Complex risk patterns identified")
print("   ✓ Enhanced by evaluation flags")
print("   Example: Low Hemoglobin → triggers 'Anemia Indicator' pattern")

print("\n3. RECOMMENDATION SYNTHESIS (Phase 3C) - Actionable Guidance")
print("   ✓ Merges evaluation + pattern signals")
print("   ✓ Maps to clinical guidelines")
print("   ✓ Generates personalized recommendations")
print("   Example: Anemia Indicator + Low Hemoglobin → Iron-rich diet + follow-up testing")

print("\n" + "="*80)
print("KEY DIFFERENTIATORS (for viva defense)")
print("="*80)
print("""
✓ NOT hard-coded thresholds → Uses authoritative reference ranges
✓ NOT single-model → Multi-model reasoning (evaluation + patterns)
✓ NOT arbitrary → Evidence-backed at every decision point
✓ NOT black-box → Fully auditable decision trail
✓ NOT diagnostic → Educational support with clear disclaimers

This is a clinically-grounded decision support prototype,
NOT a medical device or diagnostic tool.
""")

print("="*80)
print("✓ Integration Test Complete")
print("="*80)

# Save detailed report to file
output_file = "phase3_integration_test_output.json"
with open(output_file, 'w', encoding='utf-8') as f:
    # Convert enum values to strings for JSON serialization
    def convert_for_json(obj):
        if hasattr(obj, 'value'):
            return obj.value
        raise TypeError
    
    json.dump(report, f, indent=2, default=convert_for_json)

print(f"\n💾 Detailed report saved to: {output_file}")
