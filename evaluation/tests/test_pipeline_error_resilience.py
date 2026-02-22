"""
Property-based test for pipeline error resilience.

Feature: milestone-1-validation
Property 15: Pipeline Error Resilience

For any validation pipeline run, if an individual report fails to process,
the pipeline should continue processing remaining reports and include the
error in the final summary.

Validates: Requirements 9.3
"""

import pytest
from hypothesis import given, strategies as st, settings
import tempfile
import json
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.validation_pipeline import ValidationPipeline


# Strategy for generating ground truth data
@st.composite
def ground_truth_data(draw):
    """Generate valid ground truth data."""
    report_id = draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'P'))))
    
    # Generate 1-5 parameters
    num_params = draw(st.integers(min_value=1, max_value=5))
    parameters = {}
    classifications = {}
    
    param_names = ['hemoglobin', 'glucose', 'creatinine', 'cholesterol', 'wbc']
    
    for i in range(num_params):
        param_name = param_names[i]
        value = draw(st.floats(min_value=0.1, max_value=500.0, allow_nan=False, allow_infinity=False))
        
        parameters[param_name] = {
            "value": round(value, 2),
            "unit": "mg/dL",
            "reference_range": {
                "min": round(value * 0.8, 2),
                "max": round(value * 1.2, 2)
            }
        }
        classifications[param_name] = draw(st.sampled_from(['Normal', 'High', 'Low']))
    
    return {
        "report_id": report_id,
        "report_metadata": {
            "laboratory": "Test Lab",
            "format": "PDF",
            "date": "2026-01-15",
            "completeness": "Complete",
            "abnormality_type": "Normal"
        },
        "parameters": parameters,
        "classifications": classifications
    }


# Feature: milestone-1-validation, Property 15: Pipeline Error Resilience
@given(
    num_invalid_reports=st.integers(min_value=1, max_value=3)
)
@settings(max_examples=50, deadline=None)
def test_pipeline_continues_on_individual_report_failure(num_invalid_reports):
    """
    Property 15: Pipeline Error Resilience
    
    For any validation pipeline run, if an individual report fails to process,
    the pipeline should continue processing remaining reports and include the
    error in the final summary.
    
    **Validates: Requirements 9.3**
    """
    pipeline = ValidationPipeline()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ground_truth_dir = tmpdir / "ground_truth"
        ground_truth_dir.mkdir()
        
        # Create invalid ground truth files (missing corresponding reports)
        # These will cause "Report file not found" errors
        invalid_report_ids = []
        for i in range(num_invalid_reports):
            report_id = f"report_missing_{i:03d}"
            invalid_report_ids.append(report_id)
            
            # Create ground truth file but NO corresponding report
            gt_data = {
                "report_id": report_id,
                "report_metadata": {
                    "laboratory": "Test Lab",
                    "format": "PDF",
                    "date": "2026-01-15",
                    "completeness": "Complete",
                    "abnormality_type": "Normal"
                },
                "parameters": {
                    "glucose": {
                        "value": 100.0,
                        "unit": "mg/dL",
                        "reference_range": {"min": 70.0, "max": 99.0}
                    }
                },
                "classifications": {
                    "glucose": "High"
                }
            }
            
            with open(ground_truth_dir / f"{report_id}.json", 'w') as f:
                json.dump(gt_data, f)
            # Note: No report file created - this will cause an error
        
        # Run validation pipeline
        # We don't create a reports_dir, so all reports will fail with "Report file not found"
        results = pipeline.run_validation(
            reports_dir=str(tmpdir / "nonexistent_reports"),
            ground_truth_dir=str(ground_truth_dir)
        )
        
        # Property assertions:
        # 1. Pipeline should complete (not crash) even when all reports fail
        assert results is not None
        
        # 2. Pipeline should process all ground truth files
        assert results['reports_processed'] == num_invalid_reports
        
        # 3. Errors should be recorded for all invalid reports
        assert 'errors' in results
        assert len(results['errors']) == num_invalid_reports
        
        # 4. Accuracy metrics should still be present (even if 0)
        assert 'accuracy_metrics' in results
        
        # 5. Each error should have report_id and error message
        for error in results['errors']:
            assert 'report_id' in error
            assert 'error' in error
            assert error['report_id'] in invalid_report_ids
            # Should be "Report file not found" error
            assert 'not found' in error['error'].lower() or 'error' in error['error'].lower()
        
        # 6. Pipeline should report that it processed all ground truth files
        # even though they all failed
        assert results['reports_with_errors'] == num_invalid_reports


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

