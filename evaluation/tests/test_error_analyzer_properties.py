"""
Property-Based Tests for Error Analyzer Module

Tests universal properties that should hold across all inputs.
Uses hypothesis for property-based testing.
"""

import pytest
from hypothesis import given, strategies as st, assume, HealthCheck, settings
from evaluation.error_analyzer import ErrorAnalyzer


# Test data strategies
@st.composite
def error_dict(draw):
    """Generate a valid error dictionary."""
    parameter = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
    report_id = draw(st.text(min_size=1, max_size=20))
    
    # Generate values
    system_value = draw(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False))
    ground_truth_value = draw(st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False))
    
    # Generate reference range
    min_val = draw(st.floats(min_value=0.1, max_value=500, allow_nan=False, allow_infinity=False))
    max_val = draw(st.floats(min_value=min_val + 1, max_value=1000, allow_nan=False, allow_infinity=False))
    
    # Generate classifications
    classification = draw(st.sampled_from(['Normal', 'High', 'Low']))
    
    return {
        'parameter': parameter,
        'report_id': report_id,
        'system_value': system_value,
        'ground_truth_value': ground_truth_value,
        'system_classification': classification,
        'ground_truth_classification': draw(st.sampled_from(['Normal', 'High', 'Low'])),
        'reference_range': {'min': min_val, 'max': max_val}
    }


@st.composite
def error_list(draw, min_size=0, max_size=20):
    """Generate a list of error dictionaries."""
    return draw(st.lists(error_dict(), min_size=min_size, max_size=max_size))


class TestErrorAnalyzerProperties:
    """Property-based tests for ErrorAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ErrorAnalyzer()
    
    # Feature: milestone-1-validation, Property 9: Error Categorization Validity
    @given(error=error_dict())
    def test_categorize_error_returns_valid_category(self, error):
        """
        Property: For any error, categorization should return a valid category.
        
        **Validates: Requirements 5.2**
        """
        category = self.analyzer.categorize_error(error)
        
        # Category must be one of the valid categories
        assert category in self.analyzer.error_categories
        assert category in ['extraction_error', 'reference_range_error', 
                          'classification_logic_error', 'edge_case']
    
    # Feature: milestone-1-validation, Property 8: Error Logging Completeness
    @given(errors=error_list(min_size=1, max_size=10))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_analyze_errors_preserves_all_fields(self, errors):
        """
        Property: For any error list, analysis should preserve all required fields.
        
        **Validates: Requirements 5.1**
        """
        analysis = self.analyzer.analyze_errors(errors)
        
        # Check all categorized errors have required fields
        for category_errors in analysis['by_category'].values():
            for error in category_errors:
                assert 'parameter' in error
                assert 'report_id' in error
                assert 'system_value' in error
                assert 'ground_truth_value' in error
                assert 'system_classification' in error
                assert 'ground_truth_classification' in error
                assert 'reference_range' in error
                assert 'category' in error
    
    # Feature: milestone-1-validation, Property 10: Systematic Error Detection
    @given(
        parameter_name=st.text(min_size=1, max_size=20),
        num_errors=st.integers(min_value=3, max_value=10)
    )
    def test_systematic_error_detection_threshold(self, parameter_name, num_errors):
        """
        Property: For any parameter failing ≥3 times, it should be flagged as systematic.
        
        **Validates: Requirements 5.3**
        """
        # Create errors for the same parameter
        errors = []
        for i in range(num_errors):
            errors.append({
                'parameter': parameter_name,
                'report_id': f'report_{i:03d}',
                'system_value': 100.0,
                'ground_truth_value': 100.0,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 90}
            })
        
        systematic = self.analyzer.identify_systematic_errors(errors)
        
        # Should be flagged as systematic (≥3 occurrences)
        assert len(systematic) == 1
        assert systematic[0]['parameter'] == parameter_name.lower()
        assert systematic[0]['frequency'] == num_errors
    
    @given(errors=error_list(min_size=0, max_size=5))
    def test_systematic_error_detection_below_threshold(self, errors):
        """
        Property: For any parameter failing <3 times, it should NOT be flagged as systematic.
        
        **Validates: Requirements 5.3**
        """
        # Ensure each parameter appears at most 2 times
        seen_params = set()
        filtered_errors = []
        param_counts = {}
        
        for error in errors:
            param = error['parameter'].lower()
            count = param_counts.get(param, 0)
            if count < 2:
                filtered_errors.append(error)
                param_counts[param] = count + 1
        
        systematic = self.analyzer.identify_systematic_errors(filtered_errors)
        
        # No parameter should be flagged as systematic
        assert len(systematic) == 0
    
    # Feature: milestone-1-validation, Property 11: Edge Case Separation
    @given(
        min_val=st.floats(min_value=10, max_value=100, allow_nan=False, allow_infinity=False),
        max_val=st.floats(min_value=110, max_value=200, allow_nan=False, allow_infinity=False)
    )
    def test_edge_case_detection_near_boundaries(self, min_val, max_val):
        """
        Property: For any value within 5% of boundaries, it should be categorized as edge_case.
        
        **Validates: Requirements 5.4**
        """
        range_span = max_val - min_val
        threshold = range_span * 0.05
        
        # Test value just above minimum (within 5%)
        value_near_min = min_val + (threshold * 0.5)
        
        error = {
            'parameter': 'test_param',
            'system_value': value_near_min,
            'ground_truth_value': value_near_min,
            'system_classification': 'Low',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': min_val, 'max': max_val}
        }
        
        category = self.analyzer.categorize_error(error)
        assert category == 'edge_case'
    
    @given(errors=error_list(min_size=0, max_size=20))
    def test_analyze_errors_total_count_matches(self, errors):
        """
        Property: For any error list, total_errors should match input length.
        
        **Validates: Requirements 5.1**
        """
        analysis = self.analyzer.analyze_errors(errors)
        
        assert analysis['total_errors'] == len(errors)
    
    @given(errors=error_list(min_size=0, max_size=20))
    def test_analyze_errors_category_counts_sum_to_total(self, errors):
        """
        Property: For any error list, sum of category counts should equal total errors.
        
        **Validates: Requirements 5.2**
        """
        analysis = self.analyzer.analyze_errors(errors)
        
        category_sum = sum(analysis['category_summary'].values())
        assert category_sum == analysis['total_errors']
    
    @given(errors=error_list(min_size=1, max_size=20))
    def test_analyze_errors_always_has_recommendations(self, errors):
        """
        Property: For any non-empty error list, recommendations should be generated.
        
        **Validates: Requirements 5.5**
        """
        analysis = self.analyzer.analyze_errors(errors)
        
        assert 'recommendations' in analysis
        assert len(analysis['recommendations']) > 0
    
    @given(errors=error_list(min_size=0, max_size=20))
    def test_generate_error_report_always_returns_string(self, errors):
        """
        Property: For any error list, report generation should return a string.
        
        **Validates: Requirements 5.5**
        """
        analysis = self.analyzer.analyze_errors(errors)
        report = self.analyzer.generate_error_report(analysis)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "# Error Analysis Report" in report
    
    @given(errors=error_list(min_size=0, max_size=20))
    def test_error_report_contains_summary_section(self, errors):
        """
        Property: For any error list, report should contain summary section.
        
        **Validates: Requirements 5.5**
        """
        analysis = self.analyzer.analyze_errors(errors)
        report = self.analyzer.generate_error_report(analysis)
        
        assert "## Summary" in report
        assert f"**Total Errors:** {len(errors)}" in report
    
    @given(
        errors=error_list(min_size=1, max_size=20),
        report_id=st.text(min_size=1, max_size=20)
    )
    def test_error_report_includes_report_id_when_provided(self, errors, report_id):
        """
        Property: For any error list with report_id, report should include it.
        
        **Validates: Requirements 5.5**
        """
        analysis = self.analyzer.analyze_errors(errors)
        report = self.analyzer.generate_error_report(analysis, report_id=report_id)
        
        assert f"**Report ID:** {report_id}" in report
    
    @given(errors=error_list(min_size=0, max_size=20))
    def test_edge_cases_list_matches_category(self, errors):
        """
        Property: For any error list, edge_cases should match edge_case category.
        
        **Validates: Requirements 5.4**
        """
        analysis = self.analyzer.analyze_errors(errors)
        
        edge_cases = analysis['edge_cases']
        edge_case_category = analysis['by_category'].get('edge_case', [])
        
        assert len(edge_cases) == len(edge_case_category)
    
    @given(errors=error_list(min_size=0, max_size=20))
    def test_systematic_errors_have_required_fields(self, errors):
        """
        Property: For any systematic error, it should have required fields.
        
        **Validates: Requirements 5.3**
        """
        systematic = self.analyzer.identify_systematic_errors(errors)
        
        for sys_error in systematic:
            assert 'parameter' in sys_error
            assert 'frequency' in sys_error
            assert 'errors' in sys_error
            assert 'category_breakdown' in sys_error
            assert 'most_common_category' in sys_error
            assert sys_error['frequency'] >= 3
    
    @given(errors=error_list(min_size=0, max_size=20))
    def test_systematic_errors_sorted_by_frequency(self, errors):
        """
        Property: For any error list, systematic errors should be sorted by frequency.
        
        **Validates: Requirements 5.3**
        """
        systematic = self.analyzer.identify_systematic_errors(errors)
        
        # Check that frequencies are in descending order
        frequencies = [s['frequency'] for s in systematic]
        assert frequencies == sorted(frequencies, reverse=True)
    
    @given(
        value=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False),
        min_val=st.floats(min_value=0.1, max_value=500, allow_nan=False, allow_infinity=False)
    )
    def test_extraction_error_for_different_values(self, value, min_val):
        """
        Property: For any error with significantly different values, it should be extraction_error.
        
        **Validates: Requirements 5.2**
        """
        max_val = min_val + 100
        
        # Make values significantly different (>0.01)
        system_value = value
        ground_truth_value = value + 10  # Significantly different
        
        error = {
            'parameter': 'test',
            'system_value': system_value,
            'ground_truth_value': ground_truth_value,
            'system_classification': 'Normal',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': min_val, 'max': max_val}
        }
        
        category = self.analyzer.categorize_error(error)
        assert category == 'extraction_error'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

