"""
Unit tests for ValidationPipeline module.

Tests core functionality including ground truth loading, parameter matching,
classification comparison, and accuracy calculation.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.validation_pipeline import ValidationPipeline


class TestValidationPipeline:
    """Test suite for ValidationPipeline class."""
    
    @pytest.fixture
    def pipeline(self):
        """Create a ValidationPipeline instance for testing."""
        return ValidationPipeline()
    
    @pytest.fixture
    def sample_ground_truth(self):
        """Sample ground truth data for testing."""
        return {
            "report_id": "report_001",
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
                    "reference_range": {
                        "min": 13.0,
                        "max": 17.5
                    }
                },
                "glucose": {
                    "value": 110,
                    "unit": "mg/dL",
                    "reference_range": {
                        "min": 70,
                        "max": 99
                    }
                }
            },
            "classifications": {
                "hemoglobin": "Normal",
                "glucose": "High"
            }
        }
    
    @pytest.fixture
    def sample_system_output(self):
        """Sample system output for testing."""
        return {
            "parameters": {
                "hemoglobin": {
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_range": {
                        "min": 13.0,
                        "max": 17.5
                    }
                },
                "glucose": {
                    "value": 110,
                    "unit": "mg/dL",
                    "reference_range": {
                        "min": 70,
                        "max": 99
                    }
                }
            },
            "classifications": {
                "hemoglobin": "Normal",
                "glucose": "High"
            }
        }
    
    def test_load_ground_truth_success(self, pipeline):
        """Test loading ground truth files from directory."""
        # Create temporary directory with ground truth files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create sample ground truth files
            gt1 = {
                "report_id": "report_001",
                "parameters": {"hemoglobin": {"value": 14.5, "unit": "g/dL", "reference_range": {"min": 13.0, "max": 17.5}}},
                "classifications": {"hemoglobin": "Normal"}
            }
            gt2 = {
                "report_id": "report_002",
                "parameters": {"glucose": {"value": 110, "unit": "mg/dL", "reference_range": {"min": 70, "max": 99}}},
                "classifications": {"glucose": "High"}
            }
            
            with open(tmpdir / "report_001.json", 'w') as f:
                json.dump(gt1, f)
            with open(tmpdir / "report_002.json", 'w') as f:
                json.dump(gt2, f)
            
            # Load ground truth
            result = pipeline.load_ground_truth(str(tmpdir))
            
            # Verify
            assert len(result) == 2
            assert "report_001" in result
            assert "report_002" in result
            assert result["report_001"]["classifications"]["hemoglobin"] == "Normal"
            assert result["report_002"]["classifications"]["glucose"] == "High"
    
    def test_load_ground_truth_filters_template(self, pipeline):
        """Test that TEMPLATE.json is filtered out when loading ground truth."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create TEMPLATE.json (should be filtered)
            template = {
                "_instructions": "This is a template",
                "report_id": "template"
            }
            with open(tmpdir / "TEMPLATE.json", 'w') as f:
                json.dump(template, f)
            
            # Create actual ground truth
            gt1 = {
                "report_id": "report_001",
                "parameters": {},
                "classifications": {}
            }
            with open(tmpdir / "report_001.json", 'w') as f:
                json.dump(gt1, f)
            
            # Load ground truth
            result = pipeline.load_ground_truth(str(tmpdir))
            
            # Verify TEMPLATE is not loaded
            assert len(result) == 1
            assert "template" not in result
            assert "report_001" in result
    
    def test_normalize_parameter_name(self, pipeline):
        """Test parameter name normalization."""
        assert pipeline._normalize_parameter_name("Hemoglobin") == "Hemoglobin"
        assert pipeline._normalize_parameter_name("WBC") == "WBC"
        assert pipeline._normalize_parameter_name("White Blood Cells") == "WBC"
        assert pipeline._normalize_parameter_name("Glucose") == "Glucose"
        assert pipeline._normalize_parameter_name("Blood Glucose") == "Glucose"

    def test_compare_classifications_all_match(self, pipeline, sample_system_output, sample_ground_truth):
        """Test comparison when all classifications match."""
        result = pipeline.compare_classifications(sample_system_output, sample_ground_truth)
        
        # All should match
        assert result['correct'] == 2
        assert result['incorrect'] == 0
        assert len(result['matches']) == 2
        assert len(result['mismatches']) == 0
        assert len(result['missing_in_system']) == 0
        assert len(result['extra_in_system']) == 0
    
    def test_compare_classifications_with_mismatch(self, pipeline, sample_system_output, sample_ground_truth):
        """Test comparison when there's a classification mismatch."""
        # Change system output to have wrong classification
        sample_system_output['classifications']['glucose'] = "Normal"  # Should be High
        
        result = pipeline.compare_classifications(sample_system_output, sample_ground_truth)
        
        # One match, one mismatch
        assert result['correct'] == 1
        assert result['incorrect'] == 1
        assert len(result['matches']) == 1
        assert len(result['mismatches']) == 1
        
        # Check mismatch details
        mismatch = result['mismatches'][0]
        assert mismatch['parameter'] == 'glucose'
        assert mismatch['system_classification'] == 'Normal'
        assert mismatch['ground_truth_classification'] == 'High'
    
    def test_compare_classifications_missing_parameter(self, pipeline, sample_system_output, sample_ground_truth):
        """Test comparison when system is missing a parameter."""
        # Remove glucose from system output
        del sample_system_output['parameters']['glucose']
        del sample_system_output['classifications']['glucose']
        
        result = pipeline.compare_classifications(sample_system_output, sample_ground_truth)
        
        # One match, one missing
        assert result['correct'] == 1
        assert result['incorrect'] == 0
        assert len(result['matches']) == 1
        assert len(result['missing_in_system']) == 1
        
        # Check missing parameter
        missing = result['missing_in_system'][0]
        assert missing['parameter'] == 'glucose'
        assert missing['classification'] == 'High'
    
    def test_compare_classifications_extra_parameter(self, pipeline, sample_system_output, sample_ground_truth):
        """Test comparison when system has extra parameter."""
        # Add extra parameter to system output
        sample_system_output['parameters']['creatinine'] = {
            "value": 1.1,
            "unit": "mg/dL",
            "reference_range": {"min": 0.7, "max": 1.3}
        }
        sample_system_output['classifications']['creatinine'] = "Normal"
        
        result = pipeline.compare_classifications(sample_system_output, sample_ground_truth)
        
        # Two matches, one extra
        assert result['correct'] == 2
        assert result['incorrect'] == 0
        assert len(result['matches']) == 2
        assert len(result['extra_in_system']) == 1
        
        # Check extra parameter
        extra = result['extra_in_system'][0]
        assert extra['parameter'] == 'creatinine'
        assert extra['classification'] == 'Normal'
    
    def test_calculate_accuracy_perfect(self, pipeline):
        """Test accuracy calculation with 100% accuracy."""
        comparisons = [
            {
                'total_ground_truth': 5,
                'correct': 5,
                'incorrect': 0,
                'mismatches': [],
                'missing_in_system': [],
                'extra_in_system': []
            },
            {
                'total_ground_truth': 3,
                'correct': 3,
                'incorrect': 0,
                'mismatches': [],
                'missing_in_system': [],
                'extra_in_system': []
            }
        ]
        
        result = pipeline.calculate_accuracy(comparisons)
        
        assert result['total_parameters'] == 8
        assert result['correct_classifications'] == 8
        assert result['incorrect_classifications'] == 0
        assert result['accuracy_percentage'] == 100.0
    
    def test_calculate_accuracy_with_errors(self, pipeline):
        """Test accuracy calculation with some errors."""
        comparisons = [
            {
                'total_ground_truth': 10,
                'correct': 9,
                'incorrect': 1,
                'mismatches': [{'parameter': 'glucose'}],
                'missing_in_system': [],
                'extra_in_system': []
            },
            {
                'total_ground_truth': 10,
                'correct': 10,
                'incorrect': 0,
                'mismatches': [],
                'missing_in_system': [],
                'extra_in_system': []
            }
        ]
        
        result = pipeline.calculate_accuracy(comparisons)
        
        assert result['total_parameters'] == 20
        assert result['correct_classifications'] == 19
        assert result['incorrect_classifications'] == 1
        assert result['accuracy_percentage'] == 95.0
        assert len(result['all_mismatches']) == 1
    
    def test_calculate_accuracy_empty(self, pipeline):
        """Test accuracy calculation with no data."""
        comparisons = []
        
        result = pipeline.calculate_accuracy(comparisons)
        
        assert result['total_parameters'] == 0
        assert result['correct_classifications'] == 0
        assert result['incorrect_classifications'] == 0
        assert result['accuracy_percentage'] == 0.0
    
    def test_find_report_file_pdf(self, pipeline):
        """Test finding PDF report file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test report file
            report_file = tmpdir / "test report (5).pdf"
            report_file.touch()
            
            # Find it
            result = pipeline._find_report_file(tmpdir, "report_005")
            
            assert result is not None
            assert result.name == "test report (5).pdf"
    
    def test_find_report_file_png(self, pipeline):
        """Test finding PNG report file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test report file
            report_file = tmpdir / "test report (15).png"
            report_file.touch()
            
            # Find it
            result = pipeline._find_report_file(tmpdir, "report_015_png")
            
            assert result is not None
            assert result.name == "test report (15).png"
    
    def test_find_report_file_not_found(self, pipeline):
        """Test when report file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Try to find non-existent file
            result = pipeline._find_report_file(tmpdir, "report_999")
            
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

