"""
Unit tests for run_validation.py

Tests the main validation pipeline orchestration script.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.run_validation import ValidationRunner


class TestValidationRunner:
    """Test suite for ValidationRunner class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_base = tempfile.mkdtemp()
        temp_path = Path(temp_base)
        
        reports_dir = temp_path / 'reports'
        ground_truth_dir = temp_path / 'ground_truth'
        output_dir = temp_path / 'output'
        
        reports_dir.mkdir()
        ground_truth_dir.mkdir()
        output_dir.mkdir()
        
        yield {
            'reports': reports_dir,
            'ground_truth': ground_truth_dir,
            'output': output_dir
        }
        
        # Cleanup
        shutil.rmtree(temp_base)
    
    @pytest.fixture
    def runner(self, temp_dirs):
        """Create a ValidationRunner instance with temp directories."""
        return ValidationRunner(
            reports_dir=str(temp_dirs['reports']),
            ground_truth_dir=str(temp_dirs['ground_truth']),
            output_dir=str(temp_dirs['output']),
            verbose=False
        )
    
    def test_initialization(self, temp_dirs):
        """Test ValidationRunner initialization."""
        runner = ValidationRunner(
            reports_dir=str(temp_dirs['reports']),
            ground_truth_dir=str(temp_dirs['ground_truth']),
            output_dir=str(temp_dirs['output']),
            verbose=True
        )
        
        assert runner.reports_dir == temp_dirs['reports']
        assert runner.ground_truth_dir == temp_dirs['ground_truth']
        assert runner.output_dir == temp_dirs['output']
        assert runner.verbose is True
        assert runner.output_dir.exists()
    
    def test_output_directory_creation(self, temp_dirs):
        """Test that output directory is created if it doesn't exist."""
        output_dir = temp_dirs['output'] / 'nested' / 'dir'
        
        runner = ValidationRunner(
            reports_dir=str(temp_dirs['reports']),
            ground_truth_dir=str(temp_dirs['ground_truth']),
            output_dir=str(output_dir),
            verbose=False
        )
        
        assert output_dir.exists()
    
    def test_check_ground_truth_changes_first_run(self, runner, temp_dirs):
        """Test ground truth change detection on first run (no previous validation)."""
        # First run should return False (no previous validation to compare)
        changes = runner._check_ground_truth_changes()
        assert changes is False
    
    def test_check_ground_truth_changes_no_changes(self, runner, temp_dirs):
        """Test ground truth change detection when no changes occurred."""
        # Create a ground truth file
        gt_file = temp_dirs['ground_truth'] / 'report_001.json'
        gt_file.write_text('{"report_id": "report_001"}')
        
        # Save initial timestamp
        runner._save_validation_timestamp()
        
        # Check for changes (should be False since nothing changed)
        changes = runner._check_ground_truth_changes()
        assert changes is False
    
    def test_check_ground_truth_changes_with_changes(self, runner, temp_dirs):
        """Test ground truth change detection when files have changed."""
        # Create a ground truth file
        gt_file = temp_dirs['ground_truth'] / 'report_001.json'
        gt_file.write_text('{"report_id": "report_001"}')
        
        # Save initial timestamp
        runner._save_validation_timestamp()
        
        # Modify the file
        import time
        time.sleep(0.1)  # Ensure timestamp difference
        gt_file.write_text('{"report_id": "report_001", "modified": true}')
        
        # Check for changes (should be True)
        changes = runner._check_ground_truth_changes()
        assert changes is True
    
    def test_check_ground_truth_changes_new_file(self, runner, temp_dirs):
        """Test ground truth change detection when new file is added."""
        # Create initial file
        gt_file1 = temp_dirs['ground_truth'] / 'report_001.json'
        gt_file1.write_text('{"report_id": "report_001"}')
        
        # Save initial timestamp
        runner._save_validation_timestamp()
        
        # Add new file
        gt_file2 = temp_dirs['ground_truth'] / 'report_002.json'
        gt_file2.write_text('{"report_id": "report_002"}')
        
        # Check for changes (should be True)
        changes = runner._check_ground_truth_changes()
        assert changes is True
    
    def test_check_ground_truth_changes_ignores_template(self, runner, temp_dirs):
        """Test that TEMPLATE.json is ignored in change detection."""
        # Create TEMPLATE.json
        template_file = temp_dirs['ground_truth'] / 'TEMPLATE.json'
        template_file.write_text('{"_instructions": "template"}')
        
        # Save initial timestamp
        runner._save_validation_timestamp()
        
        # Modify template
        import time
        time.sleep(0.1)
        template_file.write_text('{"_instructions": "modified template"}')
        
        # Check for changes (should be False since TEMPLATE is ignored)
        changes = runner._check_ground_truth_changes()
        assert changes is False
    
    def test_save_validation_timestamp(self, runner, temp_dirs):
        """Test saving validation timestamp."""
        # Create some ground truth files
        gt_file1 = temp_dirs['ground_truth'] / 'report_001.json'
        gt_file1.write_text('{"report_id": "report_001"}')
        
        gt_file2 = temp_dirs['ground_truth'] / 'report_002.json'
        gt_file2.write_text('{"report_id": "report_002"}')
        
        # Save timestamp
        runner._save_validation_timestamp()
        
        # Check that timestamp file was created
        timestamp_file = temp_dirs['output'] / 'last_validation_timestamp.json'
        assert timestamp_file.exists()
        
        # Load and verify content
        with open(timestamp_file, 'r') as f:
            data = json.load(f)
        
        assert 'timestamp' in data
        assert 'ground_truth_files' in data
        assert 'report_001.json' in data['ground_truth_files']
        assert 'report_002.json' in data['ground_truth_files']
        
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data['timestamp'])
    
    def test_run_validation_success(self, temp_dirs):
        """Test successful validation run."""
        # Create a runner with mocked components
        runner = ValidationRunner(
            reports_dir=str(temp_dirs['reports']),
            ground_truth_dir=str(temp_dirs['ground_truth']),
            output_dir=str(temp_dirs['output']),
            verbose=False
        )
        
        # Mock validation results
        mock_validation_results = {
            'timestamp': datetime.now().isoformat(),
            'reports_processed': 17,
            'reports_with_errors': 0,
            'accuracy_metrics': {
                'total_parameters': 255,
                'correct_classifications': 251,
                'incorrect_classifications': 4,
                'accuracy_percentage': 98.43,
                'all_mismatches': []
            },
            'per_report_results': [],
            'errors': [],
            'target_met': True
        }
        
        # Mock the pipeline's run_validation method
        runner.pipeline.run_validation = Mock(return_value=mock_validation_results)
        
        # Mock error analyzer
        runner.error_analyzer.analyze_errors = Mock(return_value={
            'total_errors': 0,
            'by_category': {},
            'category_summary': {},
            'systematic_errors': [],
            'edge_cases': [],
            'recommendations': []
        })
        
        # Mock report generator
        runner.report_generator.generate_validation_report = Mock(return_value="# Report")
        runner.report_generator.generate_certification = Mock(return_value="# Certification")
        runner.report_generator.save_report = Mock()
        
        # Run validation
        results = runner.run_validation()
        
        # Verify results
        assert results['success'] is True
        assert results['target_met'] is True
        assert 'validation_results' in results
        assert 'elapsed_time' in results
        
        # Verify pipeline was called
        runner.pipeline.run_validation.assert_called_once()
        
        # Verify reports were generated
        runner.report_generator.generate_validation_report.assert_called_once()
        runner.report_generator.generate_certification.assert_called_once()
    
    def test_run_validation_pipeline_failure(self, temp_dirs):
        """Test validation run when pipeline fails."""
        # Create runner
        runner = ValidationRunner(
            reports_dir=str(temp_dirs['reports']),
            ground_truth_dir=str(temp_dirs['ground_truth']),
            output_dir=str(temp_dirs['output']),
            verbose=False
        )
        
        # Configure mock to raise exception
        runner.pipeline.run_validation = Mock(side_effect=Exception("Pipeline error"))
        
        # Run validation
        results = runner.run_validation()
        
        # Verify error handling
        assert results['success'] is False
        assert 'error' in results
        assert 'Pipeline error' in results['error']
    
    def test_run_validation_with_errors(self, temp_dirs):
        """Test validation run with classification errors."""
        # Create runner
        runner = ValidationRunner(
            reports_dir=str(temp_dirs['reports']),
            ground_truth_dir=str(temp_dirs['ground_truth']),
            output_dir=str(temp_dirs['output']),
            verbose=False
        )
        
        # Mock validation results with errors
        mock_validation_results = {
            'timestamp': datetime.now().isoformat(),
            'reports_processed': 17,
            'reports_with_errors': 0,
            'accuracy_metrics': {
                'total_parameters': 255,
                'correct_classifications': 245,
                'incorrect_classifications': 10,
                'accuracy_percentage': 96.08,
                'all_mismatches': [
                    {
                        'parameter': 'glucose',
                        'system_classification': 'High',
                        'ground_truth_classification': 'Normal'
                    }
                ]
            },
            'per_report_results': [],
            'errors': [],
            'target_met': False
        }
        
        # Configure mocks
        runner.pipeline.run_validation = Mock(return_value=mock_validation_results)
        
        runner.error_analyzer.analyze_errors = Mock(return_value={
            'total_errors': 10,
            'by_category': {'edge_case': []},
            'category_summary': {'edge_case': 10},
            'systematic_errors': [],
            'edge_cases': [],
            'recommendations': ['Review edge cases']
        })
        runner.error_analyzer.generate_error_report = Mock(return_value="# Error Report")
        
        runner.report_generator.generate_validation_report = Mock(return_value="# Report")
        runner.report_generator.save_report = Mock()
        
        # Run validation
        results = runner.run_validation()
        
        # Verify results
        assert results['success'] is True
        assert results['target_met'] is False
        
        # Verify error analysis was performed
        runner.error_analyzer.analyze_errors.assert_called_once()
        runner.error_analyzer.generate_error_report.assert_called_once()
        
        # Verify certification was NOT generated (target not met)
        assert not hasattr(runner.report_generator.generate_certification, 'called') or \
               runner.report_generator.generate_certification.call_count == 0
    
    def test_run_validation_saves_results(self, temp_dirs):
        """Test that validation results are saved to JSON file."""
        # Create runner
        runner = ValidationRunner(
            reports_dir=str(temp_dirs['reports']),
            ground_truth_dir=str(temp_dirs['ground_truth']),
            output_dir=str(temp_dirs['output']),
            verbose=False
        )
        
        # Mock validation results
        mock_validation_results = {
            'timestamp': datetime.now().isoformat(),
            'reports_processed': 17,
            'target_met': True,
            'accuracy_metrics': {
                'accuracy_percentage': 98.5,
                'all_mismatches': []
            }
        }
        
        # Configure mocks
        runner.pipeline.run_validation = Mock(return_value=mock_validation_results)
        runner.report_generator.generate_validation_report = Mock(return_value="# Report")
        runner.report_generator.generate_certification = Mock(return_value="# Cert")
        runner.report_generator.save_report = Mock()
        
        # Run validation
        runner.run_validation()
        
        # Verify JSON results file was created
        results_file = temp_dirs['output'] / 'validation_results.json'
        assert results_file.exists()
        
        # Verify content
        with open(results_file, 'r') as f:
            saved_results = json.load(f)
        
        assert saved_results['reports_processed'] == 17
        assert saved_results['target_met'] is True
    
    def test_print_header(self, runner, capsys):
        """Test header printing."""
        runner._print_header("TEST HEADER")
        captured = capsys.readouterr()
        
        assert "TEST HEADER" in captured.out
        assert "=" in captured.out
    
    def test_print_progress(self, runner, capsys):
        """Test progress message printing."""
        runner._print_progress("Test message")
        captured = capsys.readouterr()
        
        assert "Test message" in captured.out
        assert "[" in captured.out  # Timestamp bracket


class TestValidationRunnerIntegration:
    """Integration tests for ValidationRunner with real components."""
    
    @pytest.fixture
    def integration_dirs(self):
        """Use actual project directories for integration testing."""
        return {
            'reports': Path('data/test_reports'),
            'ground_truth': Path('evaluation/test_dataset/ground_truth'),
            'output': Path('evaluation/test_results_integration')
        }
    
    @pytest.fixture
    def integration_runner(self, integration_dirs):
        """Create runner with real directories."""
        # Create output dir
        integration_dirs['output'].mkdir(parents=True, exist_ok=True)
        
        runner = ValidationRunner(
            reports_dir=str(integration_dirs['reports']),
            ground_truth_dir=str(integration_dirs['ground_truth']),
            output_dir=str(integration_dirs['output']),
            verbose=False
        )
        
        yield runner
        
        # Cleanup
        if integration_dirs['output'].exists():
            shutil.rmtree(integration_dirs['output'])
    
    @pytest.mark.skipif(
        not Path('data/test_reports').exists() or 
        not Path('evaluation/test_dataset/ground_truth').exists(),
        reason="Test data not available"
    )
    def test_integration_validation_run(self, integration_runner):
        """
        Integration test: Run validation with real data.
        
        This test requires actual test reports and ground truth files.
        """
        # Run validation
        results = integration_runner.run_validation()
        
        # Verify basic structure
        assert 'success' in results
        assert 'validation_results' in results or 'error' in results
        
        # If successful, verify output files were created
        if results.get('success'):
            output_dir = Path('evaluation/test_results_integration')
            
            # Check for validation report
            validation_report = output_dir / 'MILESTONE_1_VALIDATION_REPORT.md'
            assert validation_report.exists()
            
            # Check for results JSON
            results_json = output_dir / 'validation_results.json'
            assert results_json.exists()
            
            # If target met, check for certification
            if results.get('target_met'):
                certification = output_dir / 'MILESTONE_1_CERTIFICATION.md'
                assert certification.exists()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

