"""
Property-based tests for certification document completeness.

Feature: milestone-1-validation
Property 18: Certification Document Completeness

**Validates: Requirements 10.2**

For any generated certification document, it should include achievement date, final metrics,
evidence reference, and technical achievements summary.
"""

import pytest
from hypothesis import given, strategies as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.report_generator import ReportGenerator


# Strategy for generating validation results that meet targets
@st.composite
def passing_validation_results_strategy(draw):
    """Generate validation results that meet the >98% target."""
    total_params = draw(st.integers(min_value=50, max_value=500))
    
    # Generate correct count that ensures >= 98% accuracy
    # For 98% accuracy, we need correct/total >= 0.98
    min_correct = int(total_params * 0.98) + (1 if total_params * 0.98 % 1 > 0 else 0)
    correct = draw(st.integers(min_value=min_correct, max_value=total_params))
    incorrect = total_params - correct
    
    # Calculate actual accuracy
    actual_accuracy = (correct / total_params * 100) if total_params > 0 else 0.0
    
    # Ensure target is met (should always be true with our constraints)
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


# Strategy for generating validation results that don't meet targets
@st.composite
def failing_validation_results_strategy(draw):
    """Generate validation results that don't meet the >98% target."""
    total_params = draw(st.integers(min_value=1, max_value=500))
    
    # Generate accuracy < 98%
    accuracy_percentage = draw(st.floats(min_value=0.0, max_value=97.99))
    
    correct = int(total_params * (accuracy_percentage / 100.0))
    incorrect = total_params - correct
    
    # Recalculate actual accuracy
    actual_accuracy = (correct / total_params * 100) if total_params > 0 else 0.0
    
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
        'target_met': False
    }


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=passing_validation_results_strategy())
def test_certification_includes_achievement_date(validation_results):
    """
    Property 18: Certification Document Completeness
    
    For any generated certification document, it should include achievement date.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    # Generate certification
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification must be a non-empty string
    assert isinstance(certification, str), "Certification must be a string"
    assert len(certification) > 0, "Certification must not be empty"
    
    # Property: Certification must include achievement date
    assert "Achievement Date" in certification or "Date" in certification, \
        "Certification must include achievement date"
    
    # Property: Certification should include a date in some format (YYYY-MM-DD or similar)
    import re
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    assert re.search(date_pattern, certification), \
        "Certification must include a date in YYYY-MM-DD format"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=passing_validation_results_strategy())
def test_certification_includes_final_metrics(validation_results):
    """
    Property 18: Certification Document Completeness
    
    For any generated certification document, it should include final metrics.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    # Generate certification
    certification = generator.generate_certification(validation_results)
    
    accuracy_percentage = validation_results['accuracy_metrics']['accuracy_percentage']
    
    # Property: Certification must include metrics section
    assert "Metrics" in certification or "metrics" in certification, \
        "Certification must include metrics section"
    
    # Property: Certification must include extraction accuracy
    assert "Extraction Accuracy" in certification or "extraction" in certification.lower(), \
        "Certification must include extraction accuracy"
    
    # Property: Certification must include classification accuracy
    assert "Classification Accuracy" in certification or "classification" in certification.lower(), \
        "Certification must include classification accuracy"
    
    # Property: Certification must show the actual accuracy percentage
    # The format may vary, so we check for presence of percentage and accuracy-related text
    assert "%" in certification, "Certification must include percentage symbol"
    assert "Accuracy" in certification or "accuracy" in certification, \
        "Certification must mention accuracy"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=passing_validation_results_strategy())
def test_certification_includes_evidence_reference(validation_results):
    """
    Property 18: Certification Document Completeness
    
    For any generated certification document, it should include evidence reference.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    # Generate certification
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification must include evidence section
    assert "Evidence" in certification or "evidence" in certification, \
        "Certification must include evidence section"
    
    # Property: Certification should reference validation report
    assert "Validation Report" in certification or "VALIDATION_REPORT" in certification, \
        "Certification must reference validation report"
    
    # Property: Certification should reference ground truth dataset
    assert "Ground Truth" in certification or "ground_truth" in certification, \
        "Certification must reference ground truth dataset"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=passing_validation_results_strategy())
def test_certification_includes_technical_achievements(validation_results):
    """
    Property 18: Certification Document Completeness
    
    For any generated certification document, it should include technical achievements summary.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    # Generate certification
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification must include technical achievements section
    assert "Technical Achievements" in certification or "Achievements" in certification, \
        "Certification must include technical achievements section"
    
    # Property: Certification should mention key system components
    # Based on the implementation, these should be mentioned
    key_components = [
        'Extraction',
        'Reference',
        'Indian',
        'Validation'
    ]
    
    # At least some key components should be mentioned
    assert any(component in certification for component in key_components), \
        "Certification must mention key technical components"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=passing_validation_results_strategy())
def test_certification_has_all_required_sections(validation_results):
    """
    Property: Certification document has all required sections.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    # Generate certification
    certification = generator.generate_certification(validation_results)
    
    required_sections = [
        "Achievement Date",
        "Metrics",
        "Evidence",
        "Technical Achievements"
    ]
    
    # Property: All required sections must be present
    for section in required_sections:
        assert section in certification or section.lower() in certification.lower(), \
            f"Certification must include {section} section"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=failing_validation_results_strategy())
def test_certification_not_generated_when_targets_not_met(validation_results):
    """
    Property: Certification is not generated when targets are not met.
    
    Validates: Requirements 10.1
    """
    generator = ReportGenerator()
    
    # Generate certification (should return a message instead)
    certification = generator.generate_certification(validation_results)
    
    # Property: When targets not met, should return a message (not full certification)
    assert "not" in certification.lower() or "cannot" in certification.lower(), \
        "Should indicate certification cannot be issued when targets not met"
    
    # Property: Should not include full certification sections
    assert "Sign-Off" not in certification, \
        "Should not include sign-off section when targets not met"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
def test_certification_with_exact_threshold():
    """
    Property: Certification is generated at exactly 98% threshold.
    
    Validates: Requirements 10.1, 10.2
    """
    generator = ReportGenerator()
    
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
    
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification should be generated at exactly 98%
    assert "Achievement Date" in certification
    assert "Technical Achievements" in certification
    assert "98" in certification


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
def test_certification_with_perfect_accuracy():
    """
    Property: Certification correctly shows 100% accuracy.
    
    Validates: Requirements 10.2, 10.3
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
    
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification should show 100% accuracy
    assert "100" in certification
    
    # Property: Should highlight exceeding target (Requirement 10.3)
    assert "EXCEEDED" in certification or "exceeds" in certification.lower(), \
        "Certification should highlight exceeding target"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
def test_certification_includes_sign_off_section():
    """
    Property: Certification includes sign-off section.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
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
    
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification must include sign-off section
    assert "Sign-Off" in certification or "Sign Off" in certification, \
        "Certification must include sign-off section"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
def test_certification_marks_milestone_complete():
    """
    Property: Certification marks milestone as COMPLETE.
    
    Validates: Requirements 10.5
    """
    generator = ReportGenerator()
    
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
    
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification must mark milestone as complete
    assert "COMPLETE" in certification or "complete" in certification.lower(), \
        "Certification must mark milestone as complete"
    
    # Property: Should include status indicator
    assert "Status" in certification or "status" in certification, \
        "Certification should include status section"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=passing_validation_results_strategy())
def test_certification_includes_target_comparison(validation_results):
    """
    Property: Certification compares achieved metrics against targets.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    # Generate certification
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification should mention targets
    assert "Target" in certification or "target" in certification, \
        "Certification must mention targets"
    
    # Property: Certification should show both target and achieved values
    assert "Achieved" in certification or "achieved" in certification, \
        "Certification must show achieved values"
    
    # Property: Should mention the 98% target
    assert "98" in certification, \
        "Certification must mention the 98% target"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(validation_results=passing_validation_results_strategy())
def test_certification_has_proper_structure(validation_results):
    """
    Property: Certification has proper markdown structure.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    # Generate certification
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification must have a title
    assert certification.startswith("#") or "Certification" in certification, \
        "Certification must have a title"
    
    # Property: Certification must have multiple sections (indicated by ##)
    section_count = certification.count("##")
    assert section_count >= 3, \
        f"Certification must have at least 3 sections, found {section_count}"
    
    # Property: Certification must have proper markdown formatting
    assert "\n" in certification, "Certification must have line breaks"


# Feature: milestone-1-validation, Property 18: Certification Document Completeness
@given(
    total_params=st.integers(min_value=50, max_value=500),
    accuracy=st.floats(min_value=98.0, max_value=100.0)
)
def test_certification_metrics_consistency(total_params, accuracy):
    """
    Property: Certification metrics are mathematically consistent.
    
    Validates: Requirements 10.2
    """
    generator = ReportGenerator()
    
    correct = int(total_params * (accuracy / 100.0))
    incorrect = total_params - correct
    actual_accuracy = (correct / total_params) * 100
    
    validation_results = {
        'timestamp': '2026-01-20T10:30:00',
        'reports_processed': 17,
        'accuracy_metrics': {
            'total_parameters': total_params,
            'correct_classifications': correct,
            'incorrect_classifications': incorrect,
            'accuracy_percentage': actual_accuracy
        },
        'per_report_results': [],
        'errors': [],
        'target_met': True
    }
    
    certification = generator.generate_certification(validation_results)
    
    # Property: Certification must include total parameters
    assert str(total_params) in certification, \
        f"Certification must include total parameters {total_params}"
    
    # Property: Certification must include correct classifications
    assert str(correct) in certification, \
        f"Certification must include correct classifications {correct}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

