"""
Property-based tests for error categorization validity.

Feature: milestone-1-validation
Property 9: Error Categorization Validity

**Validates: Requirements 5.2**

For any categorized error, the category should be one of: extraction_error,
reference_range_error, classification_logic_error, or edge_case.
"""

import pytest
from hypothesis import given, strategies as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.error_analyzer import ErrorAnalyzer


# Strategy for generating error data
@st.composite
def error_data_strategy(draw):
    """Generate a valid error data structure."""
    parameter_names = ['hemoglobin', 'glucose', 'creatinine', 'wbc', 'rbc', 'platelets']
    classifications = ['Normal', 'High', 'Low']
    
    min_val = draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    max_val = draw(st.floats(min_value=min_val + 1, max_value=500.0, allow_nan=False, allow_infinity=False))
    
    return {
        'parameter': draw(st.sampled_from(parameter_names)),
        'report_id': f"report_{draw(st.integers(min_value=1, max_value=20)):03d}",
        'system_value': draw(st.floats(min_value=0.1, max_value=500.0, allow_nan=False, allow_infinity=False)),
        'ground_truth_value': draw(st.floats(min_value=0.1, max_value=500.0, allow_nan=False, allow_infinity=False)),
        'system_classification': draw(st.sampled_from(classifications)),
        'ground_truth_classification': draw(st.sampled_from(classifications)),
        'reference_range': {
            'min': min_val,
            'max': max_val
        }
    }


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
@given(error=error_data_strategy())
def test_error_categorization_validity(error):
    """
    Property 9: Error Categorization Validity
    
    For any categorized error, the category should be one of: extraction_error,
    reference_range_error, classification_logic_error, or edge_case.
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    # Categorize error
    category = analyzer.categorize_error(error)
    
    # Property: Category must be one of the valid categories
    valid_categories = [
        'extraction_error',
        'reference_range_error',
        'classification_logic_error',
        'edge_case'
    ]
    
    assert category in valid_categories, \
        f"Invalid category '{category}'. Must be one of {valid_categories}"
    
    # Property: Category must match analyzer's defined categories
    assert category in analyzer.error_categories, \
        f"Category '{category}' not in analyzer's error_categories list"


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
@given(errors=st.lists(error_data_strategy(), min_size=1, max_size=20))
def test_all_errors_have_valid_categories(errors):
    """
    Property: All errors in analysis have valid categories.
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    
    # Property: All categorized errors must have valid categories
    by_category = analysis.get('by_category', {})
    
    for category, errors_list in by_category.items():
        # Property: Category key must be valid
        assert category in analyzer.error_categories, \
            f"Invalid category key '{category}'"
        
        # Property: Each error in the list must have the same category
        for error in errors_list:
            assert error.get('category') == category, \
                f"Error has category '{error.get('category')}' but is in '{category}' list"


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
def test_extraction_error_categorization():
    """
    Property: Errors with different values are categorized as extraction_error.
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    # Error with different system and ground truth values
    error = {
        'parameter': 'glucose',
        'system_value': 110.0,
        'ground_truth_value': 95.0,  # Different value
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
    }
    
    category = analyzer.categorize_error(error)
    
    # Property: Should be categorized as extraction_error
    assert category == 'extraction_error', \
        f"Expected 'extraction_error', got '{category}'"


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
def test_edge_case_categorization():
    """
    Property: Errors with values within 5% of boundaries are categorized as edge_case.
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    # Error with value very close to upper boundary
    # Range: 70-100, 5% of range = 1.5, so 98.6 is within 5% of 100
    error = {
        'parameter': 'glucose',
        'system_value': 98.6,
        'ground_truth_value': 98.6,
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
    }
    
    category = analyzer.categorize_error(error)
    
    # Property: Should be categorized as edge_case
    assert category == 'edge_case', \
        f"Expected 'edge_case', got '{category}'"


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
def test_classification_logic_error_categorization():
    """
    Property: Errors with same value but wrong classification are classification_logic_error.
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    # Error with same value, but wrong classification
    # Value is clearly in range, but system says High
    error = {
        'parameter': 'glucose',
        'system_value': 85.0,
        'ground_truth_value': 85.0,  # Same value
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
    }
    
    category = analyzer.categorize_error(error)
    
    # Property: Should be categorized as classification_logic_error
    assert category == 'classification_logic_error', \
        f"Expected 'classification_logic_error', got '{category}'"


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
@given(errors=st.lists(error_data_strategy(), min_size=0, max_size=50))
def test_category_summary_validity(errors):
    """
    Property: Category summary only contains valid categories.
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    
    # Property: All categories in summary must be valid
    category_summary = analysis.get('category_summary', {})
    
    for category in category_summary.keys():
        assert category in analyzer.error_categories, \
            f"Invalid category '{category}' in summary"


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
@given(errors=st.lists(error_data_strategy(), min_size=1, max_size=20))
def test_category_counts_match(errors):
    """
    Property: Category counts in summary match actual categorized errors.
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    
    # Property: Counts in summary must match actual errors in categories
    category_summary = analysis.get('category_summary', {})
    by_category = analysis.get('by_category', {})
    
    for category, count in category_summary.items():
        actual_count = len(by_category.get(category, []))
        assert count == actual_count, \
            f"Category '{category}' summary shows {count} but has {actual_count} errors"


# Feature: milestone-1-validation, Property 9: Error Categorization Validity
def test_categorization_deterministic():
    """
    Property: Same error always gets same category (deterministic).
    
    Validates: Requirements 5.2
    """
    analyzer = ErrorAnalyzer()
    
    error = {
        'parameter': 'glucose',
        'system_value': 110.0,
        'ground_truth_value': 110.0,
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
    }
    
    # Categorize multiple times
    categories = [analyzer.categorize_error(error) for _ in range(10)]
    
    # Property: All categorizations should be the same
    assert len(set(categories)) == 1, \
        f"Categorization is not deterministic: {set(categories)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

