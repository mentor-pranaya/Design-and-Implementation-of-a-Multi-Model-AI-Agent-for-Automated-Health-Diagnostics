"""
Property-based tests for accuracy calculation completeness.

Feature: milestone-1-validation
Property 7: Accuracy Calculation Completeness

**Validates: Requirements 4.4**

For any accuracy calculation result, it should include total_parameters,
correct_classifications, incorrect_classifications, and overall_accuracy_percentage.
"""

import pytest
from hypothesis import given, strategies as st, assume
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.validation_pipeline import ValidationPipeline


# Strategy for generating comparison results
@st.composite
def comparison_result_strategy(draw):
    """Generate a valid comparison result."""
    total_gt = draw(st.integers(min_value=0, max_value=50))
    correct = draw(st.integers(min_value=0, max_value=total_gt))
    incorrect = total_gt - correct
    
    return {
        'total_ground_truth': total_gt,
        'total_system': draw(st.integers(min_value=0, max_value=50)),
        'correct': correct,
        'incorrect': incorrect,
        'matches': [{'parameter': f'param_{i}'} for i in range(correct)],
        'mismatches': [{'parameter': f'param_{i}'} for i in range(incorrect)],
        'missing_in_system': [],
        'extra_in_system': []
    }


# Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
@given(comparisons=st.lists(comparison_result_strategy(), min_size=0, max_size=20))
def test_accuracy_calculation_completeness(comparisons):
    """
    Property 7: Accuracy Calculation Completeness
    
    For any accuracy calculation result, it should include total_parameters,
    correct_classifications, incorrect_classifications, and overall_accuracy_percentage.
    
    Validates: Requirements 4.4
    """
    pipeline = ValidationPipeline()
    
    # Calculate accuracy
    result = pipeline.calculate_accuracy(comparisons)
    
    # Property: Result must have all required fields
    assert 'total_parameters' in result, "Missing total_parameters field"
    assert 'correct_classifications' in result, "Missing correct_classifications field"
    assert 'incorrect_classifications' in result, "Missing incorrect_classifications field"
    assert 'accuracy_percentage' in result, "Missing accuracy_percentage field"
    
    # Property: All fields must be numeric
    assert isinstance(result['total_parameters'], int), "total_parameters must be integer"
    assert isinstance(result['correct_classifications'], int), "correct_classifications must be integer"
    assert isinstance(result['incorrect_classifications'], int), "incorrect_classifications must be integer"
    assert isinstance(result['accuracy_percentage'], (int, float)), "accuracy_percentage must be numeric"
    
    # Property: Values must be non-negative
    assert result['total_parameters'] >= 0, "total_parameters must be non-negative"
    assert result['correct_classifications'] >= 0, "correct_classifications must be non-negative"
    assert result['incorrect_classifications'] >= 0, "incorrect_classifications must be non-negative"
    assert result['accuracy_percentage'] >= 0, "accuracy_percentage must be non-negative"
    
    # Property: Accuracy percentage must be between 0 and 100
    assert 0 <= result['accuracy_percentage'] <= 100, "accuracy_percentage must be between 0 and 100"
    
    # Property: correct + incorrect should equal total (when total > 0)
    if result['total_parameters'] > 0:
        assert result['correct_classifications'] + result['incorrect_classifications'] == result['total_parameters'], \
            "correct + incorrect must equal total"
    
    # Property: Accuracy percentage calculation should be correct
    if result['total_parameters'] > 0:
        expected_accuracy = (result['correct_classifications'] / result['total_parameters']) * 100
        assert abs(result['accuracy_percentage'] - expected_accuracy) < 0.01, \
            "accuracy_percentage calculation is incorrect"
    else:
        assert result['accuracy_percentage'] == 0.0, "accuracy_percentage should be 0 when no parameters"


# Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
@given(
    total=st.integers(min_value=1, max_value=1000),
    correct_ratio=st.floats(min_value=0.0, max_value=1.0)
)
def test_accuracy_percentage_bounds(total, correct_ratio):
    """
    Property: Accuracy percentage is always between 0 and 100.
    
    Validates: Requirements 4.4
    """
    pipeline = ValidationPipeline()
    
    correct = int(total * correct_ratio)
    incorrect = total - correct
    
    comparisons = [{
        'total_ground_truth': total,
        'total_system': total,
        'correct': correct,
        'incorrect': incorrect,
        'matches': [],
        'mismatches': [],
        'missing_in_system': [],
        'extra_in_system': []
    }]
    
    result = pipeline.calculate_accuracy(comparisons)
    
    # Property: Accuracy must be within valid bounds
    assert 0 <= result['accuracy_percentage'] <= 100, \
        f"Accuracy {result['accuracy_percentage']}% is out of bounds [0, 100]"


# Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
@given(st.lists(comparison_result_strategy(), min_size=1, max_size=10))
def test_accuracy_aggregation_correctness(comparisons):
    """
    Property: Accuracy calculation correctly aggregates multiple comparisons.
    
    Validates: Requirements 4.4
    """
    pipeline = ValidationPipeline()
    
    # Calculate expected totals
    expected_total = sum(c['total_ground_truth'] for c in comparisons)
    expected_correct = sum(c['correct'] for c in comparisons)
    expected_incorrect = sum(c['incorrect'] for c in comparisons)
    
    # Calculate accuracy
    result = pipeline.calculate_accuracy(comparisons)
    
    # Property: Aggregation must be correct
    assert result['total_parameters'] == expected_total, \
        f"Expected total {expected_total}, got {result['total_parameters']}"
    assert result['correct_classifications'] == expected_correct, \
        f"Expected correct {expected_correct}, got {result['correct_classifications']}"
    assert result['incorrect_classifications'] == expected_incorrect, \
        f"Expected incorrect {expected_incorrect}, got {result['incorrect_classifications']}"


# Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
def test_accuracy_calculation_empty_list():
    """
    Property: Accuracy calculation handles empty comparison list.
    
    Validates: Requirements 4.4
    """
    pipeline = ValidationPipeline()
    
    result = pipeline.calculate_accuracy([])
    
    # Property: Empty list should return zero values
    assert result['total_parameters'] == 0
    assert result['correct_classifications'] == 0
    assert result['incorrect_classifications'] == 0
    assert result['accuracy_percentage'] == 0.0


# Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
def test_accuracy_calculation_perfect_score():
    """
    Property: 100% accuracy when all classifications are correct.
    
    Validates: Requirements 4.4
    """
    pipeline = ValidationPipeline()
    
    comparisons = [{
        'total_ground_truth': 10,
        'total_system': 10,
        'correct': 10,
        'incorrect': 0,
        'matches': [{'parameter': f'param_{i}'} for i in range(10)],
        'mismatches': [],
        'missing_in_system': [],
        'extra_in_system': []
    }]
    
    result = pipeline.calculate_accuracy(comparisons)
    
    # Property: Perfect score should be 100%
    assert result['accuracy_percentage'] == 100.0
    assert result['correct_classifications'] == 10
    assert result['incorrect_classifications'] == 0


# Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
def test_accuracy_calculation_zero_score():
    """
    Property: 0% accuracy when all classifications are incorrect.
    
    Validates: Requirements 4.4
    """
    pipeline = ValidationPipeline()
    
    comparisons = [{
        'total_ground_truth': 10,
        'total_system': 10,
        'correct': 0,
        'incorrect': 10,
        'matches': [],
        'mismatches': [{'parameter': f'param_{i}'} for i in range(10)],
        'missing_in_system': [],
        'extra_in_system': []
    }]
    
    result = pipeline.calculate_accuracy(comparisons)
    
    # Property: Zero correct should be 0%
    assert result['accuracy_percentage'] == 0.0
    assert result['correct_classifications'] == 0
    assert result['incorrect_classifications'] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

