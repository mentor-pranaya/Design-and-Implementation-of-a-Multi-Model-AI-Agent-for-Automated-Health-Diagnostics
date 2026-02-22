"""
Unit Tests for Ground Truth Generator

Tests file I/O operations, error handling for missing reports,
and JSON formatting and structure.

Requirements: 2.1, 2.4
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.ground_truth_generator import GroundTruthGenerator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def generator():
    """Create a GroundTruthGenerator instance for testing."""
    return GroundTruthGenerator()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_report_text():
    """Sample report text for testing."""
    return """
    CLINICAL LABORATORY REPORT
    
    Patient Name: Test Patient
    Date: 15/01/2026
    
    HEMATOLOGY
    Hemoglobin: 14.5 g/dL (13.0-17.5)
    WBC: 7500 cells/µL (4000-11000)
    RBC: 4.8 million/µL (4.5-5.5)
    
    BIOCHEMISTRY
    Glucose: 95 mg/dL (70-100)
    Creatinine: 1.0 mg/dL (0.7-1.3)
    """


# ============================================================================
# File I/O Tests
# ============================================================================

class TestFileIOOperations:
    """Test file I/O operations of the ground truth generator."""
    
    def test_save_template_creates_file(self, generator, temp_dir):
        """Test that save_template creates a JSON file."""
        template = {
            "report_id": "report_001",
            "report_metadata": {
                "laboratory": "Test Lab",
                "format": "PDF",
                "date": "2026-01-15",
                "completeness": "Complete",
                "abnormality_type": "Normal"
            },
            "parameters": {
                "Hemoglobin": {
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_range": {"min": 13.0, "max": 17.5}
                }
            },
            "classifications": {"Hemoglobin": "Normal"},
            "notes": "Test template"
        }
        
        output_path = temp_dir / "test_report.json"
        generator.save_template(template, str(output_path))
        
        # Verify file was created
        assert output_path.exists(), "JSON file should be created"
        
        # Verify file is readable
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == template, "Loaded data should match original template"
    
    def test_save_template_creates_parent_directories(self, generator, temp_dir):
        """Test that save_template creates parent directories if they don't exist."""
        template = {
            "report_id": "report_001",
            "report_metadata": {},
            "parameters": {},
            "classifications": {},
            "notes": ""
        }
        
        # Use a nested path that doesn't exist
        output_path = temp_dir / "nested" / "dir" / "test_report.json"
        generator.save_template(template, str(output_path))
        
        # Verify file was created
        assert output_path.exists(), "File should be created in nested directory"
        assert output_path.parent.exists(), "Parent directories should be created"
    
    def test_save_template_formats_json_with_indentation(self, generator, temp_dir):
        """Test that save_template formats JSON with proper indentation."""
        template = {
            "report_id": "report_001",
            "report_metadata": {"laboratory": "Test Lab"},
            "parameters": {},
            "classifications": {},
            "notes": ""
        }
        
        output_path = temp_dir / "test_report.json"
        generator.save_template(template, str(output_path))
        
        # Read the raw file content
        with open(output_path, 'r') as f:
            content = f.read()
        
        # Verify it's formatted (has newlines and indentation)
        assert '\n' in content, "JSON should be formatted with newlines"
        assert '  ' in content, "JSON should have indentation"
    
    def test_save_template_overwrites_existing_file(self, generator, temp_dir):
        """Test that save_template overwrites existing files."""
        output_path = temp_dir / "test_report.json"
        
        # Create initial file
        template1 = {
            "report_id": "report_001",
            "report_metadata": {},
            "parameters": {},
            "classifications": {},
            "notes": "First version"
        }
        generator.save_template(template1, str(output_path))
        
        # Overwrite with new template
        template2 = {
            "report_id": "report_002",
            "report_metadata": {},
            "parameters": {},
            "classifications": {},
            "notes": "Second version"
        }
        generator.save_template(template2, str(output_path))
        
        # Verify the file contains the second template
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data["report_id"] == "report_002", "File should be overwritten"
        assert loaded_data["notes"] == "Second version", "Content should be updated"


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling for missing reports and invalid inputs."""
    
    def test_extract_text_from_report_raises_error_for_missing_file(self, generator):
        """Test that _extract_text_from_report raises FileNotFoundError for missing files."""
        non_existent_path = "/path/to/nonexistent/report.pdf"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            generator._extract_text_from_report(non_existent_path)
        
        assert "not found" in str(exc_info.value).lower(), \
            "Error message should indicate file not found"
    
    def test_extract_text_from_report_raises_error_for_unsupported_format(self, generator, temp_dir):
        """Test that _extract_text_from_report raises ValueError for unsupported file formats."""
        # Create a file with unsupported extension
        unsupported_file = temp_dir / "report.txt"
        unsupported_file.write_text("Some text")
        
        with pytest.raises(ValueError) as exc_info:
            generator._extract_text_from_report(str(unsupported_file))
        
        assert "unsupported" in str(exc_info.value).lower(), \
            "Error message should indicate unsupported format"
    
    def test_generate_all_templates_continues_on_individual_failures(self, generator, temp_dir):
        """Test that generate_all_templates continues processing when individual reports fail."""
        # Create a mix of valid and invalid files
        reports_dir = temp_dir / "reports"
        reports_dir.mkdir()
        
        # Create a corrupted PDF file (will fail during extraction)
        # Note: generate_all_templates only processes .pdf and .png files
        corrupted_pdf = reports_dir / "corrupted.pdf"
        corrupted_pdf.write_bytes(b"Not a valid PDF content")
        
        output_dir = temp_dir / "output"
        
        # Run generation
        summary = generator.generate_all_templates(
            str(reports_dir),
            str(output_dir)
        )
        
        # Verify summary shows the failure
        assert summary["total_reports"] == 1, "Should count the corrupted PDF file"
        assert summary["failed"] == 1, "Should mark the corrupted file as failed"
        assert summary["successful"] == 0, "Should have no successful generations"
        assert len(summary["errors"]) > 0, "Should record the error"
    
    def test_generate_all_templates_handles_empty_directory(self, generator, temp_dir):
        """Test that generate_all_templates handles empty directories gracefully."""
        reports_dir = temp_dir / "empty_reports"
        reports_dir.mkdir()
        
        output_dir = temp_dir / "output"
        
        # Run generation on empty directory
        summary = generator.generate_all_templates(
            str(reports_dir),
            str(output_dir)
        )
        
        # Verify summary reflects empty directory
        assert summary["total_reports"] == 0, "Should find no reports"
        assert summary["successful"] == 0, "Should have no successful generations"
        assert summary["failed"] == 0, "Should have no failures"
    
    def test_validate_template_returns_errors_for_invalid_template(self, generator):
        """Test that validate_template returns appropriate errors for invalid templates."""
        invalid_template = {
            "report_id": "report_001",
            # Missing: report_metadata, parameters, classifications
        }
        
        is_valid, errors = generator.validate_template(invalid_template)
        
        assert not is_valid, "Invalid template should not be valid"
        assert len(errors) > 0, "Should return validation errors"
        assert any("report_metadata" in error for error in errors), \
            "Should report missing report_metadata"


# ============================================================================
# JSON Formatting and Structure Tests
# ============================================================================

class TestJSONFormattingAndStructure:
    """Test JSON formatting and structure of generated templates."""
    
    def test_generate_report_id_formats_pdf_correctly(self, generator):
        """Test that _generate_report_id formats PDF report IDs correctly."""
        pdf_path = "/path/to/test report (5).pdf"
        report_id = generator._generate_report_id(pdf_path)
        
        assert report_id == "report_005", \
            f"Expected 'report_005', got '{report_id}'"
    
    def test_generate_report_id_formats_png_correctly(self, generator):
        """Test that _generate_report_id formats PNG report IDs correctly."""
        png_path = "/path/to/test report (15).png"
        report_id = generator._generate_report_id(png_path)
        
        assert report_id == "report_015_png", \
            f"Expected 'report_015_png', got '{report_id}'"
    
    def test_generate_report_id_handles_missing_number(self, generator):
        """Test that _generate_report_id handles filenames without numbers."""
        path = "/path/to/report_without_number.pdf"
        report_id = generator._generate_report_id(path)
        
        # Should use filename as fallback
        assert report_id == "report_without_number", \
            f"Expected 'report_without_number', got '{report_id}'"
    
    def test_generate_output_filename_adds_json_extension(self, generator):
        """Test that _generate_output_filename adds .json extension."""
        report_id = "report_001"
        filename = generator._generate_output_filename(report_id)
        
        assert filename == "report_001.json", \
            f"Expected 'report_001.json', got '{filename}'"
        assert filename.endswith('.json'), "Filename should end with .json"
    
    def test_determine_report_format_identifies_pdf(self, generator):
        """Test that _determine_report_format correctly identifies PDF files."""
        pdf_path = "/path/to/report.pdf"
        format_type = generator._determine_report_format(pdf_path)
        
        assert format_type == "PDF", f"Expected 'PDF', got '{format_type}'"
    
    def test_determine_report_format_identifies_png(self, generator):
        """Test that _determine_report_format correctly identifies PNG files."""
        png_path = "/path/to/report.png"
        format_type = generator._determine_report_format(png_path)
        
        assert format_type == "PNG", f"Expected 'PNG', got '{format_type}'"
    
    def test_determine_report_format_handles_case_insensitive(self, generator):
        """Test that _determine_report_format handles case-insensitive extensions."""
        pdf_upper = "/path/to/report.PDF"
        png_upper = "/path/to/report.PNG"
        
        assert generator._determine_report_format(pdf_upper) == "PDF"
        assert generator._determine_report_format(png_upper) == "PNG"
    
    def test_normalize_parameter_name_handles_acronyms(self, generator):
        """Test that _normalize_parameter_name correctly handles common acronyms."""
        test_cases = {
            'wbc': 'WBC',
            'rbc': 'RBC',
            'hdl': 'HDL',
            'ldl': 'LDL',
            'tsh': 'TSH',
            'hba1c': 'HbA1c',
        }
        
        for input_name, expected_output in test_cases.items():
            result = generator._normalize_parameter_name(input_name)
            assert result == expected_output, \
                f"Expected '{expected_output}' for '{input_name}', got '{result}'"
    
    def test_normalize_parameter_name_capitalizes_regular_names(self, generator):
        """Test that _normalize_parameter_name capitalizes regular parameter names."""
        test_cases = {
            'hemoglobin': 'Hemoglobin',
            'glucose': 'Glucose',
            'creatinine': 'Creatinine',
            'albumin': 'Albumin',
        }
        
        for input_name, expected_output in test_cases.items():
            result = generator._normalize_parameter_name(input_name)
            assert result == expected_output, \
                f"Expected '{expected_output}' for '{input_name}', got '{result}'"
    
    def test_classify_parameter_returns_low_for_below_range(self, generator):
        """Test that _classify_parameter returns 'Low' for values below range."""
        ref_range = {"min": 13.0, "max": 17.5}
        classification = generator._classify_parameter("Hemoglobin", 12.0, ref_range)
        
        assert classification == "Low", \
            f"Expected 'Low' for value below range, got '{classification}'"
    
    def test_classify_parameter_returns_high_for_above_range(self, generator):
        """Test that _classify_parameter returns 'High' for values above range."""
        ref_range = {"min": 13.0, "max": 17.5}
        classification = generator._classify_parameter("Hemoglobin", 18.0, ref_range)
        
        assert classification == "High", \
            f"Expected 'High' for value above range, got '{classification}'"
    
    def test_classify_parameter_returns_normal_for_within_range(self, generator):
        """Test that _classify_parameter returns 'Normal' for values within range."""
        ref_range = {"min": 13.0, "max": 17.5}
        classification = generator._classify_parameter("Hemoglobin", 15.0, ref_range)
        
        assert classification == "Normal", \
            f"Expected 'Normal' for value within range, got '{classification}'"
    
    def test_classify_parameter_returns_unknown_for_missing_range(self, generator):
        """Test that _classify_parameter returns 'Unknown' when reference range is unavailable."""
        ref_range = {"min": None, "max": None}
        classification = generator._classify_parameter("Hemoglobin", 15.0, ref_range)
        
        assert classification == "Unknown", \
            f"Expected 'Unknown' for missing range, got '{classification}'"
    
    def test_classify_parameter_handles_boundary_values(self, generator):
        """Test that _classify_parameter correctly handles boundary values."""
        ref_range = {"min": 13.0, "max": 17.5}
        
        # Test exact min value
        classification_min = generator._classify_parameter("Hemoglobin", 13.0, ref_range)
        assert classification_min == "Normal", \
            "Value at min boundary should be Normal"
        
        # Test exact max value
        classification_max = generator._classify_parameter("Hemoglobin", 17.5, ref_range)
        assert classification_max == "Normal", \
            "Value at max boundary should be Normal"
    
    def test_extract_report_metadata_includes_required_fields(self, generator, sample_report_text):
        """Test that _extract_report_metadata includes all required metadata fields."""
        metadata = generator._extract_report_metadata(sample_report_text, "test_report.pdf")
        
        required_fields = ['laboratory', 'format', 'date', 'completeness', 'abnormality_type']
        for field in required_fields:
            assert field in metadata, f"Metadata missing required field: {field}"
    
    def test_extract_report_metadata_sets_verified_false_by_default(self, generator, sample_report_text):
        """Test that _extract_report_metadata sets verified to False by default."""
        metadata = generator._extract_report_metadata(sample_report_text, "test_report.pdf")
        
        assert metadata.get('verified') == False, \
            "Metadata should have verified=False by default"
        assert metadata.get('verified_by') == "", \
            "Metadata should have empty verified_by by default"
        assert metadata.get('verified_date') == "", \
            "Metadata should have empty verified_date by default"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the complete ground truth generation workflow."""
    
    def test_validate_template_accepts_complete_valid_template(self, generator):
        """Test that validate_template accepts a complete, valid template."""
        valid_template = {
            "report_id": "report_001",
            "report_metadata": {
                "laboratory": "Test Lab",
                "format": "PDF",
                "date": "2026-01-15",
                "completeness": "Complete",
                "abnormality_type": "Normal"
            },
            "parameters": {
                "Hemoglobin": {
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_range": {"min": 13.0, "max": 17.5}
                },
                "Glucose": {
                    "value": 95.0,
                    "unit": "mg/dL",
                    "reference_range": {"min": 70.0, "max": 100.0}
                }
            },
            "classifications": {
                "Hemoglobin": "Normal",
                "Glucose": "Normal"
            },
            "notes": "Test template"
        }
        
        is_valid, errors = generator.validate_template(valid_template)
        
        assert is_valid, f"Valid template should pass validation, errors: {errors}"
        assert len(errors) == 0, "Valid template should have no errors"
    
    def test_save_and_load_template_preserves_data(self, generator, temp_dir):
        """Test that saving and loading a template preserves all data."""
        original_template = {
            "report_id": "report_001",
            "report_metadata": {
                "laboratory": "Test Lab",
                "format": "PDF",
                "date": "2026-01-15",
                "completeness": "Complete",
                "abnormality_type": "Normal"
            },
            "parameters": {
                "Hemoglobin": {
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_range": {"min": 13.0, "max": 17.5}
                }
            },
            "classifications": {"Hemoglobin": "Normal"},
            "notes": "Test template"
        }
        
        # Save template
        output_path = temp_dir / "test_report.json"
        generator.save_template(original_template, str(output_path))
        
        # Load template
        with open(output_path, 'r') as f:
            loaded_template = json.load(f)
        
        # Verify all data is preserved
        assert loaded_template == original_template, \
            "Loaded template should match original"
        assert loaded_template["report_id"] == original_template["report_id"]
        assert loaded_template["parameters"] == original_template["parameters"]
        assert loaded_template["classifications"] == original_template["classifications"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

