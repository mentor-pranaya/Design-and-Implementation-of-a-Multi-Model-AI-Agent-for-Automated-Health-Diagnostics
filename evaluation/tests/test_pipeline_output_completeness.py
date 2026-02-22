"""
Property-based test for pipeline output completeness.

Feature: milestone-1-validation
Property 16: Pipeline Output Completeness

For any completed pipeline run, it should produce both console output (summary)
and a detailed results file.

Validates: Requirements 9.4
"""

import pytest
from hypothesis import given, strategies as st, settings
import tempfile
import json
from pathlib import Path
from io import StringIO
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.validation_pipeline import ValidationPipeline


# Feature: milestone-1-validation, Property 16: Pipeline Output Completeness
@given(
    num_reports=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=50, deadline=None)
def test_pipeline_produces_complete_output(num_reports):
    """
    Property 16: Pipeline Output Completeness
    
    For any completed pipeline run, it should produce both console output (summary)
    and a detailed results file.
    
    **Validates: Requirements 9.4**
    """
    pipeline = ValidationPipeline()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ground_truth_dir = tmpdir / "ground_truth"
        ground_truth_dir.mkdir()
        
        # Create ground truth files
        for i in range(num_reports):
            report_id = f"report_{i:03d}"
            
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
                    "hemoglobin": {
                        "value": 14.5,
                        "unit": "g/dL",
                        "reference_range": {"min": 13.0, "max": 17.5}
                    }
                },
                "classifications": {
                    "hemoglobin": "Normal"
                }
            }
            
            with open(ground_truth_dir / f"{report_id}.json", 'w') as f:
                json.dump(gt_data, f)
        
        # Capture console output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Run validation pipeline
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),  # Will cause errors
                ground_truth_dir=str(ground_truth_dir)
            )
        finally:
            sys.stdout = old_stdout
        
        console_output = captured_output.getvalue()
        
        # Property assertions:
        # 1. Pipeline should return detailed results dictionary
        assert results is not None
        assert isinstance(results, dict)
        
        # 2. Results should contain all required fields
        required_fields = [
            'timestamp',
            'reports_processed',
            'reports_with_errors',
            'accuracy_metrics',
            'per_report_results',
            'errors',
            'target_met'
        ]
        for field in required_fields:
            assert field in results, f"Missing required field: {field}"
        
        # 3. Console output should be produced (summary)
        assert len(console_output) > 0, "No console output produced"
        
        # 4. Console output should contain key information
        assert "VALIDATION PIPELINE" in console_output
        assert "Loading ground truth files" in console_output
        assert "CALCULATING OVERALL ACCURACY" in console_output
        assert "VALIDATION COMPLETE" in console_output
        
        # 5. Console output should show progress for each report
        assert "Validating:" in console_output
        
        # 6. Console output should show final metrics
        assert "Total parameters evaluated:" in console_output
        assert "Overall accuracy:" in console_output
        
        # 7. Results dictionary should be serializable (can be saved to file)
        try:
            json_str = json.dumps(results)
            assert len(json_str) > 0
            # Verify it can be loaded back
            loaded = json.loads(json_str)
            assert loaded == results
        except (TypeError, ValueError) as e:
            pytest.fail(f"Results not JSON serializable: {e}")
        
        # 8. Accuracy metrics should be complete
        accuracy_metrics = results['accuracy_metrics']
        assert 'total_parameters' in accuracy_metrics
        assert 'correct_classifications' in accuracy_metrics
        assert 'incorrect_classifications' in accuracy_metrics
        assert 'accuracy_percentage' in accuracy_metrics
        
        # 9. Per-report results should be present
        assert isinstance(results['per_report_results'], list)
        
        # 10. Errors list should be present (even if empty)
        assert isinstance(results['errors'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

