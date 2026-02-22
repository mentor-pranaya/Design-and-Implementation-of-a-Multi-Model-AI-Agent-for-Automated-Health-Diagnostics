"""
Property-Based Tests for Classification Presence

Feature: milestone-1-validation
Property 5: Classification Presence
Validates: Requirements 2.3

Tests that for any parameter in a generated template, there should be a
corresponding classification (Normal/High/Low) in the classifications section.
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
def parameter_with_classification_strategy(draw):
    """Generate a parameter with its classification."""
    value = draw(st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False))
    unit = draw(st.sampled_from(['g/dL', 'mg/dL', 'cells/µL', 'mmol/L', 'U/L', '%', 'ng/mL']))
    
    # Generate reference range
    min_val = draw(st.floats(min_value=0.0, max_value=500.0, allow_nan=False, allow_infinity=False))
    max_val = draw(st.floats(min_value=min_val + 1, max_value=1000.0, allow_nan=False, allow_infinity=False))
    
    # Determine classification based on value and range
    if value < min_val:
        classification = "Low"
    elif value > max_val:
        classification = "High"
    else:
        classification = "Normal"
    
    parameter_data = {
        "value": round(value, 2),
        "unit": unit,
        "reference_range": {
            "min": round(min_val, 2),
            "max": round(max_val, 2)
        }
    }
    
    return parameter_data, classification


@st.composite
def ground_truth_with_classifications_strategy(draw):
    """Generate a complete ground truth template with parameters and classifications."""
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
    
    # Generate parameters and classifications
    parameters = {}
    classifications = {}
    
    for param_name in param_names:
        param_data, classification = draw(parameter_with_classification_strategy())
        parameters[param_name] = param_data
        classifications[param_name] = classification
    
    return {
        "report_id": f"report_{draw(st.integers(min_value=1, max_value=999)):03d}",
        "report_metadata": {},
        "parameters": parameters,
        "classifications": classifications,
        "notes": ""
    }


# ============================================================================
# Property Tests
# ============================================================================

class TestClassificationPresence:
    """
    Property 5: Classification Presence
    
    **Validates: Requirements 2.3**
    
    For any parameter in a generated template, there should be a corresponding
    classification (Normal/High/Low) in the classifications section.
    """
    
    # Feature: milestone-1-validation, Property 5: Classification Presence
    @given(template=ground_truth_with_classifications_strategy())
    @settings(max_examples=20, deadline=None)
    def test_all_parameters_have_classification(self, template):
        """Property: Every parameter must have a corresponding classification."""
        parameters = template['parameters']
        classifications = template['classifications']
        
        assert len(parameters) > 0, "Template must have at least one parameter"
        assert 'classifications' in template, "Template must have 'classifications' field"
        
        # Check that every parameter has a classification
        for param_name in parameters.keys():
            assert param_name in classifications, \
                f"Parameter '{param_name}' must have a corresponding classification"
    
    # Feature: milestone-1-validation, Property 5: Classification Presence
    @given(template=ground_truth_with_classifications_strategy())
    @settings(max_examples=20, deadline=None)
    def test_classification_values_are_valid(self, template):
        """Property: All classifications must be Normal, High, Low, or Unknown."""
        classifications = template['classifications']
        valid_classifications = {'Normal', 'High', 'Low', 'Unknown'}
        
        for param_name, classification in classifications.items():
            assert classification in valid_classifications, \
                f"Parameter '{param_name}' has invalid classification '{classification}'. " \
                f"Must be one of: {valid_classifications}"
    
    # Feature: milestone-1-validation, Property 5: Classification Presence
    @given(template=ground_truth_with_classifications_strategy())
    @settings(max_examples=20, deadline=None)
    def test_classification_count_matches_parameter_count(self, template):
        """Property: Number of classifications should match number of parameters."""
        parameters = template['parameters']
        classifications = template['classifications']
        
        param_count = len(parameters)
        classification_count = len(classifications)
        
        assert param_count == classification_count, \
            f"Parameter count ({param_count}) must match classification count ({classification_count})"
    
    # Feature: milestone-1-validation, Property 5: Classification Presence
    @given(template=ground_truth_with_classifications_strategy())
    @settings(max_examples=20, deadline=None)
    def test_no_extra_classifications(self, template):
        """Property: There should be no classifications for non-existent parameters."""
        parameters = template['parameters']
        classifications = template['classifications']
        
        param_names = set(parameters.keys())
        classification_names = set(classifications.keys())
        
        # Check that all classification keys correspond to actual parameters
        extra_classifications = classification_names - param_names
        assert len(extra_classifications) == 0, \
            f"Found classifications for non-existent parameters: {extra_classifications}"
    
    # Feature: milestone-1-validation, Property 5: Classification Presence
    @given(template=ground_truth_with_classifications_strategy())
    @settings(max_examples=20, deadline=None)
    def test_classification_is_not_none_or_empty(self, template):
        """Property: Classifications must not be None or empty strings."""
        classifications = template['classifications']
        
        for param_name, classification in classifications.items():
            assert classification is not None, \
                f"Classification for '{param_name}' must not be None"
            assert isinstance(classification, str), \
                f"Classification for '{param_name}' must be a string"
            assert len(classification) > 0, \
                f"Classification for '{param_name}' must not be empty"


# ============================================================================
# Real File Tests
# ============================================================================

def test_real_ground_truth_files_classification_presence():
    """
    Property 5: Classification Presence (Real Files)

    Verify that all existing ground truth files in the test dataset
    have classifications for all parameters.

    **Validates: Requirements 2.3**

    Note: This test only validates files that match the new ground truth format
    (with report_id field). Old format files are skipped.
    """
    ground_truth_dir = Path(__file__).parent.parent / "test_dataset" / "ground_truth"
    json_files = [f for f in ground_truth_dir.glob("*.json") 
                  if f.name not in ["TEMPLATE.json", "generation_summary.json"]]

    if len(json_files) == 0:
        pytest.skip("No ground truth files found to test")

    print(f"\nChecking {len(json_files)} ground truth files for classification presence...")

    new_format_files = 0
    old_format_files = 0
    valid_classifications = {'Normal', 'High', 'Low', 'Unknown'}

    for json_file in json_files:
        with open(json_file, 'r') as f:
            template = json.load(f)

        # Check if this is a new format file (has report_id)
        if "report_id" not in template:
            old_format_files += 1
            print(f"  ⊘ {json_file.name}: Old format (skipped)")
            continue

        new_format_files += 1

        assert "parameters" in template, \
            f"File {json_file.name} must have 'parameters' field"
        assert "classifications" in template, \
            f"File {json_file.name} must have 'classifications' field"

        parameters = template["parameters"]
        classifications = template["classifications"]

        # Check that every parameter has a classification
        for param_name in parameters.keys():
            assert param_name in classifications, \
                f"File {json_file.name}: Parameter '{param_name}' must have a classification"
            
            classification = classifications[param_name]
            assert classification is not None, \
                f"File {json_file.name}: Classification for '{param_name}' must not be None"
            assert isinstance(classification, str), \
                f"File {json_file.name}: Classification for '{param_name}' must be a string"
            assert classification in valid_classifications, \
                f"File {json_file.name}: Classification for '{param_name}' is '{classification}', " \
                f"must be one of: {valid_classifications}"

        # Check that there are no extra classifications
        param_names = set(parameters.keys())
        classification_names = set(classifications.keys())
        extra_classifications = classification_names - param_names
        
        assert len(extra_classifications) == 0, \
            f"File {json_file.name}: Found classifications for non-existent parameters: {extra_classifications}"

        print(f"  ✓ {json_file.name}: {len(parameters)} parameters, {len(classifications)} classifications")

    print(f"\nSummary: {new_format_files} new format files tested, {old_format_files} old format files skipped")

    if new_format_files == 0:
        pytest.skip("No new format ground truth files found to test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

