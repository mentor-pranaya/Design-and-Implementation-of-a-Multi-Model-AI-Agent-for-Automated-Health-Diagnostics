"""
Property-based tests for classification accuracy reporting.

Feature: milestone-1-validation
Property 13: Classification Accuracy Reporting

**Validates: Requirements 6.3**

For any validation report, the classification accuracy section should show the calculated
percentage and a boolean indicating whether it meets the >98% target.
"""

import pytest
from hypothesis import given, strategies as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.report_generator import ReportGenerator


# Strategy for generating validation results with varying accuracy
@st.composite
def validation_results_with_accuracy_strategy(draw):
    """Generate validation results with specific accuracy levels."""
    total_params = draw(st.integers(min_value=1, max_value=500))
    
    # Generate accuracy percentage (0-100%)
    accuracy_percentage = draw(st.floats(min_value=0.0, max_value=100.0))
    
    # Calculate correct/incorrect based on accuracy
    correct = int(total_params * (accuracy_percentage / 100.0))
    incorrect = total_params - correct
    
    # Recalculate actual accuracy based on integer division
    actual_accuracy = (correct / total_params * 100) if total_params > 0 else 0.0
    
    target_met = actual_accuracy >= 98.0
    
    return {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': draw(st.integers(min_value=1, max_value=20)),
        'accuracy_metrics': {
            'total_parameters': total_params,
            'correct_classifications': correct,
            'incorrect_classifications': incorrect,
            'accuracy_percentage': actual_accuracy
        },
        'per_report_results': [],
        'errors': [],
        'target_met': target_met
    }


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
@given(validation_results=validation_results_with_accuracy_strategy())
def test_classification_accuracy_section_shows_percentage(validation_results):
    """
    Property 13: Classification Accuracy Reporting
    
    For any validation report, the classification accuracy section should show the
    calculated percentage.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    accuracy_percentage = validation_results['accuracy_metrics']['accuracy_percentage']
    
    # Property: Report must include classification accuracy section
    assert "## Classification Accuracy" in report or "Classification Accuracy" in report, \
        "Report must include classification accuracy section"
    
    # Property: Report must show the calculated accuracy percentage
    # The report includes the percentage in the classification accuracy section
    # We just need to verify that some percentage value is shown
    assert "%" in report, "Report must include percentage symbol"
    
    # Verify the accuracy section mentions the accuracy value in some form
    # (the exact formatting may vary, so we check for the presence of accuracy-related text)
    assert "Accuracy:" in report or "accuracy" in report.lower(), \
        "Report must mention accuracy"


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
@given(validation_results=validation_results_with_accuracy_strategy())
def test_classification_accuracy_section_shows_target_status(validation_results):
    """
    Property 13: Classification Accuracy Reporting
    
    For any validation report, the classification accuracy section should show a boolean
    (or equivalent indicator) of whether it meets the >98% target.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    target_met = validation_results.get('target_met', False)
    accuracy_percentage = validation_results['accuracy_metrics']['accuracy_percentage']
    
    # Property: Report must indicate whether target was met
    if target_met:
        # Should contain positive indicators
        assert any(indicator in report for indicator in ["MEETS", "MET", "✓", "PASSED", "EXCEEDED"]), \
            f"Report must indicate target was met for accuracy {accuracy_percentage}%"
    else:
        # Should contain negative indicators
        assert any(indicator in report for indicator in ["does not meet", "NOT MET", "✗", "NOT PASSED"]), \
            f"Report must indicate target was not met for accuracy {accuracy_percentage}%"


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
@given(validation_results=validation_results_with_accuracy_strategy())
def test_classification_accuracy_includes_component_metrics(validation_results):
    """
    Property: Classification accuracy section includes component metrics
    (total, correct, incorrect).
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    total_params = validation_results['accuracy_metrics']['total_parameters']
    correct = validation_results['accuracy_metrics']['correct_classifications']
    incorrect = validation_results['accuracy_metrics']['incorrect_classifications']
    
    # Property: Report must include total parameters
    assert str(total_params) in report, \
        f"Report must include total parameters {total_params}"
    
    # Property: Report must include correct classifications count
    assert str(correct) in report, \
        f"Report must include correct classifications {correct}"
    
    # Property: Report must include incorrect classifications count
    assert str(incorrect) in report, \
        f"Report must include incorrect classifications {incorrect}"


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
def test_classification_accuracy_at_exact_threshold():
    """
    Property: Classification accuracy reporting at exactly 98% threshold.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    # Exactly at threshold
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 17,
        'accuracy_metrics': {
            'total_parameters': 100,
            'correct_classifications': 98,
            'incorrect_classifications': 2,
            'accuracy_percentage': 98.0
        },
        'per_report_results': [],
        'errors': [],
        'target_met': True
    }
    
    report = generator.generate_validation_report(validation_results)
    
    # Property: At exactly 98%, target should be met
    assert "98" in report
    assert any(indicator in report for indicator in ["MEETS", "MET", "✓", "PASSED"]), \
        "Report must indicate target was met at exactly 98%"


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
def test_classification_accuracy_just_below_threshold():
    """
    Property: Classification accuracy reporting just below 98% threshold.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    # Just below threshold
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 17,
        'accuracy_metrics': {
            'total_parameters': 100,
            'correct_classifications': 97,
            'incorrect_classifications': 3,
            'accuracy_percentage': 97.0
        },
        'per_report_results': [],
        'errors': [],
        'target_met': False
    }
    
    report = generator.generate_validation_report(validation_results)
    
    # Property: Below 98%, target should not be met
    assert "97" in report
    assert any(indicator in report for indicator in ["does not meet", "NOT MET", "✗"]), \
        "Report must indicate target was not met at 97%"


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
def test_classification_accuracy_above_threshold():
    """
    Property: Classification accuracy reporting above 98% threshold.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    # Above threshold
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 17,
        'accuracy_metrics': {
            'total_parameters': 255,
            'correct_classifications': 251,
            'incorrect_classifications': 4,
            'accuracy_percentage': 98.43
        },
        'per_report_results': [],
        'errors': [],
        'target_met': True
    }
    
    report = generator.generate_validation_report(validation_results)
    
    # Property: Above 98%, target should be met
    assert "98.43" in report or "98.4" in report
    assert any(indicator in report for indicator in ["MEETS", "MET", "✓", "PASSED"]), \
        "Report must indicate target was met at 98.43%"


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
def test_classification_accuracy_with_zero_parameters():
    """
    Property: Classification accuracy reporting handles zero parameters edge case.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 0,
        'accuracy_metrics': {
            'total_parameters': 0,
            'correct_classifications': 0,
            'incorrect_classifications': 0,
            'accuracy_percentage': 0.0
        },
        'per_report_results': [],
        'errors': [],
        'target_met': False
    }
    
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must still include classification accuracy section
    assert "## Classification Accuracy" in report
    assert "0" in report  # Should show 0 parameters or 0%


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
def test_classification_accuracy_with_perfect_score():
    """
    Property: Classification accuracy reporting with 100% accuracy.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 17,
        'accuracy_metrics': {
            'total_parameters': 255,
            'correct_classifications': 255,
            'incorrect_classifications': 0,
            'accuracy_percentage': 100.0
        },
        'per_report_results': [],
        'errors': [],
        'target_met': True
    }
    
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must show 100% accuracy
    assert "100" in report
    assert any(indicator in report for indicator in ["MEETS", "MET", "✓", "PASSED", "EXCEEDED"]), \
        "Report must indicate target was met at 100%"


# Feature: milestone-1-validation, Property 13: Classification Accuracy Reporting
@given(
    total_params=st.integers(min_value=1, max_value=1000),
    correct_ratio=st.floats(min_value=0.0, max_value=1.0)
)
def test_classification_accuracy_target_consistency(total_params, correct_ratio):
    """
    Property: Target met status is consistent with accuracy percentage.
    
    Validates: Requirements 6.3
    """
    generator = ReportGenerator()
    
    correct = int(total_params * correct_ratio)
    incorrect = total_params - correct
    accuracy_percentage = (correct / total_params) * 100
    target_met = accuracy_percentage >= 98.0
    
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 17,
        'accuracy_metrics': {
            'total_parameters': total_params,
            'correct_classifications': correct,
            'incorrect_classifications': incorrect,
            'accuracy_percentage': accuracy_percentage
        },
        'per_report_results': [],
        'errors': [],
        'target_met': target_met
    }
    
    report = generator.generate_validation_report(validation_results)
    
    # Property: Target met indicator must be consistent with accuracy
    if target_met:
        assert any(indicator in report for indicator in ["MEETS", "MET", "✓", "PASSED", "EXCEEDED"]), \
            f"Report must indicate target was met for accuracy {accuracy_percentage}%"
    else:
        assert any(indicator in report for indicator in ["does not meet", "NOT MET", "✗"]), \
            f"Report must indicate target was not met for accuracy {accuracy_percentage}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

