"""
Property-based tests for edge case separation.

Feature: milestone-1-validation
Property 11: Edge Case Separation

**Validates: Requirements 5.4**

For any error where the value is within 5% of a reference range boundary,
the error analyzer should categorize it as an edge_case.
"""

import pytest
from hypothesis import given, strategies as st, assume
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.error_analyzer import ErrorAnalyzer


# Feature: milestone-1-validation, Property 11: Edge Case Separation
@given(
    min_val=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_val=st.floats(min_value=100.0, max_value=500.0, allow_nan=False, allow_infinity=False)
)
def test_edge_case_near_upper_boundary(min_val, max_val):
    """
    Property 11: Edge Case Separation
    
    For any error where the value is within 5% of a reference range boundary,
    the error analyzer should categorize it as an edge_case.
    
    Validates: Requirements 5.4
    """
    assume(max_val > min_val)
    
    analyzer = ErrorAnalyzer()
    
    # Calculate 5% threshold
    range_span = max_val - min_val
    threshold = range_span * 0.05
    
    # Value within 5% of upper boundary
    value = max_val - (threshold * 0.5)  # Halfway into the 5% zone
    
    error = {
        'parameter': 'test_param',
        'system_value': value,
        'ground_truth_value': value,
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': min_val, 'max': max_val}
    }
    
    category = analyzer.categorize_error(error)
    
    # Property: Should be categorized as edge_case
    assert category == 'edge_case', \
        f"Value {value} within 5% of boundary {max_val} should be edge_case, got '{category}'"


# Feature: milestone-1-validation, Property 11: Edge Case Separation
@given(
    min_val=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_val=st.floats(min_value=100.0, max_value=500.0, allow_nan=False, allow_infinity=False)
)
def test_edge_case_near_lower_boundary(min_val, max_val):
    """
    Property: Values within 5% of lower boundary are edge cases.
    
    Validates: Requirements 5.4
    """
    assume(max_val > min_val)
    
    analyzer = ErrorAnalyzer()
    
    # Calculate 5% threshold
    range_span = max_val - min_val
    threshold = range_span * 0.05
    
    # Value within 5% of lower boundary
    value = min_val + (threshold * 0.5)  # Halfway into the 5% zone
    
    error = {
        'parameter': 'test_param',
        'system_value': value,
        'ground_truth_value': value,
        'system_classification': 'Low',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': min_val, 'max': max_val}
    }
    
    category = analyzer.categorize_error(error)
    
    # Property: Should be categorized as edge_case
    assert category == 'edge_case', \
        f"Value {value} within 5% of boundary {min_val} should be edge_case, got '{category}'"


# Feature: milestone-1-validation, Property 11: Edge Case Separation
@given(
    min_val=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_val=st.floats(min_value=100.0, max_value=500.0, allow_nan=False, allow_infinity=False)
)
def test_non_edge_case_in_middle(min_val, max_val):
    """
    Property: Values in the middle of range are NOT edge cases.
    
    Validates: Requirements 5.4
    """
    assume(max_val > min_val)
    assume(max_val - min_val > 20)  # Ensure range is large enough
    
    analyzer = ErrorAnalyzer()
    
    # Value in the middle of range (far from boundaries)
    value = (min_val + max_val) / 2
    
    error = {
        'parameter': 'test_param',
        'system_value': value,
        'ground_truth_value': value,
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': min_val, 'max': max_val}
    }
    
    category = analyzer.categorize_error(error)
    
    # Property: Should NOT be categorized as edge_case
    assert category != 'edge_case', \
        f"Value {value} in middle of range should not be edge_case, got '{category}'"


# Feature: milestone-1-validation, Property 11: Edge Case Separation
def test_edge_case_exactly_at_boundary():
    """
    Property: Values exactly at boundary are edge cases.
    
    Validates: Requirements 5.4
    """
    analyzer = ErrorAnalyzer()
    
    # Value exactly at upper boundary
    error = {
        'parameter': 'glucose',
        'system_value': 100.0,
        'ground_truth_value': 100.0,
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
    }
    
    category = analyzer.categorize_error(error)
    
    # Property: Should be categorized as edge_case
    assert category == 'edge_case', \
        f"Value at boundary should be edge_case, got '{category}'"


# Feature: milestone-1-validation, Property 11: Edge Case Separation
def test_edge_case_separation_in_analysis():
    """
    Property: Edge cases are separated in analysis results.
    
    Validates: Requirements 5.4
    """
    analyzer = ErrorAnalyzer()
    
    # Create mix of edge cases and non-edge cases
    errors = [
        # Edge case (near upper boundary)
        {
            'parameter': 'glucose',
            'system_value': 98.5,
            'ground_truth_value': 98.5,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        # Non-edge case (middle of range)
        {
            'parameter': 'glucose',
            'system_value': 85.0,
            'ground_truth_value': 85.0,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        # Edge case (near lower boundary)
        {
            'parameter': 'hemoglobin',
            'system_value': 13.2,
            'ground_truth_value': 13.2,
            'system_classification': 'Low',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 13.0, 'max': 17.5}
        }
    ]
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    
    # Property: Edge cases should be separated
    edge_cases = analysis.get('edge_cases', [])
    assert len(edge_cases) == 2, \
        f"Expected 2 edge cases, got {len(edge_cases)}"
    
    # Property: Edge cases should be in the edge_case category
    by_category = analysis.get('by_category', {})
    edge_case_category = by_category.get('edge_case', [])
    assert len(edge_case_category) == 2, \
        f"Expected 2 errors in edge_case category, got {len(edge_case_category)}"


# Feature: milestone-1-validation, Property 11: Edge Case Separation
def test_edge_case_5_percent_threshold():
    """
    Property: 5% threshold is correctly calculated.
    
    Validates: Requirements 5.4
    """
    analyzer = ErrorAnalyzer()
    
    # Range: 70-100, span = 30, 5% = 1.5
    # Upper boundary: 100, 5% zone: 98.5-100
    # Value at 98.5 should be edge case
    # Value at 98.4 should NOT be edge case
    
    edge_case_error = {
        'parameter': 'glucose',
        'system_value': 98.5,
        'ground_truth_value': 98.5,
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
    }
    
    non_edge_case_error = {
        'parameter': 'glucose',
        'system_value': 98.4,
        'ground_truth_value': 98.4,
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
    }
    
    # Property: 98.5 should be edge case
    category1 = analyzer.categorize_error(edge_case_error)
    assert category1 == 'edge_case', \
        f"Value 98.5 should be edge_case, got '{category1}'"
    
    # Property: 98.4 should NOT be edge case
    category2 = analyzer.categorize_error(non_edge_case_error)
    assert category2 != 'edge_case', \
        f"Value 98.4 should not be edge_case, got '{category2}'"


# Feature: milestone-1-validation, Property 11: Edge Case Separation
@given(
    value=st.floats(min_value=98.5, max_value=100.0, allow_nan=False, allow_infinity=False),
    count=st.integers(min_value=1, max_value=10)
)
def test_all_edge_cases_separated(value, count):
    """
    Property: All edge cases are properly separated in analysis.
    
    Validates: Requirements 5.4
    
    Range: 70-100, span = 30, 5% = 1.5
    Upper boundary: 100, 5% zone: 98.5-100
    All values in 98.5-100 should be edge cases
    """
    analyzer = ErrorAnalyzer()
    
    # Create errors with same value (to avoid extraction_error categorization)
    errors = []
    for i in range(count):
        errors.append({
            'parameter': 'glucose',
            'system_value': value,
            'ground_truth_value': value,  # Same value to avoid extraction error
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        })
    
    # All errors should be edge cases (values 98.5-100 with range 70-100)
    analysis = analyzer.analyze_errors(errors)
    
    # Property: All should be in edge_cases list
    edge_cases = analysis.get('edge_cases', [])
    assert len(edge_cases) == len(errors), \
        f"Expected {len(errors)} edge cases, got {len(edge_cases)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

