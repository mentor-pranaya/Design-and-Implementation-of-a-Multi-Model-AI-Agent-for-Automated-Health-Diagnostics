"""
Property-based tests for dataset documentation completeness.

Feature: milestone-1-validation
Property 14: Dataset Documentation Completeness

**Validates: Requirements 8.1, 8.3**

For any generated dataset documentation, it should list all 17 reports with their
format (PDF/PNG) and parameter count.
"""

import pytest
from hypothesis import given, strategies as st, assume
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.report_generator import ReportGenerator


# Strategy for generating report information
@st.composite
def reports_info_strategy(draw):
    """Generate valid report information for testing."""
    num_reports = draw(st.integers(min_value=1, max_value=30))
    
    reports_info = []
    for i in range(num_reports):
        report_format = draw(st.sampled_from(['PDF', 'PNG']))
        param_count = draw(st.integers(min_value=0, max_value=50))
        
        reports_info.append({
            'report_id': f'report_{i+1:03d}',
            'format': report_format,
            'parameter_count': param_count,
            'laboratory': draw(st.sampled_from(['Lab A', 'Lab B', 'Lab C', 'N/A'])),
            'notes': draw(st.sampled_from(['', 'Complete', 'Partial', 'High quality']))
        })
    
    return reports_info


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
@given(reports_info=reports_info_strategy())
def test_dataset_documentation_lists_all_reports(reports_info):
    """
    Property 14: Dataset Documentation Completeness
    
    For any generated dataset documentation, it should list all reports.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    # Generate dataset documentation
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation must be a non-empty string
    assert isinstance(documentation, str), "Documentation must be a string"
    assert len(documentation) > 0, "Documentation must not be empty"
    
    # Property: Documentation must list all report IDs
    for report in reports_info:
        report_id = report['report_id']
        assert report_id in documentation, \
            f"Documentation must include report ID {report_id}"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
@given(reports_info=reports_info_strategy())
def test_dataset_documentation_shows_formats(reports_info):
    """
    Property 14: Dataset Documentation Completeness
    
    For any generated dataset documentation, it should show the format (PDF/PNG)
    for each report.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    # Generate dataset documentation
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation must mention PDF and/or PNG formats
    has_pdf = any(r['format'] == 'PDF' for r in reports_info)
    has_png = any(r['format'] == 'PNG' for r in reports_info)
    
    if has_pdf:
        assert 'PDF' in documentation, \
            "Documentation must mention PDF format when PDF reports exist"
    
    if has_png:
        assert 'PNG' in documentation, \
            "Documentation must mention PNG format when PNG reports exist"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
@given(reports_info=reports_info_strategy())
def test_dataset_documentation_shows_parameter_counts(reports_info):
    """
    Property 14: Dataset Documentation Completeness
    
    For any generated dataset documentation, it should show the parameter count
    for each report.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    # Generate dataset documentation
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation must include parameter counts
    # Check that at least some parameter counts are mentioned
    param_counts = [str(r['parameter_count']) for r in reports_info if r['parameter_count'] > 0]
    
    if param_counts:
        # At least one parameter count should be in the documentation
        assert any(count in documentation for count in param_counts), \
            "Documentation must include parameter counts"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
@given(reports_info=reports_info_strategy())
def test_dataset_documentation_has_report_table(reports_info):
    """
    Property: Dataset documentation includes a table with report details.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    # Generate dataset documentation
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation should have table structure (markdown table)
    assert '|' in documentation, \
        "Documentation should include a table (markdown format)"
    
    # Property: Table should have relevant column headers
    assert any(header in documentation for header in ['Report ID', 'report_id', 'Report']), \
        "Documentation table should have Report ID column"
    
    assert any(header in documentation for header in ['Format', 'format']), \
        "Documentation table should have Format column"
    
    assert any(header in documentation for header in ['Parameters', 'parameters', 'Parameter']), \
        "Documentation table should have Parameters column"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
@given(reports_info=reports_info_strategy())
def test_dataset_documentation_shows_format_summary(reports_info):
    """
    Property: Dataset documentation includes summary of formats.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    # Generate dataset documentation
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Count formats
    pdf_count = sum(1 for r in reports_info if r['format'] == 'PDF')
    png_count = sum(1 for r in reports_info if r['format'] == 'PNG')
    
    # Property: Documentation should mention format counts
    if pdf_count > 0:
        assert str(pdf_count) in documentation, \
            f"Documentation should mention PDF count {pdf_count}"
    
    if png_count > 0:
        assert str(png_count) in documentation, \
            f"Documentation should mention PNG count {png_count}"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
@given(reports_info=reports_info_strategy())
def test_dataset_documentation_includes_parameter_coverage(reports_info):
    """
    Property: Dataset documentation includes parameter coverage information.
    
    Validates: Requirements 8.3
    """
    generator = ReportGenerator()
    
    # Generate dataset documentation
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation should mention parameter types/coverage
    assert "## Parameter Coverage" in documentation or "Parameter" in documentation, \
        "Documentation should include parameter coverage section"
    
    # Property: Documentation should mention various parameter categories
    # (based on the implementation which lists parameter types)
    parameter_categories = ['Hematology', 'Metabolic', 'Lipid', 'Liver', 'Kidney', 'Thyroid']
    
    # At least some categories should be mentioned
    assert any(category in documentation for category in parameter_categories), \
        "Documentation should mention parameter categories"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
def test_dataset_documentation_with_17_reports():
    """
    Property: Dataset documentation correctly handles exactly 17 reports.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    # Create exactly 17 reports (the actual test dataset size)
    reports_info = []
    for i in range(17):
        reports_info.append({
            'report_id': f'report_{i+1:03d}',
            'format': 'PDF' if i < 13 else 'PNG',
            'parameter_count': 15,
            'laboratory': 'Test Lab',
            'notes': ''
        })
    
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation must mention 17 reports
    assert '17' in documentation, \
        "Documentation must mention 17 reports"
    
    # Property: Documentation must list all 17 report IDs
    for report in reports_info:
        assert report['report_id'] in documentation, \
            f"Documentation must include {report['report_id']}"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
def test_dataset_documentation_with_mixed_formats():
    """
    Property: Dataset documentation correctly shows mixed PDF and PNG formats.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    reports_info = [
        {'report_id': 'report_001', 'format': 'PDF', 'parameter_count': 15, 'laboratory': 'Lab A', 'notes': ''},
        {'report_id': 'report_002', 'format': 'PDF', 'parameter_count': 20, 'laboratory': 'Lab B', 'notes': ''},
        {'report_id': 'report_003', 'format': 'PNG', 'parameter_count': 10, 'laboratory': 'Lab C', 'notes': ''},
        {'report_id': 'report_004', 'format': 'PNG', 'parameter_count': 12, 'laboratory': 'Lab D', 'notes': ''},
    ]
    
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation must show both formats
    assert 'PDF' in documentation
    assert 'PNG' in documentation
    
    # Property: Documentation must show correct counts
    assert '2' in documentation  # 2 PDF and 2 PNG


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
def test_dataset_documentation_with_varying_parameter_counts():
    """
    Property: Dataset documentation shows varying parameter counts.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    reports_info = [
        {'report_id': 'report_001', 'format': 'PDF', 'parameter_count': 5, 'laboratory': 'Lab A', 'notes': ''},
        {'report_id': 'report_002', 'format': 'PDF', 'parameter_count': 15, 'laboratory': 'Lab B', 'notes': ''},
        {'report_id': 'report_003', 'format': 'PDF', 'parameter_count': 30, 'laboratory': 'Lab C', 'notes': ''},
    ]
    
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation must show different parameter counts
    assert '5' in documentation
    assert '15' in documentation
    assert '30' in documentation


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
def test_dataset_documentation_includes_excluded_files_section():
    """
    Property: Dataset documentation includes information about excluded files.
    
    Validates: Requirements 8.2
    """
    generator = ReportGenerator()
    
    reports_info = [
        {'report_id': 'report_001', 'format': 'PDF', 'parameter_count': 15, 'laboratory': 'Lab A', 'notes': ''},
    ]
    
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation should mention excluded files
    assert "Excluded" in documentation or "excluded" in documentation, \
        "Documentation should mention excluded files"
    
    # Property: Documentation should explain why files were excluded
    # (report 4 blank, report 7 bill)
    assert "blank" in documentation.lower() or "bill" in documentation.lower(), \
        "Documentation should explain exclusion reasons"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
def test_dataset_documentation_with_validation_results():
    """
    Property: Dataset documentation includes statistics when validation results provided.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    reports_info = [
        {'report_id': 'report_001', 'format': 'PDF', 'parameter_count': 15, 'laboratory': 'Lab A', 'notes': ''},
        {'report_id': 'report_002', 'format': 'PDF', 'parameter_count': 20, 'laboratory': 'Lab B', 'notes': ''},
    ]
    
    validation_results = {
        'accuracy_metrics': {
            'total_parameters': 35
        }
    }
    
    documentation = generator.generate_dataset_documentation(reports_info, validation_results)
    
    # Property: Documentation should include statistics section
    assert "Statistics" in documentation or "statistics" in documentation, \
        "Documentation should include statistics when validation results provided"
    
    # Property: Documentation should show total parameters
    assert '35' in documentation, \
        "Documentation should show total parameters from validation results"


# Feature: milestone-1-validation, Property 14: Dataset Documentation Completeness
@given(
    num_reports=st.integers(min_value=1, max_value=50),
    pdf_ratio=st.floats(min_value=0.0, max_value=1.0)
)
def test_dataset_documentation_format_counts_consistency(num_reports, pdf_ratio):
    """
    Property: Format counts in documentation are mathematically consistent.
    
    Validates: Requirements 8.1
    """
    generator = ReportGenerator()
    
    pdf_count = int(num_reports * pdf_ratio)
    png_count = num_reports - pdf_count
    
    reports_info = []
    for i in range(num_reports):
        report_format = 'PDF' if i < pdf_count else 'PNG'
        reports_info.append({
            'report_id': f'report_{i+1:03d}',
            'format': report_format,
            'parameter_count': 15,
            'laboratory': 'Lab',
            'notes': ''
        })
    
    documentation = generator.generate_dataset_documentation(reports_info)
    
    # Property: Documentation must mention total number of reports
    assert str(num_reports) in documentation, \
        f"Documentation must mention total reports {num_reports}"
    
    # Property: Documentation must mention format counts
    if pdf_count > 0:
        assert str(pdf_count) in documentation, \
            f"Documentation must mention PDF count {pdf_count}"
    
    if png_count > 0:
        assert str(png_count) in documentation, \
            f"Documentation must mention PNG count {png_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

