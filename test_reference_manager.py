"""Quick test of reference range manager"""
from core_phase3.knowledge_base.reference_manager import ReferenceRangeManager, evaluate_lab_value

manager = ReferenceRangeManager()
print('Available parameters:', len(manager.get_parameter_names()))
print('\nTest Evaluation - Low Hemoglobin:')
result = evaluate_lab_value('Hemoglobin', 10.5, sex='female')
print(f"Parameter: {result['parameter']}")
print(f"Value: {result['value']} {result['unit']}")
print(f"Status: {result['status'].value}")
print(f"Severity: {result['severity']}")
print(f"Reference Range: {result['reference_range']}")
print(f"Deviation: {result['deviation_percent']:.1f}%")

print('\n\nTest Evaluation - High Glucose:')
result2 = evaluate_lab_value('Glucose', 130)
print(f"Parameter: {result2['parameter']}")
print(f"Value: {result2['value']} {result2['unit']}")
print(f"Status: {result2['status'].value}")
print(f"Severity: {result2['severity']}")
