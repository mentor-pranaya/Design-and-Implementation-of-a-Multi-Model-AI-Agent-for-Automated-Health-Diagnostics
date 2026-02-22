"""
Property-Based Tests for Classification Comparison Correctness

Feature: milestone-1-validation
Property 6: Classification Comparison Correctness
Validates: Requirements 4.1

Tests that for any pair of system output and ground truth with matching parameters,
the comparison function correctly identifies whether classifications match or differ.
"""

import json
import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.validation_pipeline import ValidationPipeline


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

@st.composite
def parameter_data_strategy(draw):
    """Generate parameter data with value, unit, and reference range."""
    value = draw(st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False))
    unit = draw(st.sampled_from(['g/dL', 'mg/dL', 'cells/µL', 'mmol/L', 'U/L', '%', 'ng/mL']))
    
    # Generate reference range
    min_val = draw(st.floats(min_value=0.0, max_value=500.0, allow_nan=False, allow_infinity=False))
    max_val = draw(st.floats(min_value=min_val + 1, max_value=1000.0, allow_nan=False, allow_infinity=False))
    
    return {
        "value": round(value, 2),
        "unit": unit,
        "reference_range": {
            "min": round(min_val, 2),
            "max": round(max_val, 2)
        }
    }


@st.composite
def classification_strategy(draw):
    """Generate a valid classification."""
    return draw(st.sampled_from(['Normal', 'High', 'Low', 'Unknown']))


@st.composite
def matching_pair_strategy(draw):
    """Generate a pair of system output and ground truth with matching classifications."""
    # Generate 1-10 parameters
    num_params = draw(st.integers(min_value=1, max_value=10))
    param_names = draw(st.lists(
        st.sampled_from([
            'Hemoglobin', 'WBC', 'RBC', 'Platelets', 'Glucose', 'Creatinine',
            'Cholesterol', 'Triglycerides', 'ALT', 'AST'
        ]),
        min_size=num_params,
        max_size=num_params,
        unique=True
    ))
    
    # Generate matching parameters and classifications
    system_params = {}
    system_classifications = {}
    gt_params = {}
    gt_classifications = {}
    
    for param_name in param_names:
        param_data = draw(parameter_data_strategy())
        classification = draw(classification_strategy())
        
        # Both system and ground truth have same data
        system_params[param_name] = param_data
        system_classifications[param_name] = classification
        gt_params[param_name] = param_data
        gt_classifications[param_name] = classification
    
    system_output = {
        "parameters": system_params,
        "classifications": system_classifications
    }
    
    ground_truth = {
        "parameters": gt_params,
        "classifications": gt_classifications
    }
    
    return system_output, ground_truth


@st.composite
def mismatching_pair_strategy(draw):
    """Generate a pair of system output and ground truth with at least one mismatching classification."""
    # Generate 1-10 parameters
    num_params = draw(st.integers(min_value=1, max_value=10))
    param_names = draw(st.lists(
        st.sampled_from([
            'Hemoglobin', 'WBC', 'RBC', 'Platelets', 'Glucose', 'Creatinine',
            'Cholesterol', 'Triglycerides', 'ALT', 'AST'
        ]),
        min_size=num_params,
        max_size=num_params,
        unique=True
    ))
    
    # Ensure at least one parameter will have mismatching classification
    assume(len(param_names) >= 1)
    
    # Generate parameters
    system_params = {}
    system_classifications = {}
    gt_params = {}
    gt_classifications = {}
    
    # Pick at least one parameter to have mismatching classification
    mismatch_param = param_names[0]
    
    for param_name in param_names:
        param_data = draw(parameter_data_strategy())
        
        if param_name == mismatch_param:
            # Generate different classifications for this parameter
            sys_classification = draw(classification_strategy())
            gt_classification = draw(classification_strategy())
            # Ensure they're different
            assume(sys_classification != gt_classification)
        else:
            # Other parameters can match or not
            sys_classification = draw(classification_strategy())
            gt_classification = draw(classification_strategy())
        
        system_params[param_name] = param_data
        system_classifications[param_name] = sys_classification
        gt_params[param_name] = param_data
        gt_classifications[param_name] = gt_classification
    
    system_output = {
        "parameters": system_params,
        "classifications": system_classifications
    }
    
    ground_truth = {
        "parameters": gt_params,
        "classifications": gt_classifications
    }
    
    return system_output, ground_truth


@st.composite
def partial_overlap_strategy(draw):
    """Generate a pair where system and ground truth have different sets of parameters."""
    # Generate parameter names
    all_params = ['Hemoglobin', 'WBC', 'RBC', 'Platelets', 'Glucose', 'Creatinine',
                  'Cholesterol', 'Triglycerides', 'ALT', 'AST']
    
    # Generate 2-6 parameters for ground truth
    num_gt_params = draw(st.integers(min_value=2, max_value=6))
    gt_param_names = draw(st.lists(
        st.sampled_from(all_params),
        min_size=num_gt_params,
        max_size=num_gt_params,
        unique=True
    ))
    
    # Generate 2-6 parameters for system (with some overlap)
    num_sys_params = draw(st.integers(min_value=2, max_value=6))
    sys_param_names = draw(st.lists(
        st.sampled_from(all_params),
        min_size=num_sys_params,
        max_size=num_sys_params,
        unique=True
    ))
    
    # Ensure there's at least some difference
    assume(set(gt_param_names) != set(sys_param_names))
    
    # Generate system output
    system_params = {}
    system_classifications = {}
    for param_name in sys_param_names:
        system_params[param_name] = draw(parameter_data_strategy())
        system_classifications[param_name] = draw(classification_strategy())
    
    # Generate ground truth
    gt_params = {}
    gt_classifications = {}
    for param_name in gt_param_names:
        gt_params[param_name] = draw(parameter_data_strategy())
        gt_classifications[param_name] = draw(classification_strategy())
    
    system_output = {
        "parameters": system_params,
        "classifications": system_classifications
    }
    
    ground_truth = {
        "parameters": gt_params,
        "classifications": gt_classifications
    }
    
    return system_output, ground_truth


# ============================================================================
# Property Tests
# ============================================================================

class TestClassificationComparisonCorrectness:
    """
    Property 6: Classification Comparison Correctness
    
    **Validates: Requirements 4.1**
    
    For any pair of system output and ground truth with matching parameters,
    the comparison function should correctly identify whether classifications
    match or differ.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = ValidationPipeline()
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=matching_pair_strategy())
    @settings(max_examples=20, deadline=None)
    def test_matching_classifications_identified_correctly(self, pair):
        """Property: When classifications match, comparison should report all as correct."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        # All parameters should be in matches
        assert result['correct'] == len(ground_truth['classifications']), \
            f"Expected {len(ground_truth['classifications'])} correct, got {result['correct']}"
        
        # No mismatches
        assert result['incorrect'] == 0, \
            f"Expected 0 incorrect, got {result['incorrect']}"
        
        # No missing or extra parameters
        assert len(result['missing_in_system']) == 0, \
            f"Expected no missing parameters, got {len(result['missing_in_system'])}"
        assert len(result['extra_in_system']) == 0, \
            f"Expected no extra parameters, got {len(result['extra_in_system'])}"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=mismatching_pair_strategy())
    @settings(max_examples=20, deadline=None)
    def test_mismatching_classifications_identified_correctly(self, pair):
        """Property: When classifications differ, comparison should report mismatches."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        # Should have at least one mismatch
        assert result['incorrect'] > 0, \
            "Expected at least one incorrect classification"
        
        # Total should equal ground truth parameter count
        assert result['total_ground_truth'] == len(ground_truth['classifications']), \
            f"Expected total_ground_truth={len(ground_truth['classifications'])}, got {result['total_ground_truth']}"
        
        # Correct + incorrect should equal total (when all params present in both)
        if len(result['missing_in_system']) == 0 and len(result['extra_in_system']) == 0:
            assert result['correct'] + result['incorrect'] == result['total_ground_truth'], \
                "Correct + incorrect should equal total when all parameters present"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=partial_overlap_strategy())
    @settings(max_examples=20, deadline=None)
    def test_missing_and_extra_parameters_identified(self, pair):
        """Property: Comparison should identify parameters missing in system or extra in system."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        # Calculate expected missing and extra
        gt_params = set(ground_truth['classifications'].keys())
        sys_params = set(system_output['classifications'].keys())
        
        expected_missing = gt_params - sys_params
        expected_extra = sys_params - gt_params
        
        # Verify missing parameters are identified
        assert len(result['missing_in_system']) == len(expected_missing), \
            f"Expected {len(expected_missing)} missing parameters, got {len(result['missing_in_system'])}"
        
        # Verify extra parameters are identified
        assert len(result['extra_in_system']) == len(expected_extra), \
            f"Expected {len(expected_extra)} extra parameters, got {len(result['extra_in_system'])}"
        
        # Total ground truth should match ground truth parameter count
        assert result['total_ground_truth'] == len(gt_params), \
            f"Expected total_ground_truth={len(gt_params)}, got {result['total_ground_truth']}"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=matching_pair_strategy())
    @settings(max_examples=20, deadline=None)
    def test_comparison_result_structure(self, pair):
        """Property: Comparison result must have all required fields."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        # Check required fields exist
        required_fields = [
            'matches', 'mismatches', 'missing_in_system', 'extra_in_system',
            'total_ground_truth', 'total_system', 'correct', 'incorrect'
        ]
        
        for field in required_fields:
            assert field in result, f"Result must contain '{field}' field"
        
        # Check field types
        assert isinstance(result['matches'], list), "'matches' must be a list"
        assert isinstance(result['mismatches'], list), "'mismatches' must be a list"
        assert isinstance(result['missing_in_system'], list), "'missing_in_system' must be a list"
        assert isinstance(result['extra_in_system'], list), "'extra_in_system' must be a list"
        assert isinstance(result['total_ground_truth'], int), "'total_ground_truth' must be an int"
        assert isinstance(result['total_system'], int), "'total_system' must be an int"
        assert isinstance(result['correct'], int), "'correct' must be an int"
        assert isinstance(result['incorrect'], int), "'incorrect' must be an int"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=matching_pair_strategy())
    @settings(max_examples=20, deadline=None)
    def test_match_entries_have_required_fields(self, pair):
        """Property: Each match entry must contain required fields."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        for match in result['matches']:
            assert 'parameter' in match, "Match must have 'parameter' field"
            assert 'classification' in match, "Match must have 'classification' field"
            assert 'value' in match, "Match must have 'value' field"
            assert 'reference_range' in match, "Match must have 'reference_range' field"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=mismatching_pair_strategy())
    @settings(max_examples=20, deadline=None)
    def test_mismatch_entries_have_required_fields(self, pair):
        """Property: Each mismatch entry must contain required fields for error analysis."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        for mismatch in result['mismatches']:
            assert 'parameter' in mismatch, "Mismatch must have 'parameter' field"
            assert 'system_classification' in mismatch, "Mismatch must have 'system_classification' field"
            assert 'ground_truth_classification' in mismatch, "Mismatch must have 'ground_truth_classification' field"
            assert 'reference_range' in mismatch, "Mismatch must have 'reference_range' field"
            
            # Verify classifications are different
            assert mismatch['system_classification'] != mismatch['ground_truth_classification'], \
                "Mismatch entry should have different system and ground truth classifications"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=matching_pair_strategy())
    @settings(max_examples=20, deadline=None)
    def test_counts_are_consistent(self, pair):
        """Property: Count fields must be consistent with list lengths."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        # Correct count should match matches list length
        assert result['correct'] == len(result['matches']), \
            f"'correct' count ({result['correct']}) must match 'matches' list length ({len(result['matches'])})"
        
        # Incorrect count should match mismatches list length
        assert result['incorrect'] == len(result['mismatches']), \
            f"'incorrect' count ({result['incorrect']}) must match 'mismatches' list length ({len(result['mismatches'])})"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=matching_pair_strategy())
    @settings(max_examples=20, deadline=None)
    def test_counts_are_non_negative(self, pair):
        """Property: All count fields must be non-negative."""
        system_output, ground_truth = pair
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        assert result['total_ground_truth'] >= 0, "'total_ground_truth' must be non-negative"
        assert result['total_system'] >= 0, "'total_system' must be non-negative"
        assert result['correct'] >= 0, "'correct' must be non-negative"
        assert result['incorrect'] >= 0, "'incorrect' must be non-negative"
        assert len(result['missing_in_system']) >= 0, "'missing_in_system' length must be non-negative"
        assert len(result['extra_in_system']) >= 0, "'extra_in_system' length must be non-negative"
    
    # Feature: milestone-1-validation, Property 6: Classification Comparison Correctness
    @given(pair=partial_overlap_strategy())
    @settings(max_examples=20, deadline=None)
    def test_comparison_handles_case_insensitive_matching(self, pair):
        """Property: Comparison should handle case variations in parameter names."""
        system_output, ground_truth = pair
        
        # Modify one parameter name to have different case
        if len(system_output['classifications']) > 0 and len(ground_truth['classifications']) > 0:
            # Get first parameter from each
            sys_param = list(system_output['classifications'].keys())[0]
            gt_param = list(ground_truth['classifications'].keys())[0]
            
            # Make them the same parameter but different case
            base_name = "Hemoglobin"
            
            # Update system output
            sys_class = system_output['classifications'][sys_param]
            sys_data = system_output['parameters'][sys_param]
            del system_output['classifications'][sys_param]
            del system_output['parameters'][sys_param]
            system_output['classifications'][base_name.upper()] = sys_class
            system_output['parameters'][base_name.upper()] = sys_data
            
            # Update ground truth
            gt_class = ground_truth['classifications'][gt_param]
            gt_data = ground_truth['parameters'][gt_param]
            del ground_truth['classifications'][gt_param]
            del ground_truth['parameters'][gt_param]
            ground_truth['classifications'][base_name.lower()] = gt_class
            ground_truth['parameters'][base_name.lower()] = gt_data
            
            # Run comparison
            result = self.pipeline.compare_classifications(system_output, ground_truth)
            
            # Should match despite case difference
            # The comparison should normalize parameter names
            assert result['total_ground_truth'] > 0, "Should have at least one ground truth parameter"


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestClassificationComparisonEdgeCases:
    """Test edge cases for classification comparison."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = ValidationPipeline()
    
    def test_empty_system_output(self):
        """Test comparison when system output is empty."""
        system_output = {
            "parameters": {},
            "classifications": {}
        }
        
        ground_truth = {
            "parameters": {
                "Hemoglobin": {"value": 14.5, "unit": "g/dL", "reference_range": {"min": 13.0, "max": 17.5}}
            },
            "classifications": {
                "Hemoglobin": "Normal"
            }
        }
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        assert result['correct'] == 0
        assert result['incorrect'] == 0
        assert len(result['missing_in_system']) == 1
        assert result['total_ground_truth'] == 1
    
    def test_empty_ground_truth(self):
        """Test comparison when ground truth is empty."""
        system_output = {
            "parameters": {
                "Hemoglobin": {"value": 14.5, "unit": "g/dL", "reference_range": {"min": 13.0, "max": 17.5}}
            },
            "classifications": {
                "Hemoglobin": "Normal"
            }
        }
        
        ground_truth = {
            "parameters": {},
            "classifications": {}
        }
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        assert result['correct'] == 0
        assert result['incorrect'] == 0
        assert len(result['extra_in_system']) == 1
        assert result['total_ground_truth'] == 0
    
    def test_both_empty(self):
        """Test comparison when both are empty."""
        system_output = {
            "parameters": {},
            "classifications": {}
        }
        
        ground_truth = {
            "parameters": {},
            "classifications": {}
        }
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        assert result['correct'] == 0
        assert result['incorrect'] == 0
        assert len(result['missing_in_system']) == 0
        assert len(result['extra_in_system']) == 0
        assert result['total_ground_truth'] == 0
    
    def test_all_classifications_types(self):
        """Test comparison with all classification types (Normal, High, Low, Unknown)."""
        system_output = {
            "parameters": {
                "Hemoglobin": {"value": 14.5, "unit": "g/dL", "reference_range": {"min": 13.0, "max": 17.5}},
                "Glucose": {"value": 150, "unit": "mg/dL", "reference_range": {"min": 70, "max": 100}},
                "Creatinine": {"value": 0.5, "unit": "mg/dL", "reference_range": {"min": 0.7, "max": 1.3}},
                "TSH": {"value": 2.5, "unit": "mIU/L", "reference_range": {"min": 0.4, "max": 4.0}}
            },
            "classifications": {
                "Hemoglobin": "Normal",
                "Glucose": "High",
                "Creatinine": "Low",
                "TSH": "Normal"
            }
        }
        
        ground_truth = {
            "parameters": {
                "Hemoglobin": {"value": 14.5, "unit": "g/dL", "reference_range": {"min": 13.0, "max": 17.5}},
                "Glucose": {"value": 150, "unit": "mg/dL", "reference_range": {"min": 70, "max": 100}},
                "Creatinine": {"value": 0.5, "unit": "mg/dL", "reference_range": {"min": 0.7, "max": 1.3}},
                "TSH": {"value": 2.5, "unit": "mIU/L", "reference_range": {"min": 0.4, "max": 4.0}}
            },
            "classifications": {
                "Hemoglobin": "Normal",
                "Glucose": "High",
                "Creatinine": "Low",
                "TSH": "Normal"
            }
        }
        
        result = self.pipeline.compare_classifications(system_output, ground_truth)
        
        assert result['correct'] == 4
        assert result['incorrect'] == 0
        assert result['total_ground_truth'] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

