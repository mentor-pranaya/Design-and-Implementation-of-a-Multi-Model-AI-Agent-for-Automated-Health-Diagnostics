"""
Property-based tests for systematic error detection.

Feature: milestone-1-validation
Property 10: Systematic Error Detection

**Validates: Requirements 5.3**

For any set of errors where the same parameter fails across multiple reports (≥3),
the error analyzer should flag it as systematic.
"""

import pytest
from hypothesis import given, strategies as st, assume
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.error_analyzer import ErrorAnalyzer


# Strategy for generating error data
@st.composite
def error_with_parameter_strategy(draw, parameter_name):
    """Generate error data for a specific parameter."""
    classifications = ['Normal', 'High', 'Low']
    
    min_val = draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    max_val = draw(st.floats(min_value=min_val + 1, max_value=500.0, allow_nan=False, allow_infinity=False))
    
    return {
        'parameter': parameter_name,
        'report_id': f"report_{draw(st.integers(min_value=1, max_value=100)):03d}",
        'system_value': draw(st.floats(min_value=0.1, max_value=500.0, allow_nan=False, allow_infinity=False)),
        'ground_truth_value': draw(st.floats(min_value=0.1, max_value=500.0, allow_nan=False, allow_infinity=False)),
        'system_classification': draw(st.sampled_from(classifications)),
        'ground_truth_classification': draw(st.sampled_from(classifications)),
        'reference_range': {
            'min': min_val,
            'max': max_val
        }
    }


# Feature: milestone-1-validation, Property 10: Systematic Error Detection
@given(
    frequency=st.integers(min_value=3, max_value=10),
    parameter_name=st.sampled_from(['glucose', 'hemoglobin', 'creatinine'])
)
def test_systematic_error_detection_threshold(frequency, parameter_name):
    """
    Property 10: Systematic Error Detection
    
    For any set of errors where the same parameter fails across multiple reports (≥3),
    the error analyzer should flag it as systematic.
    
    Validates: Requirements 5.3
    """
    analyzer = ErrorAnalyzer()
    
    # Generate errors for the same parameter across multiple reports
    errors = []
    for i in range(frequency):
        error = {
            'parameter': parameter_name,
            'report_id': f"report_{i+1:03d}",
            'system_value': 100.0 + i,
            'ground_truth_value': 100.0 + i,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        }
        errors.append(error)
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    systematic_errors = analysis.get('systematic_errors', [])
    
    # Property: Parameter with ≥3 errors should be flagged as systematic
    assert len(systematic_errors) == 1, \
        f"Expected 1 systematic error, got {len(systematic_errors)}"
    
    systematic = systematic_errors[0]
    assert systematic['parameter'] == parameter_name.lower(), \
        f"Expected parameter '{parameter_name}', got '{systematic['parameter']}'"
    assert systematic['frequency'] == frequency, \
        f"Expected frequency {frequency}, got {systematic['frequency']}"


# Feature: milestone-1-validation, Property 10: Systematic Error Detection
@given(frequency=st.integers(min_value=0, max_value=2))
def test_systematic_error_below_threshold(frequency):
    """
    Property: Parameters with <3 errors are NOT flagged as systematic.
    
    Validates: Requirements 5.3
    """
    analyzer = ErrorAnalyzer()
    
    # Generate errors below threshold
    errors = []
    for i in range(frequency):
        error = {
            'parameter': 'glucose',
            'report_id': f"report_{i+1:03d}",
            'system_value': 100.0,
            'ground_truth_value': 100.0,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        }
        errors.append(error)
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    systematic_errors = analysis.get('systematic_errors', [])
    
    # Property: Should NOT be flagged as systematic
    assert len(systematic_errors) == 0, \
        f"Expected 0 systematic errors for frequency {frequency}, got {len(systematic_errors)}"


# Feature: milestone-1-validation, Property 10: Systematic Error Detection
def test_systematic_error_multiple_parameters():
    """
    Property: Multiple parameters can be flagged as systematic independently.
    
    Validates: Requirements 5.3
    """
    analyzer = ErrorAnalyzer()
    
    # Create errors for two different parameters, both ≥3 times
    errors = []
    
    # Glucose errors (4 times)
    for i in range(4):
        errors.append({
            'parameter': 'glucose',
            'report_id': f"report_{i+1:03d}",
            'system_value': 100.0,
            'ground_truth_value': 100.0,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        })
    
    # Hemoglobin errors (3 times)
    for i in range(3):
        errors.append({
            'parameter': 'hemoglobin',
            'report_id': f"report_{i+10:03d}",
            'system_value': 12.0,
            'ground_truth_value': 12.0,
            'system_classification': 'Low',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 13.0, 'max': 17.5}
        })
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    systematic_errors = analysis.get('systematic_errors', [])
    
    # Property: Both parameters should be flagged
    assert len(systematic_errors) == 2, \
        f"Expected 2 systematic errors, got {len(systematic_errors)}"
    
    # Property: Should be sorted by frequency (glucose first with 4, then hemoglobin with 3)
    assert systematic_errors[0]['frequency'] >= systematic_errors[1]['frequency'], \
        "Systematic errors should be sorted by frequency (descending)"


# Feature: milestone-1-validation, Property 10: Systematic Error Detection
def test_systematic_error_frequency_accuracy():
    """
    Property: Systematic error frequency count is accurate.
    
    Validates: Requirements 5.3
    """
    analyzer = ErrorAnalyzer()
    
    # Create exactly 5 errors for glucose
    errors = []
    for i in range(5):
        errors.append({
            'parameter': 'glucose',
            'report_id': f"report_{i+1:03d}",
            'system_value': 100.0 + i,
            'ground_truth_value': 100.0 + i,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        })
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    systematic_errors = analysis.get('systematic_errors', [])
    
    # Property: Frequency should be exactly 5
    assert len(systematic_errors) == 1
    assert systematic_errors[0]['frequency'] == 5, \
        f"Expected frequency 5, got {systematic_errors[0]['frequency']}"
    
    # Property: Should have all 5 errors in the list
    assert len(systematic_errors[0]['errors']) == 5, \
        f"Expected 5 errors in list, got {len(systematic_errors[0]['errors'])}"


# Feature: milestone-1-validation, Property 10: Systematic Error Detection
def test_systematic_error_category_breakdown():
    """
    Property: Systematic errors include category breakdown.
    
    Validates: Requirements 5.3
    """
    analyzer = ErrorAnalyzer()
    
    # Create errors with different categories
    errors = [
        {
            'parameter': 'glucose',
            'report_id': 'report_001',
            'system_value': 110.0,
            'ground_truth_value': 95.0,  # Different value - extraction error
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        {
            'parameter': 'glucose',
            'report_id': 'report_002',
            'system_value': 98.5,
            'ground_truth_value': 98.5,  # Edge case
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        {
            'parameter': 'glucose',
            'report_id': 'report_003',
            'system_value': 85.0,
            'ground_truth_value': 85.0,  # Classification logic error
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        }
    ]
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    systematic_errors = analysis.get('systematic_errors', [])
    
    # Property: Should have category breakdown
    assert len(systematic_errors) == 1
    systematic = systematic_errors[0]
    
    assert 'category_breakdown' in systematic, \
        "Systematic error must have category_breakdown"
    assert 'most_common_category' in systematic, \
        "Systematic error must have most_common_category"
    
    # Property: Category breakdown should sum to total frequency
    category_sum = sum(systematic['category_breakdown'].values())
    assert category_sum == systematic['frequency'], \
        f"Category breakdown sum {category_sum} != frequency {systematic['frequency']}"


# Feature: milestone-1-validation, Property 10: Systematic Error Detection
def test_systematic_error_case_insensitive():
    """
    Property: Parameter name matching is case-insensitive.
    
    Validates: Requirements 5.3
    """
    analyzer = ErrorAnalyzer()
    
    # Create errors with different case variations
    errors = [
        {
            'parameter': 'Glucose',
            'report_id': 'report_001',
            'system_value': 100.0,
            'ground_truth_value': 100.0,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        {
            'parameter': 'glucose',
            'report_id': 'report_002',
            'system_value': 100.0,
            'ground_truth_value': 100.0,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        {
            'parameter': 'GLUCOSE',
            'report_id': 'report_003',
            'system_value': 100.0,
            'ground_truth_value': 100.0,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        }
    ]
    
    # Analyze errors
    analysis = analyzer.analyze_errors(errors)
    systematic_errors = analysis.get('systematic_errors', [])
    
    # Property: Should be grouped as one systematic error
    assert len(systematic_errors) == 1, \
        f"Expected 1 systematic error (case-insensitive), got {len(systematic_errors)}"
    assert systematic_errors[0]['frequency'] == 3, \
        f"Expected frequency 3, got {systematic_errors[0]['frequency']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

