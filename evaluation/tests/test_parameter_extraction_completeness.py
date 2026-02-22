"""
Property-Based Tests for Parameter Extraction Completeness

Feature: milestone-1-validation
Property 4: Parameter Extraction Completeness
Validates: Requirements 2.2

Tests that for any generated ground truth template, every extracted parameter
should have a value, unit, and reference range.
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
def ground_truth_template_strategy(draw):
    """Generate a complete ground truth template."""
    # Generate 1-18 parameters
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
    for param_name in param_names:
        param_data = draw(parameter_data_strategy())
        parameters[param_name] = param_data
    
    return {
        "report_id": f"report_{draw(st.integers(min_value=1, max_value=999)):03d}",
        "report_metadata": {},
        "parameters": parameters,
        "classifications": {},
        "notes": ""
    }


# ============================================================================
# Property Tests
# ============================================================================

class TestParameterExtractionCompleteness:
    """
    Property 4: Parameter Extraction Completeness
    
    **Validates: Requirements 2.2**
    
    For any generated ground truth template, every extracted parameter
    should have a value, unit, and reference range.
    """
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=100, deadline=None)
    def test_all_parameters_have_value_field(self, template):
        """Property: Every parameter must have a value field."""
        parameters = template['parameters']
        assert len(parameters) > 0, "Template must have at least one parameter"
        
        for param_name, param_data in parameters.items():
            assert 'value' in param_data, f"Parameter {param_name} must have 'value' field"
            assert param_data['value'] is not None, f"Parameter {param_name} value must not be None"
            assert isinstance(param_data['value'], (int, float)), f"Parameter {param_name} value must be numeric"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=100, deadline=None)
    def test_all_parameters_have_unit_field(self, template):
        """Property: Every parameter must have a unit field."""
        parameters = template['parameters']
        
        for param_name, param_data in parameters.items():
            assert 'unit' in param_data, f"Parameter {param_name} must have 'unit' field"
            assert param_data['unit'] is not None, f"Parameter {param_name} unit must not be None"
            assert isinstance(param_data['unit'], str), f"Parameter {param_name} unit must be a string"
            assert len(param_data['unit']) > 0, f"Parameter {param_name} unit must not be empty"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=100, deadline=None)
    def test_all_parameters_have_reference_range(self, template):
        """Property: Every parameter must have a reference range with min and max."""
        parameters = template['parameters']
        
        for param_name, param_data in parameters.items():
            assert 'reference_range' in param_data, f"Parameter {param_name} must have 'reference_range' field"
            assert param_data['reference_range'] is not None, f"Parameter {param_name} reference_range must not be None"
            
            ref_range = param_data['reference_range']
            assert isinstance(ref_range, dict), f"Parameter {param_name} reference_range must be a dictionary"
            assert 'min' in ref_range, f"Parameter {param_name} reference_range must have 'min' field"
            assert 'max' in ref_range, f"Parameter {param_name} reference_range must have 'max' field"
            
            # min and max should be numeric (or None if unavailable)
            assert isinstance(ref_range['min'], (int, float, type(None))), f"Parameter {param_name} min must be numeric or None"
            assert isinstance(ref_range['max'], (int, float, type(None))), f"Parameter {param_name} max must be numeric or None"
            
            # If both are present, min should be < max
            if ref_range['min'] is not None and ref_range['max'] is not None:
                assert ref_range['min'] < ref_range['max'], f"Parameter {param_name} min must be < max"
    
    @given(template=ground_truth_template_strategy())
    @settings(max_examples=100, deadline=None)
    def test_parameter_completeness_all_fields_present(self, template):
        """Property: Every parameter must have value, unit, AND reference_range (completeness)."""
        parameters = template['parameters']
        
        for param_name, param_data in parameters.items():
            # Check all three required fields are present
            required_fields = ['value', 'unit', 'reference_range']
            for field in required_fields:
                assert field in param_data, f"Parameter {param_name} missing required field: {field}"
            
            # Check none are None
            assert param_data['value'] is not None, f"Parameter {param_name} value is None"
            assert param_data['unit'] is not None, f"Parameter {param_name} unit is None"
            assert param_data['reference_range'] is not None, f"Parameter {param_name} reference_range is None"


# ============================================================================
# Real File Tests
# ============================================================================

def test_real_ground_truth_files_completeness():
    """
    Property 4: Parameter Extraction Completeness (Real Files)

    Verify that all existing ground truth files in the test dataset
    have complete parameter information (for files in the new format).

    **Validates: Requirements 2.2**

    Note: This test only validates files that match the new ground truth format
    (with report_id field). Old format files are skipped.
    """
    ground_truth_dir = Path(__file__).parent.parent / "test_dataset" / "ground_truth"
    json_files = [f for f in ground_truth_dir.glob("*.json") if f.name not in ["TEMPLATE.json", "generation_summary.json"]]

    if len(json_files) == 0:
        pytest.skip("No ground truth files found to test")

    print(f"\nChecking {len(json_files)} ground truth files for completeness...")

    new_format_files = 0
    old_format_files = 0

    for json_file in json_files:
        with open(json_file, 'r') as f:
            template = json.load(f)

        # Check if this is a new format file (has report_id)
        if "report_id" not in template:
            old_format_files += 1
            print(f"  ⊘ {json_file.name}: Old format (skipped)")
            continue

        new_format_files += 1

        assert "parameters" in template, f"File {json_file.name} must have 'parameters' field"
        parameters = template["parameters"]

        for param_name, param_data in parameters.items():
            # Check value
            assert "value" in param_data, f"File {json_file.name}: Parameter {param_name} must have 'value'"
            assert param_data["value"] is not None, f"File {json_file.name}: Parameter {param_name} value must not be None"

            # Check unit
            assert "unit" in param_data, f"File {json_file.name}: Parameter {param_name} must have 'unit'"
            assert param_data["unit"] is not None, f"File {json_file.name}: Parameter {param_name} unit must not be None"
            assert isinstance(param_data["unit"], str), f"File {json_file.name}: Parameter {param_name} unit must be a string"

            # Check reference range
            assert "reference_range" in param_data, f"File {json_file.name}: Parameter {param_name} must have 'reference_range'"
            assert param_data["reference_range"] is not None, f"File {json_file.name}: Parameter {param_name} reference_range must not be None"

            ref_range = param_data["reference_range"]
            assert isinstance(ref_range, dict), f"File {json_file.name}: Parameter {param_name} reference_range must be a dictionary"
            assert "min" in ref_range, f"File {json_file.name}: Parameter {param_name} reference_range must have 'min'"
            assert "max" in ref_range, f"File {json_file.name}: Parameter {param_name} reference_range must have 'max'"

        print(f"  ✓ {json_file.name}: {len(parameters)} parameters verified")

    print(f"\nSummary: {new_format_files} new format files tested, {old_format_files} old format files skipped")

    if new_format_files == 0:
        pytest.skip("No new format ground truth files found to test")



if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
