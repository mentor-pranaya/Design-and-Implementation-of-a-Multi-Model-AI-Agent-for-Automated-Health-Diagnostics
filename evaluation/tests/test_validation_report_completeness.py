"""
Property-based tests for validation report completeness.

Feature: milestone-1-validation
Property 12: Validation Report Completeness

**Validates: Requirements 6.1, 6.4**

For any generated validation report, it should include sections for extraction accuracy,
classification accuracy, per-report results, and milestone status.
"""

import pytest
from hypothesis import given, strategies as st, assume
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.report_generator import ReportGenerator


# Strategy for generating validation results
@st.composite
def validation_results_strategy(draw):
    """Generate valid validation results for testing."""
    total_params = draw(st.integers(min_value=0, max_value=500))
    correct = draw(st.integers(min_value=0, max_value=total_params))
    incorrect = total_params - correct
    
    accuracy_percentage = (correct / total_params * 100) if total_params > 0 else 0.0
    target_met = accuracy_percentage >= 98.0
    
    # Generate per-report results
    num_reports = draw(st.integers(min_value=0, max_value=20))
    per_report_results = []
    
    for i in range(num_reports):
        report_params = draw(st.integers(min_value=0, max_value=50))
        report_correct = draw(st.integers(min_value=0, max_value=report_params))
        report_incorrect = report_params - report_correct
        report_accuracy = (report_correct / report_params * 100) if report_params > 0 else 0.0
        
        per_report_results.append({
            'report_id': f'report_{i+1:03d}',
            'total_parameters': report_params,
            'correct': report_correct,
            'incorrect': report_incorrect,
            'accuracy': report_accuracy
        })
    
    return {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': num_reports,
        'accuracy_metrics': {
            'total_parameters': total_params,
            'correct_classifications': correct,
            'incorrect_classifications': incorrect,
            'accuracy_percentage': accuracy_percentage
        },
        'per_report_results': per_report_results,
        'errors': [],
        'target_met': target_met
    }


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
@given(validation_results=validation_results_strategy())
def test_validation_report_has_all_required_sections(validation_results):
    """
    Property 12: Validation Report Completeness
    
    For any generated validation report, it should include sections for extraction accuracy,
    classification accuracy, per-report results, and milestone status.
    
    Validates: Requirements 6.1, 6.4
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must be a non-empty string
    assert isinstance(report, str), "Report must be a string"
    assert len(report) > 0, "Report must not be empty"
    
    # Property: Report must include extraction accuracy section (Requirement 6.1)
    assert "## Extraction Accuracy" in report or "Extraction Accuracy" in report, \
        "Report must include extraction accuracy section"
    
    # Property: Report must include classification accuracy section (Requirement 6.1)
    assert "## Classification Accuracy" in report or "Classification Accuracy" in report, \
        "Report must include classification accuracy section"
    
    # Property: Report must include per-report results section (Requirement 6.4)
    assert "## Per-Report Results" in report or "Per-Report Results" in report, \
        "Report must include per-report results section"
    
    # Property: Report must include milestone status (Requirement 6.1)
    assert "Milestone 1 Status" in report or "MILESTONE 1" in report or "Status:" in report, \
        "Report must include milestone status"


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
@given(validation_results=validation_results_strategy())
def test_validation_report_includes_extraction_metrics(validation_results):
    """
    Property: Validation report includes extraction accuracy metrics.
    
    Validates: Requirements 6.1, 6.2
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must mention extraction accuracy percentage
    assert "100%" in report or "Extraction Accuracy" in report, \
        "Report must include extraction accuracy percentage"
    
    # Property: Report must mention reports processed
    assert "Reports Processed" in report or "reports processed" in report.lower(), \
        "Report must include reports processed count"


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
@given(validation_results=validation_results_strategy())
def test_validation_report_includes_classification_metrics(validation_results):
    """
    Property: Validation report includes classification accuracy metrics.
    
    Validates: Requirements 6.1, 6.3
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    accuracy_percentage = validation_results['accuracy_metrics']['accuracy_percentage']
    
    # Property: Report must include classification accuracy percentage
    assert f"{accuracy_percentage:.2f}%" in report or f"{accuracy_percentage:.1f}%" in report or \
           "Classification Accuracy" in report, \
        "Report must include classification accuracy percentage"
    
    # Property: Report must mention total parameters
    total_params = validation_results['accuracy_metrics']['total_parameters']
    if total_params > 0:
        assert "Total Parameters" in report or "total parameters" in report.lower(), \
            "Report must include total parameters count"
    
    # Property: Report must mention correct classifications
    correct = validation_results['accuracy_metrics']['correct_classifications']
    if correct > 0:
        assert "Correct Classifications" in report or "correct" in report.lower(), \
            "Report must include correct classifications count"


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
@given(validation_results=validation_results_strategy())
def test_validation_report_includes_per_report_table(validation_results):
    """
    Property: Validation report includes per-report results table.
    
    Validates: Requirements 6.4
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    per_report_results = validation_results.get('per_report_results', [])
    
    if len(per_report_results) > 0:
        # Property: Report must include table headers for per-report results
        assert "Report ID" in report or "report_id" in report.lower(), \
            "Report must include Report ID column"
        assert "Parameters" in report or "parameters" in report.lower(), \
            "Report must include Parameters column"
        assert "Accuracy" in report or "accuracy" in report.lower(), \
            "Report must include Accuracy column"
        
        # Property: Report must include at least one report ID from the results
        first_report_id = per_report_results[0]['report_id']
        assert first_report_id in report, \
            f"Report must include report ID {first_report_id}"


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
@given(validation_results=validation_results_strategy())
def test_validation_report_includes_milestone_status(validation_results):
    """
    Property: Validation report includes milestone status (pass/fail).
    
    Validates: Requirements 6.1
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    target_met = validation_results.get('target_met', False)
    
    # Property: Report must indicate whether milestone target was met
    if target_met:
        assert "PASSED" in report or "MET" in report or "✓" in report, \
            "Report must indicate milestone target was met"
    else:
        assert "NOT MET" in report or "✗" in report or "does not meet" in report, \
            "Report must indicate milestone target was not met"


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
@given(validation_results=validation_results_strategy())
def test_validation_report_has_proper_structure(validation_results):
    """
    Property: Validation report has proper markdown structure.
    
    Validates: Requirements 6.1
    """
    generator = ReportGenerator()
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must have a title
    assert report.startswith("#") or "Milestone 1 Validation Report" in report, \
        "Report must have a title"
    
    # Property: Report must have multiple sections (indicated by ##)
    section_count = report.count("##")
    assert section_count >= 3, \
        f"Report must have at least 3 sections, found {section_count}"
    
    # Property: Report must have proper markdown formatting
    assert "\n" in report, "Report must have line breaks"


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
def test_validation_report_with_zero_parameters():
    """
    Property: Validation report handles edge case of zero parameters.
    
    Validates: Requirements 6.1
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
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must still be generated with all sections
    assert "## Extraction Accuracy" in report
    assert "## Classification Accuracy" in report
    assert "## Per-Report Results" in report
    assert len(report) > 0


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
def test_validation_report_with_perfect_accuracy():
    """
    Property: Validation report correctly shows 100% accuracy.
    
    Validates: Requirements 6.1, 6.3
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
        'per_report_results': [
            {
                'report_id': 'report_001',
                'total_parameters': 15,
                'correct': 15,
                'incorrect': 0,
                'accuracy': 100.0
            }
        ],
        'errors': [],
        'target_met': True
    }
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must show 100% accuracy
    assert "100.0%" in report or "100%" in report
    assert "PASSED" in report or "MET" in report or "✓" in report


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
def test_validation_report_with_errors():
    """
    Property: Validation report includes error information when errors exist.
    
    Validates: Requirements 6.1
    """
    generator = ReportGenerator()
    
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 15,
        'accuracy_metrics': {
            'total_parameters': 200,
            'correct_classifications': 195,
            'incorrect_classifications': 5,
            'accuracy_percentage': 97.5
        },
        'per_report_results': [],
        'errors': [
            {
                'report_id': 'report_005',
                'error': 'Failed to extract parameters'
            },
            {
                'report_id': 'report_012',
                'error': 'OCR failure'
            }
        ],
        'target_met': False
    }
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must include error section when errors exist
    assert "Error" in report or "error" in report.lower()
    assert "report_005" in report
    assert "report_012" in report


# Feature: milestone-1-validation, Property 12: Validation Report Completeness
@given(
    total_params=st.integers(min_value=1, max_value=1000),
    accuracy_ratio=st.floats(min_value=0.0, max_value=1.0)
)
def test_validation_report_accuracy_consistency(total_params, accuracy_ratio):
    """
    Property: Validation report accuracy values are mathematically consistent.
    
    Validates: Requirements 6.1, 6.3
    """
    generator = ReportGenerator()
    
    correct = int(total_params * accuracy_ratio)
    incorrect = total_params - correct
    accuracy_percentage = (correct / total_params) * 100
    
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
        'target_met': accuracy_percentage >= 98.0
    }
    
    # Generate validation report
    report = generator.generate_validation_report(validation_results)
    
    # Property: Report must include the accuracy percentage (in some format)
    # The report may include full precision or rounded values
    accuracy_str = str(accuracy_percentage)
    assert accuracy_str in report or f"{accuracy_percentage:.2f}%" in report or \
           f"{accuracy_percentage:.1f}%" in report or f"{accuracy_percentage:.0f}%" in report, \
        f"Report must include accuracy percentage {accuracy_percentage}%"
    
    # Property: Report must include total parameters
    assert str(total_params) in report, \
        f"Report must include total parameters {total_params}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

