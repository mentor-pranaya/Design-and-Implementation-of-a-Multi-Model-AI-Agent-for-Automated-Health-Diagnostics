"""
Unit Tests for Error Analyzer Module

Tests error categorization, systematic error detection, and report generation.
"""

import pytest
from evaluation.error_analyzer import ErrorAnalyzer


class TestErrorAnalyzer:
    """Unit tests for ErrorAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ErrorAnalyzer()
    
    def test_initialization(self):
        """Test ErrorAnalyzer initializes correctly."""
        assert self.analyzer is not None
        assert len(self.analyzer.error_categories) == 4
        assert 'extraction_error' in self.analyzer.error_categories
        assert 'reference_range_error' in self.analyzer.error_categories
        assert 'classification_logic_error' in self.analyzer.error_categories
        assert 'edge_case' in self.analyzer.error_categories
    
    def test_categorize_extraction_error(self):
        """Test categorization of extraction errors (different values)."""
        error = {
            'parameter': 'glucose',
            'system_value': 110,
            'ground_truth_value': 105,  # Different value
            'system_classification': 'High',
            'ground_truth_classification': 'High',
            'reference_range': {'min': 70, 'max': 100}
        }
        
        category = self.analyzer.categorize_error(error)
        assert category == 'extraction_error'
    
    def test_categorize_edge_case_near_min(self):
        """Test categorization of edge cases near minimum boundary."""
        error = {
            'parameter': 'hemoglobin',
            'system_value': 13.2,
            'ground_truth_value': 13.2,
            'system_classification': 'Low',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 13.0, 'max': 17.5}
        }
        
        category = self.analyzer.categorize_error(error)
        # 13.2 is within 5% of 13.0 (range span = 4.5, 5% = 0.225)
        assert category == 'edge_case'
    
    def test_categorize_edge_case_near_max(self):
        """Test categorization of edge cases near maximum boundary."""
        error = {
            'parameter': 'glucose',
            'system_value': 99,
            'ground_truth_value': 99,
            'system_classification': 'Normal',
            'ground_truth_classification': 'High',
            'reference_range': {'min': 70, 'max': 100}
        }
        
        category = self.analyzer.categorize_error(error)
        # 99 is within 5% of 100 (range span = 30, 5% = 1.5)
        assert category == 'edge_case'
    
    def test_categorize_reference_range_error(self):
        """Test categorization of reference range errors."""
        error = {
            'parameter': 'creatinine',
            'system_value': 0.9,
            'ground_truth_value': 0.9,
            'system_classification': 'Normal',
            'ground_truth_classification': 'High',  # GT says High but value in range
            'reference_range': {'min': 0.6, 'max': 1.2}
        }
        
        category = self.analyzer.categorize_error(error)
        assert category == 'reference_range_error'
    
    def test_categorize_classification_logic_error(self):
        """Test categorization of classification logic errors."""
        error = {
            'parameter': 'glucose',
            'system_value': 120,
            'ground_truth_value': 120,
            'system_classification': 'Normal',
            'ground_truth_classification': 'High',
            'reference_range': {'min': 70, 'max': 100}
        }
        
        category = self.analyzer.categorize_error(error)
        # Value is clearly outside range, not an edge case
        # Same value, so not extraction error
        # Value outside range matches system classification, so not ref range error
        assert category == 'classification_logic_error'
    
    def test_identify_systematic_errors_none(self):
        """Test systematic error detection with no systematic errors."""
        errors = [
            {
                'parameter': 'glucose',
                'system_value': 110,
                'ground_truth_value': 110,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 100}
            },
            {
                'parameter': 'hemoglobin',
                'system_value': 13.0,
                'ground_truth_value': 13.0,
                'system_classification': 'Low',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 13.0, 'max': 17.5}
            }
        ]
        
        systematic = self.analyzer.identify_systematic_errors(errors)
        assert len(systematic) == 0
    
    def test_identify_systematic_errors_found(self):
        """Test systematic error detection with systematic errors (≥3 occurrences)."""
        errors = [
            {
                'parameter': 'glucose',
                'report_id': 'report_001',
                'system_value': 110,
                'ground_truth_value': 110,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 100}
            },
            {
                'parameter': 'glucose',
                'report_id': 'report_002',
                'system_value': 105,
                'ground_truth_value': 105,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 100}
            },
            {
                'parameter': 'glucose',
                'report_id': 'report_003',
                'system_value': 102,
                'ground_truth_value': 102,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 100}
            }
        ]
        
        systematic = self.analyzer.identify_systematic_errors(errors)
        assert len(systematic) == 1
        assert systematic[0]['parameter'] == 'glucose'
        assert systematic[0]['frequency'] == 3
    
    def test_analyze_errors_empty(self):
        """Test error analysis with no errors."""
        analysis = self.analyzer.analyze_errors([])
        
        assert analysis['total_errors'] == 0
        assert len(analysis['by_category']) == 0
        assert len(analysis['systematic_errors']) == 0
        assert len(analysis['edge_cases']) == 0
        assert len(analysis['recommendations']) > 0
    
    def test_analyze_errors_with_errors(self):
        """Test error analysis with multiple errors."""
        errors = [
            {
                'parameter': 'glucose',
                'report_id': 'report_001',
                'system_value': 110,
                'ground_truth_value': 110,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 100}
            },
            {
                'parameter': 'hemoglobin',
                'report_id': 'report_002',
                'system_value': 12.5,
                'ground_truth_value': 13.0,
                'system_classification': 'Low',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 13.0, 'max': 17.5}
            }
        ]
        
        analysis = self.analyzer.analyze_errors(errors)
        
        assert analysis['total_errors'] == 2
        assert len(analysis['by_category']) > 0
        assert 'category_summary' in analysis
        assert 'recommendations' in analysis
        assert len(analysis['recommendations']) > 0
    
    def test_error_logging_completeness(self):
        """Test that all required fields are logged in error analysis."""
        error = {
            'parameter': 'glucose',
            'report_id': 'report_001',
            'system_value': 110,
            'ground_truth_value': 110,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        }
        
        analysis = self.analyzer.analyze_errors([error])
        
        # Get the categorized error
        categorized_errors = []
        for category_errors in analysis['by_category'].values():
            categorized_errors.extend(category_errors)
        
        assert len(categorized_errors) == 1
        logged_error = categorized_errors[0]
        
        # Verify all required fields are present (Requirement 5.1)
        assert 'parameter' in logged_error
        assert 'report_id' in logged_error
        assert 'system_value' in logged_error
        assert 'ground_truth_value' in logged_error
        assert 'system_classification' in logged_error
        assert 'ground_truth_classification' in logged_error
        assert 'reference_range' in logged_error
        assert 'category' in logged_error
    
    def test_generate_error_report_no_errors(self):
        """Test error report generation with no errors."""
        analysis = self.analyzer.analyze_errors([])
        report = self.analyzer.generate_error_report(analysis)
        
        assert "# Error Analysis Report" in report
        assert "Total Errors:** 0" in report
        assert "No errors detected" in report
    
    def test_generate_error_report_with_errors(self):
        """Test error report generation with errors."""
        errors = [
            {
                'parameter': 'glucose',
                'report_id': 'report_001',
                'system_value': 110,
                'ground_truth_value': 110,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 100}
            }
        ]
        
        analysis = self.analyzer.analyze_errors(errors)
        report = self.analyzer.generate_error_report(analysis)
        
        assert "# Error Analysis Report" in report
        assert "Total Errors:** 1" in report
        assert "## Error Categories" in report
        assert "## Recommendations" in report
    
    def test_generate_error_report_with_report_id(self):
        """Test error report generation with specific report ID."""
        analysis = self.analyzer.analyze_errors([])
        report = self.analyzer.generate_error_report(analysis, report_id="report_001")
        
        assert "Report ID:** report_001" in report
    
    def test_recommendations_for_extraction_errors(self):
        """Test that recommendations are generated for extraction errors."""
        errors = [
            {
                'parameter': 'glucose',
                'system_value': 110,
                'ground_truth_value': 105,  # Different value
                'system_classification': 'High',
                'ground_truth_classification': 'High',
                'reference_range': {'min': 70, 'max': 100}
            }
        ]
        
        analysis = self.analyzer.analyze_errors(errors)
        recommendations = analysis['recommendations']
        
        assert any('EXTRACTION ERRORS' in rec for rec in recommendations)
    
    def test_recommendations_for_systematic_errors(self):
        """Test that recommendations are generated for systematic errors."""
        errors = [
            {
                'parameter': 'glucose',
                'report_id': f'report_{i:03d}',
                'system_value': 110,
                'ground_truth_value': 110,
                'system_classification': 'High',
                'ground_truth_classification': 'Normal',
                'reference_range': {'min': 70, 'max': 100}
            }
            for i in range(1, 4)  # 3 errors for same parameter
        ]
        
        analysis = self.analyzer.analyze_errors(errors)
        recommendations = analysis['recommendations']
        
        assert any('SYSTEMATIC ERROR DETECTED' in rec for rec in recommendations)
    
    def test_edge_case_5_percent_threshold(self):
        """Test that edge case detection uses 5% threshold correctly."""
        # For range 70-100 (span=30), 5% = 1.5
        # Value at 98.6 should be edge case (100 - 98.6 = 1.4 < 1.5)
        error = {
            'parameter': 'glucose',
            'system_value': 98.6,
            'ground_truth_value': 98.6,
            'system_classification': 'Normal',
            'ground_truth_classification': 'High',
            'reference_range': {'min': 70, 'max': 100}
        }
        
        category = self.analyzer.categorize_error(error)
        assert category == 'edge_case'
    
    def test_not_edge_case_outside_threshold(self):
        """Test that values outside 5% threshold are not edge cases."""
        # For range 70-100 (span=30), 5% = 1.5
        # Value at 95 should NOT be edge case (100 - 95 = 5 > 1.5)
        error = {
            'parameter': 'glucose',
            'system_value': 95,
            'ground_truth_value': 95,
            'system_classification': 'Normal',
            'ground_truth_classification': 'High',
            'reference_range': {'min': 70, 'max': 100}
        }
        
        category = self.analyzer.categorize_error(error)
        assert category != 'edge_case'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

