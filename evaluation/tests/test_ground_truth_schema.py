"""
Property-Based Tests for Ground Truth Schema Compliance

Feature: milestone-1-validation
Property 1: Ground Truth Schema Compliance
Validates: Requirements 1.1, 1.2, 2.4

Tests that any generated ground truth JSON file conforms to the template schema
with all required fields (report_id, report_metadata, parameters, classifications, notes).
"""

import json
import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.ground_truth_generator import GroundTruthGenerator


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

@st.composite
def parameter_data_strategy(draw):
    """Generate valid parameter data with value, unit, and reference range."""
    value = draw(st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False))
    unit = draw(st.sampled_from(['g/dL', 'mg/dL', 'cells/µL', 'mmol/L', 'U/L', '%', 'ng/mL']))
    
    # Generate reference range with min < max
    min_val = draw(st.floats(min_value=0.0, max_value=value * 0.8, allow_nan=False, allow_infinity=False))
    max_val = draw(st.floats(min_value=value * 1.2, max_value=2000.0, allow_nan=False, allow_infinity=False))
    
    return {
        "value": round(value, 2),
        "unit": unit,
        "reference_range": {
            "min": round(min_val, 2),
            "max": round(max_val, 2)
        }
    }


@st.composite
def report_metadata_strategy(draw):
    """Generate valid report metadata."""
    from datetime import date
    return {
        "laboratory": draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' &'))),
        "format": draw(st.sampled_from(['PDF', 'PNG', 'Scanned', 'Digital'])),
        "date": draw(st.dates().map(lambda d: d.strftime("%Y-%m-%d"))),
        "completeness": draw(st.sampled_from(['Complete', 'Partial'])),
        "abnormality_type": draw(st.sampled_from(['Normal', 'Single', 'Multiple', 'Edge Case']))
    }


@st.composite
def ground_truth_template_strategy(draw):
    """
    Generate a complete ground truth template matching the schema.
    
    This strategy creates valid ground truth data structures that should
    pass schema validation.
    """
    # Generate report ID
    report_num = draw(st.integers(min_value=1, max_value=999))
    is_png = draw(st.booleans())
    report_id = f"report_{report_num:03d}" + ("_png" if is_png else "")
    
    # Generate metadata
    metadata = draw(report_metadata_strategy())
    
    # Generate 1-18 parameters (we have 18 unique parameter names)
    num_params = draw(st.integers(min_value=1, max_value=18))
    param_names = draw(st.lists(
        st.sampled_from([
            'Hemoglobin', 'WBC', 'RBC', 'Platelets', 'Glucose', 'Creatinine',
            'Cholesterol', 'Triglycerides', 'ALT', 'AST', 'Bilirubin',
            'Albumin', 'TSH', 'T3', 'T4', 'Sodium', 'Potassium', 'Calcium'
        ]),
        min_size=num_params,
        max_size=num_params,
        unique=True
    ))
    
    # Generate parameters
    parameters = {}
    classifications = {}
    
    for param_name in param_names:
        param_data = draw(parameter_data_strategy())
        parameters[param_name] = param_data
        
        # Classify based on reference range
        value = param_data['value']
        min_val = param_data['reference_range']['min']
        max_val = param_data['reference_range']['max']
        
        if value < min_val:
            classification = 'Low'
        elif value > max_val:
            classification = 'High'
        else:
            classification = 'Normal'
        
        classifications[param_name] = classification
    
    # Generate notes
    notes = draw(st.text(min_size=0, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
    
    return {
        "report_id": report_id,
        "report_metadata": metadata,
        "parameters": parameters,
        "classifications": classifications,
        "notes": notes
    }


# ============================================================================
# Property Tests
# ============================================================================

class TestGroundTruthSchemaCompliance:
    """
    Property 1: Ground Truth Schema Compliance
    
    **Validates: Requirements 1.1, 1.2, 2.4**
    
    For any generated ground truth JSON file, it should conform to the template
    schema with all required fields (report_id, report_metadata, parameters,
    classifications, notes).
    """
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_ground_truth_has_all_required_top_level_fields(self, template):
        """
        Property: All ground truth templates must have required top-level fields.
        
        Required fields: report_id, report_metadata, parameters, classifications, notes
        """
        required_fields = ['report_id', 'report_metadata', 'parameters', 'classifications', 'notes']
        
        for field in required_fields:
            assert field in template, f"Missing required field: {field}"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_report_id_is_valid_string(self, template):
        """
        Property: report_id must be a non-empty string.
        """
        assert isinstance(template['report_id'], str), "report_id must be a string"
        assert len(template['report_id']) > 0, "report_id must not be empty"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_report_metadata_has_required_fields(self, template):
        """
        Property: report_metadata must contain all required metadata fields.
        
        Required metadata: laboratory, format, date, completeness, abnormality_type
        """
        metadata = template['report_metadata']
        required_metadata_fields = ['laboratory', 'format', 'date', 'completeness', 'abnormality_type']
        
        for field in required_metadata_fields:
            assert field in metadata, f"Missing metadata field: {field}"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_parameters_have_required_structure(self, template):
        """
        Property: Each parameter must have value, unit, and reference_range.
        """
        parameters = template['parameters']
        
        # Must have at least one parameter
        assert len(parameters) > 0, "Template must have at least one parameter"
        
        for param_name, param_data in parameters.items():
            # Check parameter is a dictionary
            assert isinstance(param_data, dict), f"Parameter {param_name} must be a dictionary"
            
            # Check required fields
            required_fields = ['value', 'unit', 'reference_range']
            for field in required_fields:
                assert field in param_data, f"Parameter {param_name} missing field: {field}"
            
            # Check value is numeric
            assert isinstance(param_data['value'], (int, float)), \
                f"Parameter {param_name} value must be numeric"
            
            # Check unit is string
            assert isinstance(param_data['unit'], str), \
                f"Parameter {param_name} unit must be a string"
            
            # Check reference_range structure
            ref_range = param_data['reference_range']
            assert isinstance(ref_range, dict), \
                f"Parameter {param_name} reference_range must be a dictionary"
            assert 'min' in ref_range, \
                f"Parameter {param_name} reference_range missing 'min'"
            assert 'max' in ref_range, \
                f"Parameter {param_name} reference_range missing 'max'"
            
            # Check min/max are numeric
            assert isinstance(ref_range['min'], (int, float, type(None))), \
                f"Parameter {param_name} reference_range min must be numeric or None"
            assert isinstance(ref_range['max'], (int, float, type(None))), \
                f"Parameter {param_name} reference_range max must be numeric or None"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_classifications_match_parameters(self, template):
        """
        Property: Every parameter must have a corresponding classification.
        """
        parameters = template['parameters']
        classifications = template['classifications']
        
        param_names = set(parameters.keys())
        classification_names = set(classifications.keys())
        
        # Every parameter should have a classification
        missing_classifications = param_names - classification_names
        assert len(missing_classifications) == 0, \
            f"Missing classifications for parameters: {missing_classifications}"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_classifications_are_valid_values(self, template):
        """
        Property: All classifications must be Normal, High, Low, or Unknown.
        """
        classifications = template['classifications']
        valid_classifications = {'Normal', 'High', 'Low', 'Unknown'}
        
        for param_name, classification in classifications.items():
            assert classification in valid_classifications, \
                f"Parameter {param_name} has invalid classification: {classification}"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_notes_field_is_string(self, template):
        """
        Property: notes field must be a string (can be empty).
        """
        assert isinstance(template['notes'], str), "notes must be a string"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_template_is_json_serializable(self, template):
        """
        Property: Template must be JSON serializable.
        
        This ensures the template can be saved to a JSON file.
        """
        try:
            json_str = json.dumps(template)
            # Verify we can parse it back
            parsed = json.loads(json_str)
            assert parsed == template, "Template changed after JSON round-trip"
        except (TypeError, ValueError) as e:
            pytest.fail(f"Template is not JSON serializable: {e}")
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_reference_range_min_less_than_or_equal_to_max(self, template):
        """
        Property: For all parameters, reference_range min <= max (when both are not None).
        """
        parameters = template['parameters']
        
        for param_name, param_data in parameters.items():
            ref_range = param_data['reference_range']
            min_val = ref_range['min']
            max_val = ref_range['max']
            
            # If both are numeric, min should be <= max
            if min_val is not None and max_val is not None:
                assert min_val <= max_val, \
                    f"Parameter {param_name} has min ({min_val}) > max ({max_val})"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=20, deadline=None)
    def test_classification_matches_reference_range(self, template):
        """
        Property: Classification should be consistent with value and reference range.
        
        - If value < min: classification should be 'Low'
        - If value > max: classification should be 'High'
        - If min <= value <= max: classification should be 'Normal'
        - If reference range unavailable: classification can be 'Unknown'
        """
        parameters = template['parameters']
        classifications = template['classifications']
        
        for param_name, param_data in parameters.items():
            value = param_data['value']
            ref_range = param_data['reference_range']
            classification = classifications.get(param_name)
            
            min_val = ref_range['min']
            max_val = ref_range['max']
            
            # Skip if reference range is unavailable
            if min_val is None or max_val is None:
                assert classification in ['Unknown', 'Normal', 'High', 'Low'], \
                    f"Parameter {param_name} has invalid classification when range unavailable"
                continue
            
            # Check classification consistency
            if value < min_val:
                assert classification == 'Low', \
                    f"Parameter {param_name}: value {value} < min {min_val}, but classification is {classification}"
            elif value > max_val:
                assert classification == 'High', \
                    f"Parameter {param_name}: value {value} > max {max_val}, but classification is {classification}"
            else:
                assert classification == 'Normal', \
                    f"Parameter {param_name}: value {value} in range [{min_val}, {max_val}], but classification is {classification}"


# ============================================================================
# Integration Tests with GroundTruthGenerator
# ============================================================================

class TestGroundTruthGeneratorSchemaCompliance:
    """
    Test that the GroundTruthGenerator produces templates that comply with the schema.
    """
    
    def test_generator_validate_template_accepts_valid_template(self):
        """
        Test that the generator's validate_template method accepts valid templates.
        """
        generator = GroundTruthGenerator()
        
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
                    "reference_range": {
                        "min": 13.0,
                        "max": 17.5
                    }
                }
            },
            "classifications": {
                "Hemoglobin": "Normal"
            },
            "notes": "Test template"
        }
        
        is_valid, errors = generator.validate_template(valid_template)
        assert is_valid, f"Valid template rejected with errors: {errors}"
        assert len(errors) == 0, f"Valid template has validation errors: {errors}"
    
    def test_generator_validate_template_rejects_missing_report_id(self):
        """
        Test that validate_template rejects templates missing report_id.
        """
        generator = GroundTruthGenerator()
        
        invalid_template = {
            "report_metadata": {},
            "parameters": {},
            "classifications": {},
            "notes": ""
        }
        
        is_valid, errors = generator.validate_template(invalid_template)
        assert not is_valid, "Template without report_id should be invalid"
        assert any("report_id" in error for error in errors), \
            "Validation should report missing report_id"
    
    def test_generator_validate_template_rejects_missing_metadata_fields(self):
        """
        Test that validate_template rejects templates with incomplete metadata.
        """
        generator = GroundTruthGenerator()
        
        invalid_template = {
            "report_id": "report_001",
            "report_metadata": {
                "laboratory": "Test Lab"
                # Missing: format, date, completeness, abnormality_type
            },
            "parameters": {},
            "classifications": {},
            "notes": ""
        }
        
        is_valid, errors = generator.validate_template(invalid_template)
        assert not is_valid, "Template with incomplete metadata should be invalid"
        assert len(errors) > 0, "Should have validation errors for missing metadata fields"
    
    def test_generator_validate_template_rejects_parameter_without_reference_range(self):
        """
        Test that validate_template rejects parameters missing reference_range.
        """
        generator = GroundTruthGenerator()
        
        invalid_template = {
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
                    "unit": "g/dL"
                    # Missing: reference_range
                }
            },
            "classifications": {
                "Hemoglobin": "Normal"
            },
            "notes": ""
        }
        
        is_valid, errors = generator.validate_template(invalid_template)
        assert not is_valid, "Template with parameter missing reference_range should be invalid"
        assert any("reference_range" in error for error in errors), \
            "Validation should report missing reference_range"
    
    def test_generator_validate_template_rejects_missing_classifications(self):
        """
        Test that validate_template rejects templates with parameters but no classifications.
        """
        generator = GroundTruthGenerator()
        
        invalid_template = {
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
                    "reference_range": {
                        "min": 13.0,
                        "max": 17.5
                    }
                }
            },
            "classifications": {
                # Missing: Hemoglobin classification
            },
            "notes": ""
        }
        
        is_valid, errors = generator.validate_template(invalid_template)
        assert not is_valid, "Template with missing classifications should be invalid"
        assert any("classification" in error.lower() for error in errors), \
            "Validation should report missing classifications"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

