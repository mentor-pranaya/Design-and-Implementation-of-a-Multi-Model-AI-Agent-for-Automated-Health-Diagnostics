"""
Property-Based Tests for Accuracy Calculation Completeness

Feature: milestone-1-validation
Property 7: Accuracy Calculation Completeness
Validates: Requirements 4.4

Tests that for any accuracy calculation result, it should include total_parameters,
correct_classifications, incorrect_classifications, and overall_accuracy_percentage.
"""

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
def comparison_result_strategy(draw):
    """Generate a single comparison result from compare_classifications."""
    # Generate counts
    total_ground_truth = draw(st.integers(min_value=0, max_value=50))
    correct = draw(st.integers(min_value=0, max_value=total_ground_truth))
    incorrect = total_ground_truth - correct
    
    # Generate parameter names for mismatches, missing, and extra
    param_names = [f"param_{i}" for i in range(total_ground_truth + 10)]
    
    num_mismatches = draw(st.integers(min_value=0, max_value=incorrect))
    num_missing = draw(st.integers(min_value=0, max_value=5))
    num_extra = draw(st.integers(min_value=0, max_value=5))
    
    mismatches = [
        {
            "parameter": draw(st.sampled_from(param_names)),
            "system_classification": draw(st.sampled_from(["Normal", "High", "Low"])),
            "ground_truth_classification": draw(st.sampled_from(["Normal", "High", "Low"]))
        }
        for _ in range(num_mismatches)
    ]
    
    missing_in_system = [
        {"parameter": draw(st.sampled_from(param_names))}
        for _ in range(num_missing)
    ]
    
    extra_in_system = [
        {"parameter": draw(st.sampled_from(param_names))}
        for _ in range(num_extra)
    ]
    
    return {
        "report_id": f"report_{draw(st.integers(min_value=1, max_value=999)):03d}",
        "total_ground_truth": total_ground_truth,
        "correct": correct,
        "incorrect": incorrect,
        "mismatches": mismatches,
        "missing_in_system": missing_in_system,
        "extra_in_system": extra_in_system
    }


@st.composite
def comparisons_list_strategy(draw):
    """Generate a list of comparison results."""
    num_comparisons = draw(st.integers(min_value=1, max_value=20))
    comparisons = [draw(comparison_result_strategy()) for _ in range(num_comparisons)]
    return comparisons


# ============================================================================
# Property Tests
# ============================================================================

class TestAccuracyCalculationCompleteness:
    """
    Property 7: Accuracy Calculation Completeness
    
    **Validates: Requirements 4.4**
    
    For any accuracy calculation result, it should include total_parameters,
    correct_classifications, incorrect_classifications, and overall_accuracy_percentage.
    """
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_accuracy_result_has_all_required_fields(self, comparisons):
        """Property: Accuracy result must contain all required fields."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        # Requirement 4.4: Must include all required metrics
        required_fields = [
            "total_parameters",
            "correct_classifications",
            "incorrect_classifications",
            "accuracy_percentage"
        ]
        
        for field in required_fields:
            assert field in result, \
                f"Accuracy result must contain '{field}' field"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_total_parameters_is_non_negative_integer(self, comparisons):
        """Property: total_parameters must be a non-negative integer."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        total_params = result["total_parameters"]
        assert isinstance(total_params, int), \
            f"total_parameters must be an integer, got {type(total_params)}"
        assert total_params >= 0, \
            f"total_parameters must be non-negative, got {total_params}"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_correct_classifications_is_non_negative_integer(self, comparisons):
        """Property: correct_classifications must be a non-negative integer."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        correct = result["correct_classifications"]
        assert isinstance(correct, int), \
            f"correct_classifications must be an integer, got {type(correct)}"
        assert correct >= 0, \
            f"correct_classifications must be non-negative, got {correct}"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_incorrect_classifications_is_non_negative_integer(self, comparisons):
        """Property: incorrect_classifications must be a non-negative integer."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        incorrect = result["incorrect_classifications"]
        assert isinstance(incorrect, int), \
            f"incorrect_classifications must be an integer, got {type(incorrect)}"
        assert incorrect >= 0, \
            f"incorrect_classifications must be non-negative, got {incorrect}"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_accuracy_percentage_is_valid_float(self, comparisons):
        """Property: accuracy_percentage must be a float between 0 and 100."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        accuracy = result["accuracy_percentage"]
        assert isinstance(accuracy, (int, float)), \
            f"accuracy_percentage must be numeric, got {type(accuracy)}"
        assert 0.0 <= accuracy <= 100.0, \
            f"accuracy_percentage must be between 0 and 100, got {accuracy}"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_correct_plus_incorrect_equals_total(self, comparisons):
        """Property: correct + incorrect should equal total_parameters."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        total = result["total_parameters"]
        correct = result["correct_classifications"]
        incorrect = result["incorrect_classifications"]
        
        assert correct + incorrect == total, \
            f"correct ({correct}) + incorrect ({incorrect}) must equal total ({total})"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_accuracy_percentage_calculation_is_correct(self, comparisons):
        """Property: accuracy_percentage should be correctly calculated from counts."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        total = result["total_parameters"]
        correct = result["correct_classifications"]
        accuracy = result["accuracy_percentage"]
        
        if total > 0:
            expected_accuracy = round((correct / total) * 100, 2)
            assert accuracy == expected_accuracy, \
                f"accuracy_percentage ({accuracy}) should equal (correct/total)*100 ({expected_accuracy})"
        else:
            # When total is 0, accuracy should be 0.0
            assert accuracy == 0.0, \
                f"accuracy_percentage should be 0.0 when total_parameters is 0, got {accuracy}"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_total_parameters_aggregates_correctly(self, comparisons):
        """Property: total_parameters should be sum of all comparison totals."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        expected_total = sum(comp["total_ground_truth"] for comp in comparisons)
        actual_total = result["total_parameters"]
        
        assert actual_total == expected_total, \
            f"total_parameters ({actual_total}) should equal sum of all comparison totals ({expected_total})"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_correct_classifications_aggregates_correctly(self, comparisons):
        """Property: correct_classifications should be sum of all comparison correct counts."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        expected_correct = sum(comp["correct"] for comp in comparisons)
        actual_correct = result["correct_classifications"]
        
        assert actual_correct == expected_correct, \
            f"correct_classifications ({actual_correct}) should equal sum of all comparison correct counts ({expected_correct})"
    
    # Feature: milestone-1-validation, Property 7: Accuracy Calculation Completeness
    @given(comparisons=comparisons_list_strategy())
    @settings(max_examples=20, deadline=None)
    def test_incorrect_classifications_aggregates_correctly(self, comparisons):
        """Property: incorrect_classifications should be sum of all comparison incorrect counts."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        expected_incorrect = sum(comp["incorrect"] for comp in comparisons)
        actual_incorrect = result["incorrect_classifications"]
        
        assert actual_incorrect == expected_incorrect, \
            f"incorrect_classifications ({actual_incorrect}) should equal sum of all comparison incorrect counts ({expected_incorrect})"


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestAccuracyCalculationEdgeCases:
    """Test edge cases for accuracy calculation."""
    
    def test_empty_comparisons_list(self):
        """Test accuracy calculation with empty comparisons list."""
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy([])
        
        assert result["total_parameters"] == 0
        assert result["correct_classifications"] == 0
        assert result["incorrect_classifications"] == 0
        assert result["accuracy_percentage"] == 0.0
    
    def test_all_correct_classifications(self):
        """Test accuracy calculation when all classifications are correct."""
        comparisons = [
            {
                "report_id": "report_001",
                "total_ground_truth": 10,
                "correct": 10,
                "incorrect": 0,
                "mismatches": [],
                "missing_in_system": [],
                "extra_in_system": []
            }
        ]
        
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        assert result["total_parameters"] == 10
        assert result["correct_classifications"] == 10
        assert result["incorrect_classifications"] == 0
        assert result["accuracy_percentage"] == 100.0
    
    def test_all_incorrect_classifications(self):
        """Test accuracy calculation when all classifications are incorrect."""
        comparisons = [
            {
                "report_id": "report_001",
                "total_ground_truth": 10,
                "correct": 0,
                "incorrect": 10,
                "mismatches": [{"parameter": f"param_{i}"} for i in range(10)],
                "missing_in_system": [],
                "extra_in_system": []
            }
        ]
        
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        assert result["total_parameters"] == 10
        assert result["correct_classifications"] == 0
        assert result["incorrect_classifications"] == 10
        assert result["accuracy_percentage"] == 0.0
    
    def test_mixed_results_across_multiple_reports(self):
        """Test accuracy calculation with mixed results across multiple reports."""
        comparisons = [
            {
                "report_id": "report_001",
                "total_ground_truth": 10,
                "correct": 8,
                "incorrect": 2,
                "mismatches": [{"parameter": "param_1"}, {"parameter": "param_2"}],
                "missing_in_system": [],
                "extra_in_system": []
            },
            {
                "report_id": "report_002",
                "total_ground_truth": 15,
                "correct": 14,
                "incorrect": 1,
                "mismatches": [{"parameter": "param_3"}],
                "missing_in_system": [],
                "extra_in_system": []
            },
            {
                "report_id": "report_003",
                "total_ground_truth": 5,
                "correct": 5,
                "incorrect": 0,
                "mismatches": [],
                "missing_in_system": [],
                "extra_in_system": []
            }
        ]
        
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        assert result["total_parameters"] == 30
        assert result["correct_classifications"] == 27
        assert result["incorrect_classifications"] == 3
        assert result["accuracy_percentage"] == 90.0
    
    def test_single_parameter_report(self):
        """Test accuracy calculation with a single parameter."""
        comparisons = [
            {
                "report_id": "report_001",
                "total_ground_truth": 1,
                "correct": 1,
                "incorrect": 0,
                "mismatches": [],
                "missing_in_system": [],
                "extra_in_system": []
            }
        ]
        
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        assert result["total_parameters"] == 1
        assert result["correct_classifications"] == 1
        assert result["incorrect_classifications"] == 0
        assert result["accuracy_percentage"] == 100.0
    
    def test_accuracy_percentage_rounding(self):
        """Test that accuracy percentage is rounded to 2 decimal places."""
        comparisons = [
            {
                "report_id": "report_001",
                "total_ground_truth": 3,
                "correct": 2,
                "incorrect": 1,
                "mismatches": [{"parameter": "param_1"}],
                "missing_in_system": [],
                "extra_in_system": []
            }
        ]
        
        pipeline = ValidationPipeline(reference_manager=None)
        result = pipeline.calculate_accuracy(comparisons)
        
        # 2/3 * 100 = 66.666... should be rounded to 66.67
        assert result["accuracy_percentage"] == 66.67


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

