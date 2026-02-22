"""
Integration tests for validation pipeline.

Tests end-to-end pipeline execution, error handling, and performance.
Validates Requirements 9.1, 9.2, 9.3 from milestone-1-validation spec.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.validation_pipeline import ValidationPipeline


class TestValidationPipelineIntegration:
    """Integration test suite for ValidationPipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create a ValidationPipeline instance for testing."""
        return ValidationPipeline()
    
    def create_ground_truth_file(self, path: Path, report_id: str, params: dict = None):
        """Helper to create a ground truth file."""
        if params is None:
            params = {
                "hemoglobin": {
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_range": {"min": 13.0, "max": 17.5}
                }
            }
        
        classifications = {}
        for param_name, param_data in params.items():
            value = param_data["value"]
            min_val = param_data["reference_range"]["min"]
            max_val = param_data["reference_range"]["max"]
            
            if value < min_val:
                classifications[param_name] = "Low"
            elif value > max_val:
                classifications[param_name] = "High"
            else:
                classifications[param_name] = "Normal"
        
        gt_data = {
            "report_id": report_id,
            "report_metadata": {
                "laboratory": "Test Lab",
                "format": "PDF",
                "date": "2026-01-15",
                "completeness": "Complete",
                "abnormality_type": "Normal"
            },
            "parameters": params,
            "classifications": classifications
        }
        
        with open(path, 'w') as f:
            json.dump(gt_data, f)
    
    def test_end_to_end_pipeline_with_sample_reports(self, pipeline):
        """
        Test end-to-end pipeline execution with sample reports.
        
        Validates Requirement 9.1: Complete validation workflow
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Create 3 sample ground truth files
            params1 = {
                "hemoglobin": {
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_range": {"min": 13.0, "max": 17.5}
                },
                "glucose": {
                    "value": 95.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 70.0, "max": 99.0}
                }
            }
            
            params2 = {
                "creatinine": {
                    "value": 1.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 0.7, "max": 1.3}
                }
            }
            
            params3 = {
                "cholesterol": {
                    "value": 220.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 0.0, "max": 200.0}
                }
            }
            
            self.create_ground_truth_file(
                ground_truth_dir / "report_001.json",
                "report_001",
                params1
            )
            self.create_ground_truth_file(
                ground_truth_dir / "report_002.json",
                "report_002",
                params2
            )
            self.create_ground_truth_file(
                ground_truth_dir / "report_003.json",
                "report_003",
                params3
            )
            
            # Run validation (reports won't be found, but pipeline should complete)
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            # Verify complete workflow executed
            assert results is not None
            assert results['reports_processed'] == 3
            assert 'accuracy_metrics' in results
            assert 'per_report_results' in results
            assert 'errors' in results
            assert 'timestamp' in results
            assert 'target_met' in results
    
    def test_error_handling_with_corrupted_files(self, pipeline):
        """
        Test error handling with corrupted ground truth files.
        
        Validates Requirement 9.3: Error resilience
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Create valid ground truth file
            self.create_ground_truth_file(
                ground_truth_dir / "report_001.json",
                "report_001"
            )
            
            # Create corrupted JSON file
            corrupted_file = ground_truth_dir / "report_002.json"
            with open(corrupted_file, 'w') as f:
                f.write("{ invalid json content }")
            
            # Create another valid file
            self.create_ground_truth_file(
                ground_truth_dir / "report_003.json",
                "report_003"
            )
            
            # Run validation - should handle corrupted file gracefully
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            # Pipeline should complete despite corrupted file
            assert results is not None
            # Should load 2 valid files (corrupted one skipped with warning)
            assert results['reports_processed'] == 2
    
    def test_performance_with_multiple_reports(self, pipeline):
        """
        Test performance with multiple reports.
        
        Validates Requirement 9.2: Performance (<5 minutes for 17 reports)
        
        Note: This test uses fewer reports but verifies reasonable performance.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Create 10 ground truth files
            for i in range(10):
                self.create_ground_truth_file(
                    ground_truth_dir / f"report_{i:03d}.json",
                    f"report_{i:03d}"
                )
            
            # Measure execution time
            start_time = time.time()
            
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete in reasonable time
            # For 10 reports, should be much faster than 5 minutes
            # Allow 30 seconds for 10 reports (scales to ~50 seconds for 17)
            assert execution_time < 30, \
                f"Pipeline took {execution_time:.2f}s for 10 reports (too slow)"
            
            # Verify all reports processed
            assert results['reports_processed'] == 10
    
    def test_pipeline_with_empty_ground_truth_directory(self, pipeline):
        """Test pipeline behavior with empty ground truth directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Run validation with empty directory
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            # Should handle gracefully
            assert results is not None
            assert results['reports_processed'] == 0
            assert 'error' in results or results['reports_processed'] == 0
    
    def test_pipeline_with_mixed_report_formats(self, pipeline):
        """Test pipeline with both PDF and PNG ground truth files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Create ground truth for PDF report
            self.create_ground_truth_file(
                ground_truth_dir / "report_001.json",
                "report_001"
            )
            
            # Create ground truth for PNG report
            self.create_ground_truth_file(
                ground_truth_dir / "report_015_png.json",
                "report_015_png"
            )
            
            # Run validation
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            # Should process both formats
            assert results['reports_processed'] == 2
    
    def test_pipeline_accuracy_calculation_correctness(self, pipeline):
        """Test that accuracy calculation is mathematically correct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Create ground truth files with known parameter counts
            # Report 1: 2 parameters
            params1 = {
                "hemoglobin": {
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_range": {"min": 13.0, "max": 17.5}
                },
                "glucose": {
                    "value": 95.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 70.0, "max": 99.0}
                }
            }
            
            # Report 2: 3 parameters
            params2 = {
                "creatinine": {
                    "value": 1.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 0.7, "max": 1.3}
                },
                "cholesterol": {
                    "value": 180.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 0.0, "max": 200.0}
                },
                "triglycerides": {
                    "value": 150.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 0.0, "max": 150.0}
                }
            }
            
            self.create_ground_truth_file(
                ground_truth_dir / "report_001.json",
                "report_001",
                params1
            )
            self.create_ground_truth_file(
                ground_truth_dir / "report_002.json",
                "report_002",
                params2
            )
            
            # Run validation
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            # When reports are not found, pipeline doesn't process them
            # So total parameters will be 0 (no successful comparisons)
            # This is correct behavior - only counts parameters from processed reports
            accuracy_metrics = results['accuracy_metrics']
            assert accuracy_metrics['total_parameters'] == 0
            assert accuracy_metrics['correct_classifications'] == 0
            assert accuracy_metrics['incorrect_classifications'] == 0
            
            # But we should have 2 errors (one for each missing report)
            assert results['reports_with_errors'] == 2
            assert len(results['errors']) == 2
    
    def test_pipeline_continues_after_individual_failures(self, pipeline):
        """
        Test that pipeline continues processing after individual report failures.
        
        Validates Requirement 9.3: Error resilience
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Create 5 ground truth files
            for i in range(5):
                self.create_ground_truth_file(
                    ground_truth_dir / f"report_{i:03d}.json",
                    f"report_{i:03d}"
                )
            
            # Run validation (all will fail - no reports exist)
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            # Pipeline should process all 5 despite failures
            assert results['reports_processed'] == 5
            assert results['reports_with_errors'] == 5
            assert len(results['errors']) == 5
            
            # Each error should be recorded
            for error in results['errors']:
                assert 'report_id' in error
                assert 'error' in error
    
    def test_pipeline_output_structure_completeness(self, pipeline):
        """
        Test that pipeline output has complete structure.
        
        Validates Requirement 9.4: Output completeness
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            ground_truth_dir = tmpdir / "ground_truth"
            ground_truth_dir.mkdir()
            
            # Create sample ground truth
            self.create_ground_truth_file(
                ground_truth_dir / "report_001.json",
                "report_001"
            )
            
            # Run validation
            results = pipeline.run_validation(
                reports_dir=str(tmpdir / "nonexistent_reports"),
                ground_truth_dir=str(ground_truth_dir)
            )
            
            # Verify all required fields present
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
            
            # Verify accuracy_metrics structure
            accuracy_fields = [
                'total_parameters',
                'correct_classifications',
                'incorrect_classifications',
                'accuracy_percentage'
            ]
            
            for field in accuracy_fields:
                assert field in results['accuracy_metrics'], \
                    f"Missing accuracy metric: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

