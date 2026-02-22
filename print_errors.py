"""Print classification errors from validation."""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core_phase3'))

from evaluation_runner import ValidationRunner

validation_dir = project_root / "validation_dataset"
runner = ValidationRunner(validation_dir, project_root)
metrics = runner.run_validation()

print("\n" + "="*80)
print("CLASSIFICATION ERRORS (Model 1)")
print("="*80)

errors = runner.model1_evaluator.errors
print(f"\nTotal Errors: {len(errors)}\n")

for i, error in enumerate(errors, 1):
    print(f"{i}. [{error['case']}] {error['parameter']}")
    print(f"   Error Type: {error.get('error_type')}")
    print(f"   Value: {error.get('value', 'N/A')}")
    print(f"   Expected: {error.get('expected', 'N/A')}")
    print(f"   Predicted: {error.get('predicted', 'MISSING')}")
    if 'reference' in error:
        print(f"   Reference: {error['reference']}")
    print()
