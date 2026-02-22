"""
Property-based tests for error logging completeness.

Feature: milestone-1-validation
Property 8: Error Logging Completeness

**Validates: Requirements 5.1**

For any classification error, the error log should include parameter name, report ID,
extracted value, system classification, ground truth classification, and reference range used.
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
    
    return {
        'parameter': draw(st.sampled_from(parameter_names)),
        'report_id': f"report_{draw(st.integers(min_value=1, max_value=20)):03d}",
        'system_value': draw(st.floats(min_value=0.1, max_value=500.0, allow_nan=False, allow_infinity=False)),
        'ground_truth_value': draw(st.floats(min_value=0.1, max_value=500.0, allow_nan=False, allow_infinity=False)),
        'system_classification': draw(st.sampled_from(classifications)),
        'ground_truth_classification': draw(st.sampled_from(classifications)),
        'reference_range': {
            'min': draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
            'max': draw(st.floats(min_value=100.0, max_value=500.0, allow_nan=False, allow_infinity=False))
        }
    }


# Feature: milestone-1-validation, Property 8: Error Logging Completeness
@given(errors=st.lists(error_data_strategy(), min_size=1, max_size=20))
def test_error_logging_completeness(errors):
    """
    Property 8: Error Logging Completeness
    
    For any classification error, the error log should include parameter name, report ID,
    extracted value, system classification, ground truth classification, and reference range used.
    
    Validates: Requirements 5.1
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    
    # Property: All errors should be categorized
    by_category = analysis.get('by_category', {})
    total_categorized = sum(len(errors_list) for errors_list in by_category.values())
    assert total_categorized == len(errors), \
        f"Expected {len(errors)} categorized errors, got {total_categorized}"
    
    # Property: Each categorized error must have all required fields
    required_fields = [
        'parameter',
        'report_id',
        'system_value',
        'ground_truth_value',
        'system_classification',
        'ground_truth_classification',
        'reference_range',
        'category'
    ]
    
    for category, errors_list in by_category.items():
        for error in errors_list:
            for field in required_fields:
                assert field in error, \
                    f"Error missing required field '{field}' in category '{category}'"
            
            # Property: reference_range must be a dict with min and max
            assert isinstance(error['reference_range'], dict), \
                "reference_range must be a dictionary"
            assert 'min' in error['reference_range'], \
                "reference_range must have 'min' field"
            assert 'max' in error['reference_range'], \
                "reference_range must have 'max' field"


# Feature: milestone-1-validation, Property 8: Error Logging Completeness
@given(error=error_data_strategy())
def test_single_error_logging_completeness(error):
    """
    Property: Single error analysis preserves all required fields.
    
    Validates: Requirements 5.1
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze single error
    analysis = analyzer.analyze_errors([error])
    
    # Property: Error must be in one of the categories
    by_category = analysis.get('by_category', {})
    assert len(by_category) > 0, "Error must be categorized"
    
    # Find the categorized error
    categorized_error = None
    for category, errors_list in by_category.items():
        if errors_list:
            categorized_error = errors_list[0]
            break
    
    assert categorized_error is not None, "Error must be in a category"
    
    # Property: All original fields must be preserved
    assert categorized_error['parameter'] == error['parameter']
    assert categorized_error['report_id'] == error['report_id']
    assert categorized_error['system_value'] == error['system_value']
    assert categorized_error['ground_truth_value'] == error['ground_truth_value']
    assert categorized_error['system_classification'] == error['system_classification']
    assert categorized_error['ground_truth_classification'] == error['ground_truth_classification']
    assert categorized_error['reference_range'] == error['reference_range']
    
    # Property: Category field must be added
    assert 'category' in categorized_error
    assert categorized_error['category'] in analyzer.error_categories


# Feature: milestone-1-validation, Property 8: Error Logging Completeness
@given(errors=st.lists(error_data_strategy(), min_size=0, max_size=50))
def test_error_count_preservation(errors):
    """
    Property: Total error count is preserved through analysis.
    
    Validates: Requirements 5.1
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    
    # Property: Total errors count must match input
    assert analysis['total_errors'] == len(errors), \
        f"Expected {len(errors)} total errors, got {analysis['total_errors']}"
    
    # Property: Sum of categorized errors must equal total
    by_category = analysis.get('by_category', {})
    categorized_count = sum(len(errors_list) for errors_list in by_category.values())
    assert categorized_count == len(errors), \
        f"Expected {len(errors)} categorized errors, got {categorized_count}"


# Feature: milestone-1-validation, Property 8: Error Logging Completeness
def test_error_logging_with_missing_fields():
    """
    Property: Errors with missing optional fields are still logged.
    
    Validates: Requirements 5.1
    """
    analyzer = ErrorAnalyzer()
    
    # Error with some missing fields (but required ones present)
    error = {
        'parameter': 'glucose',
        'system_classification': 'High',
        'ground_truth_classification': 'Normal',
        'reference_range': {'min': 70, 'max': 100}
        # Missing: report_id, system_value, ground_truth_value
    }
    
    # Analyze error
    analysis = analyzer.analyze_errors([error])
    
    # Property: Error should still be categorized
    assert analysis['total_errors'] == 1
    by_category = analysis.get('by_category', {})
    assert len(by_category) > 0
    
    # Property: Categorized error should have all fields (even if None)
    categorized_error = None
    for errors_list in by_category.values():
        if errors_list:
            categorized_error = errors_list[0]
            break
    
    assert categorized_error is not None
    assert 'parameter' in categorized_error
    assert 'report_id' in categorized_error
    assert 'category' in categorized_error


# Feature: milestone-1-validation, Property 8: Error Logging Completeness
def test_error_logging_empty_list():
    """
    Property: Empty error list produces valid analysis structure.
    
    Validates: Requirements 5.1
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze empty list
    analysis = analyzer.analyze_errors([])
    
    # Property: Analysis must have required structure
    assert 'total_errors' in analysis
    assert 'by_category' in analysis
    assert 'category_summary' in analysis
    assert 'systematic_errors' in analysis
    assert 'edge_cases' in analysis
    assert 'recommendations' in analysis
    
    # Property: Counts should be zero
    assert analysis['total_errors'] == 0
    assert len(analysis['by_category']) == 0
    assert len(analysis['systematic_errors']) == 0
    assert len(analysis['edge_cases']) == 0


# Feature: milestone-1-validation, Property 8: Error Logging Completeness
@given(errors=st.lists(error_data_strategy(), min_size=1, max_size=10))
def test_error_report_generation_completeness(errors):
    """
    Property: Generated error report includes all error information.
    
    Validates: Requirements 5.1
    """
    analyzer = ErrorAnalyzer()
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    
    # Generate report
    report = analyzer.generate_error_report(analysis)
    
    # Property: Report must be non-empty string
    assert isinstance(report, str)
    assert len(report) > 0
    
    # Property: Report must include key sections
    assert "Error Analysis Report" in report
    assert "Summary" in report
    assert "Total Errors" in report
    
    # Property: Report must mention error count
    assert str(len(errors)) in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

