"""
Test script to verify API integration with the processing pipeline
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_phase1.ingestion.loader import load_input
from core_phase1.extraction.parser import extract_parameters
from core_phase3.evaluation.evaluator import ParameterEvaluator
from core_phase3.main import Phase3RecommendationPipeline

def test_pipeline():
    print("Testing Blood Report Processing Pipeline Integration")
    print("=" * 70)
    
    # Test with the JSON file
    test_file = "test_report.json"
    
    print(f"\n1. Loading file: {test_file}")
    raw_data = load_input(test_file)
    print(f"   ✓ Loaded {len(raw_data)} parameters")
    
    print("\n2. Extracting parameters...")
    extracted_data = extract_parameters(raw_data)
    print(f"   ✓ Extracted {len(extracted_data)} parameters")
    
    # Convert to list format
    extracted_parameters = [
        {"parameter": param, "value": data["value"], "unit": data.get("unit", "")}
        for param, data in extracted_data.items()
    ]
    
    print("\n3. Running Phase 3 pipeline...")
    pipeline = Phase3RecommendationPipeline()
    patient_info = {"sex": "M", "age": 45}
    
    phase3_report = pipeline.process_extracted_parameters(
        extracted_parameters, 
        patient_info
    )
    
    print("\n4. Results:")
    print(f"   Total parameters evaluated: {phase3_report['phase_3a_evaluation']['total_parameters_evaluated']}")
    print(f"   Abnormal findings: {len(phase3_report['phase_3a_evaluation']['abnormal_findings'])}")
    print(f"   Critical findings: {len(phase3_report['phase_3a_evaluation']['critical_findings'])}")
    
    # Show some evaluations
    print("\n5. Sample evaluations:")
    for eval_data in phase3_report['phase_3a_evaluation']['evaluations'][:3]:
        status = eval_data['status']
        if hasattr(status, 'value'):
            status_str = status.value
        else:
            status_str = str(status)
        print(f"   - {eval_data['parameter']}: {eval_data['value']} {eval_data.get('extracted_unit', '')} [{status_str}]")
    
    print("\n✓ Pipeline integration test successful!")
    print("=" * 70)

if __name__ == "__main__":
    test_pipeline()
