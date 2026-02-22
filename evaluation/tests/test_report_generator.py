"""
Unit tests for ReportGenerator module.

Tests markdown formatting, report structure, and file saving operations.
Validates Requirements 6.1, 6.5 from milestone-1-validation spec.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.report_generator import ReportGenerator


class TestReportGenerator:
    """Test suite for ReportGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create a ReportGenerator instance for testing."""
        return ReportGenerator()
    
    @pytest.fixture
    def sample_validation_results(self):
        """Sample validation results for testing."""
        return {
            'timestamp': '2026-01-20T10:30:00',
            'reports_processed': 17,
            'reports_with_errors': 0,
            'accuracy_metrics': {
                'total_parameters': 255,
                'correct_classifications': 251,
                'incorrect_classifications': 4,
                'accuracy_percentage': 98.43
            },
            'per_report_results': [
                {
                    'report_id': 'report_001',
                    'total_parameters': 15,
                    'correct': 15,
                    'incorrect': 0,
                    'accuracy': 100.0
                },
                {
                    'report_id': 'report_002',
                    'total_parameters': 12,
                    'correct': 11,
                    'incorrect': 1,
                    'accuracy': 91.67
                }
            ],
            'errors': [],
            'target_met': True
        }
    
    @pytest.fixture
    def sample_error_analysis(self):
        """Sample error analysis for testing."""
        return {
            'total_errors': 4,
            'category_summary': {
                'edge_case': 3,
                'classification_logic_error': 1
            },
            'systematic_errors': [
                {
                    'parameter': 'glucose',
                    'frequency': 2
                }
            ],
            'recommendations': [
                'Review glucose classification thresholds',
                'Investigate edge case handling'
            ]
        }
    
    def test_generate_validation_report_structure(self, generator, sample_validation_results):
        """Test that validation report has correct structure."""
        report = generator.generate_validation_report(sample_validation_results)
        
        # Check for required sections
        assert "# Milestone 1 Validation Report" in report
        assert "## Executive Summary" in report
        assert "## Extraction Accuracy" in report
        assert "## Classification Accuracy" in report
        assert "## Per-Report Results" in report
        assert "## Report Metadata" in report
        
        # Check for key metrics
        assert "100%" in report  # Extraction accuracy
        assert "98.43%" in report  # Classification accuracy
        assert "✓ PASSED" in report  # Target met
    
    def test_generate_validation_report_with_errors(self, generator, sample_validation_results, sample_error_analysis):
        """Test validation report includes error analysis when provided."""
        report = generator.generate_validation_report(sample_validation_results, sample_error_analysis)
        
        # Check error analysis section is included
        assert "## Error Analysis Summary" in report
        assert "**Total Errors:** 4" in report
        assert "Edge Case" in report
        assert "**Systematic Errors Detected:**" in report
        assert "**Recommendations:**" in report
    
    def test_generate_validation_report_markdown_formatting(self, generator, sample_validation_results):
        """Test that report uses proper markdown formatting."""
        report = generator.generate_validation_report(sample_validation_results)
        
        # Check markdown elements
        assert report.startswith("# ")  # H1 header
        assert "## " in report  # H2 headers
        assert "**" in report  # Bold text
        assert "|" in report  # Tables
        assert "---" in report  # Horizontal rules
    
    def test_generate_validation_report_per_report_table(self, generator, sample_validation_results):
        """Test that per-report results are formatted as a table."""
        report = generator.generate_validation_report(sample_validation_results)
        
        # Check table structure
        assert "| Report ID | Parameters | Correct | Incorrect | Accuracy |" in report
        assert "|-----------|------------|---------|-----------|----------|" in report
        assert "| report_001 | 15 | 15 | 0 | 100.0% |" in report
        assert "| report_002 | 12 | 11 | 1 | 91.67% |" in report
    
    def test_generate_validation_report_target_not_met(self, generator, sample_validation_results):
        """Test report when classification target is not met."""
        # Modify results to not meet target
        sample_validation_results['target_met'] = False
        sample_validation_results['accuracy_metrics']['accuracy_percentage'] = 95.5
        
        report = generator.generate_validation_report(sample_validation_results)
        
        # Check for failure indication
        assert "✗ NOT MET" in report
        assert "does not meet the target" in report
    
    def test_generate_certification_when_target_met(self, generator, sample_validation_results):
        """Test certification document generation when targets are met."""
        cert = generator.generate_certification(sample_validation_results)
        
        # Check for required sections
        assert "# Milestone 1 Completion Certification" in cert
        assert "## Certification Statement" in cert
        assert "## Final Metrics" in cert
        assert "## Evidence" in cert
        assert "## Technical Achievements" in cert
        assert "## Sign-Off" in cert
        assert "**MILESTONE 1: COMPLETE** ✓" in cert
        
        # Check metrics
        assert "100%" in cert  # Extraction
        assert "98.43%" in cert  # Classification
        assert "✓ **EXCEEDED TARGET**" in cert
        assert "✓ **MET TARGET**" in cert
    
    def test_generate_certification_when_target_not_met(self, generator, sample_validation_results):
        """Test that certification is not generated when targets not met."""
        # Modify results to not meet target
        sample_validation_results['target_met'] = False
        
        cert = generator.generate_certification(sample_validation_results)
        
        # Should return message that certification cannot be issued
        assert "Certification Not Generated" in cert
        assert "targets have not been met" in cert
    
    def test_generate_certification_includes_technical_achievements(self, generator, sample_validation_results):
        """Test that certification includes technical achievements."""
        cert = generator.generate_certification(sample_validation_results)
        
        # Check for key technical achievements
        assert "Comprehensive Extraction System" in cert
        assert "Unified Reference Manager" in cert
        assert "Indian Population Calibration" in cert
        assert "Validation Infrastructure" in cert
        assert "Zero hardcoding" in cert
    
    def test_generate_dataset_documentation_structure(self, generator):
        """Test dataset documentation structure."""
        reports_info = [
            {
                'report_id': 'report_001',
                'format': 'PDF',
                'parameter_count': 15,
                'laboratory': 'Lab A',
                'notes': 'Complete report'
            },
            {
                'report_id': 'report_015_png',
                'format': 'PNG',
                'parameter_count': 12,
                'laboratory': 'Lab B',
                'notes': 'Scanned image'
            }
        ]
        
        doc = generator.generate_dataset_documentation(reports_info)
        
        # Check for required sections
        assert "# Test Dataset Documentation" in doc
        assert "## Overview" in doc
        assert "## Valid Test Reports" in doc
        assert "## Excluded Files" in doc
        assert "## Parameter Coverage" in doc
        assert "## Dataset Diversity" in doc
        
        # Check report counts
        assert "**Total Valid Reports:** 2" in doc
        assert "**PDF Reports:** 1" in doc
        assert "**PNG Reports:** 1" in doc
    
    def test_generate_dataset_documentation_report_table(self, generator):
        """Test that dataset documentation includes report details table."""
        reports_info = [
            {
                'report_id': 'report_001',
                'format': 'PDF',
                'parameter_count': 15,
                'laboratory': 'Lab A',
                'notes': 'Complete'
            }
        ]
        
        doc = generator.generate_dataset_documentation(reports_info)
        
        # Check table structure
        assert "| Report ID | Format | Parameters | Laboratory | Notes |" in doc
        assert "| report_001 | PDF | 15 | Lab A | Complete |" in doc
    
    def test_generate_dataset_documentation_excluded_files(self, generator):
        """Test that excluded files are documented."""
        reports_info = []
        
        doc = generator.generate_dataset_documentation(reports_info)
        
        # Check excluded files section
        assert "## Excluded Files" in doc
        assert "Report 4 (Blank)" in doc
        assert "Report 7 (Bill/Receipt)" in doc
    
    def test_generate_comparison_report_structure(self, generator):
        """Test comparison report structure."""
        original_metrics = {
            'successful_reports': 10,
            'total_reports': 19,
            'failed_reports': ['report_004', 'report_007'],
            'classification_accuracy': 95.5
        }
        
        improved_metrics = {
            'successful_reports': 17,
            'total_reports': 17,
            'classification_accuracy': 98.43
        }
        
        report = generator.generate_comparison_report(original_metrics, improved_metrics)
        
        # Check for required sections
        assert "# System Comparison Report" in report
        assert "## Extraction Accuracy Comparison" in report
        assert "## Previously Failing Reports" in report
        assert "## Key Improvements" in report
        assert "## Classification Accuracy Comparison" in report
        
        # Check metrics
        assert "52.6%" in report  # Original rate
        assert "100.0%" in report  # Improved rate
    
    def test_save_report_creates_file(self, generator):
        """Test that save_report creates a file with content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_report.md"
            content = "# Test Report\n\nThis is a test."
            
            generator.save_report(content, str(output_path))
            
            # Verify file was created
            assert output_path.exists()
            
            # Verify content
            with open(output_path, 'r') as f:
                saved_content = f.read()
            
            assert saved_content == content
    
    def test_save_report_creates_directory(self, generator):
        """Test that save_report creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "nested" / "test_report.md"
            content = "# Test Report"
            
            generator.save_report(content, str(output_path))
            
            # Verify file and directories were created
            assert output_path.exists()
            assert output_path.parent.exists()
    
    def test_validation_report_includes_timestamp(self, generator, sample_validation_results):
        """Test that validation report includes timestamp."""
        report = generator.generate_validation_report(sample_validation_results)
        
        # Check for timestamp
        assert "**Generated:**" in report
        assert "**Validation Timestamp:**" in report
    
    def test_certification_includes_achievement_date(self, generator, sample_validation_results):
        """Test that certification includes achievement date."""
        cert = generator.generate_certification(sample_validation_results)
        
        # Check for date
        assert "**Achievement Date:**" in cert
        assert "**Date:**" in cert
    
    def test_dataset_documentation_includes_parameter_types(self, generator):
        """Test that dataset documentation lists parameter types."""
        reports_info = []
        
        doc = generator.generate_dataset_documentation(reports_info)
        
        # Check for parameter categories
        assert "Hematology" in doc
        assert "Metabolic" in doc
        assert "Lipid Profile" in doc
        assert "Liver Function" in doc
        assert "Kidney Function" in doc
        assert "Thyroid" in doc


class TestCertificationGenerator:
    """
    Unit tests for certification generator functionality.
    
    Tests certification generation with passing metrics, failure when targets not met,
    and markdown formatting/structure.
    Validates Requirements 10.1, 10.2 from milestone-1-validation spec.
    """
    
    @pytest.fixture
    def generator(self):
        """Create a ReportGenerator instance for testing."""
        return ReportGenerator()
    
    @pytest.fixture
    def passing_validation_results(self):
        """Validation results that meet all targets."""
        return {
            'timestamp': '2026-01-20T10:30:00',
            'reports_processed': 17,
            'accuracy_metrics': {
                'total_parameters': 255,
                'correct_classifications': 251,
                'incorrect_classifications': 4,
                'accuracy_percentage': 98.43
            },
            'target_met': True
        }
    
    @pytest.fixture
    def failing_validation_results(self):
        """Validation results that do not meet targets."""
        return {
            'timestamp': '2026-01-20T10:30:00',
            'reports_processed': 17,
            'accuracy_metrics': {
                'total_parameters': 255,
                'correct_classifications': 240,
                'incorrect_classifications': 15,
                'accuracy_percentage': 94.12
            },
            'target_met': False
        }
    
    def test_certification_generated_when_targets_met(self, generator, passing_validation_results):
        """Test that certification is generated when both targets are met."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Should generate full certification document
        assert "# Milestone 1 Completion Certification" in cert
        assert "Certification Not Generated" not in cert
        assert "**MILESTONE 1: COMPLETE** ✓" in cert
    
    def test_certification_not_generated_when_targets_not_met(self, generator, failing_validation_results):
        """Test that certification is not generated when targets are not met."""
        cert = generator.generate_certification(failing_validation_results)
        
        # Should return message that certification cannot be issued
        assert "# Certification Not Generated" in cert
        assert "targets have not been met" in cert
        assert "cannot be issued" in cert
        
        # Should not include full certification content
        assert "## Certification Statement" not in cert
        assert "## Final Metrics" not in cert
        assert "**MILESTONE 1: COMPLETE**" not in cert
    
    def test_certification_includes_all_required_sections(self, generator, passing_validation_results):
        """Test that certification includes all required sections per Requirement 10.2."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check all required sections
        required_sections = [
            "# Milestone 1 Completion Certification",
            "## Certification Statement",
            "## Final Metrics",
            "## Evidence",
            "## Technical Achievements",
            "## Test Dataset",
            "## Sign-Off",
            "## Status"
        ]
        
        for section in required_sections:
            assert section in cert, f"Missing required section: {section}"
    
    def test_certification_includes_achievement_date(self, generator, passing_validation_results):
        """Test that certification includes achievement date."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for achievement date
        assert "**Achievement Date:**" in cert
        
        # Verify date format (YYYY-MM-DD)
        import re
        date_pattern = r'\*\*Achievement Date:\*\* \d{4}-\d{2}-\d{2}'
        assert re.search(date_pattern, cert), "Achievement date not in correct format"
    
    def test_certification_includes_final_metrics(self, generator, passing_validation_results):
        """Test that certification includes final metrics with correct values."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check extraction metrics
        assert "### Extraction Accuracy" in cert
        assert "**Target:** ≥95%" in cert
        assert "**Achieved:** 100.0%" in cert
        assert "✓ **EXCEEDED TARGET**" in cert
        
        # Check classification metrics
        assert "### Classification Accuracy" in cert
        assert "**Target:** ≥98%" in cert
        assert "**Achieved:** 98.43%" in cert
        assert "✓ **MET TARGET**" in cert
    
    def test_certification_highlights_extraction_exceeded_target(self, generator, passing_validation_results):
        """Test that certification highlights extraction accuracy exceeded target (Requirement 10.3)."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for explicit mention that extraction exceeded target
        assert "100%" in cert
        assert "EXCEEDED" in cert or "exceeds" in cert
        assert "significantly exceeds the target" in cert or "EXCEEDED TARGET" in cert
    
    def test_certification_includes_evidence_references(self, generator, passing_validation_results):
        """Test that certification includes evidence references."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for evidence section
        assert "## Evidence" in cert
        
        # Check for specific evidence files
        assert "MILESTONE_1_VALIDATION_REPORT.md" in cert
        assert "evaluation/test_dataset/ground_truth/" in cert
        assert "evaluation/validation_results.json" in cert
        assert "data/test_reports/" in cert
    
    def test_certification_includes_technical_achievements(self, generator, passing_validation_results):
        """Test that certification summarizes key technical achievements (Requirement 10.4)."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for technical achievements section
        assert "## Technical Achievements" in cert
        
        # Check for key achievements
        key_achievements = [
            "Comprehensive Extraction System",
            "Unified Reference Manager",
            "Indian Population Calibration",
            "Validation Infrastructure"
        ]
        
        for achievement in key_achievements:
            assert achievement in cert, f"Missing technical achievement: {achievement}"
        
        # Check for specific technical details
        assert "Zero hardcoding" in cert
        assert "Multi-strategy extraction" in cert
        assert "Age and sex-specific" in cert
        assert "Property-based testing" in cert
    
    def test_certification_includes_sign_off_section(self, generator, passing_validation_results):
        """Test that certification includes sign-off section."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for sign-off section
        assert "## Sign-Off" in cert
        
        # Check for signature lines
        assert "Development Team:" in cert
        assert "Quality Assurance:" in cert
        assert "Project Manager:" in cert
        assert "_____________________" in cert
    
    def test_certification_markdown_formatting(self, generator, passing_validation_results):
        """Test that certification uses proper markdown formatting."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check markdown elements
        assert cert.startswith("# ")  # H1 header
        assert "## " in cert  # H2 headers
        assert "### " in cert  # H3 headers
        assert "**" in cert  # Bold text
        assert "---" in cert  # Horizontal rules
        assert "- " in cert  # Bullet lists
        
        # Check for proper structure
        lines = cert.split('\n')
        assert lines[0].startswith("# ")  # First line is H1
    
    def test_certification_includes_test_dataset_summary(self, generator, passing_validation_results):
        """Test that certification includes test dataset summary."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for dataset section
        assert "## Test Dataset" in cert
        
        # Check for dataset details
        assert "17 valid reports" in cert
        assert "13 PDF + 4 PNG" in cert
        assert "Hematology, Metabolic, Lipid, Liver, Kidney, Thyroid" in cert
    
    def test_certification_marks_milestone_complete(self, generator, passing_validation_results):
        """Test that certification marks Milestone 1 as COMPLETE (Requirement 10.5)."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for completion status
        assert "## Status" in cert
        assert "**MILESTONE 1: COMPLETE** ✓" in cert
    
    def test_certification_with_exact_target_accuracy(self, generator):
        """Test certification when classification accuracy exactly meets target (98.0%)."""
        results = {
            'timestamp': '2026-01-20T10:30:00',
            'reports_processed': 17,
            'accuracy_metrics': {
                'total_parameters': 250,
                'correct_classifications': 245,
                'incorrect_classifications': 5,
                'accuracy_percentage': 98.0
            },
            'target_met': True
        }
        
        cert = generator.generate_certification(results)
        
        # Should generate certification
        assert "# Milestone 1 Completion Certification" in cert
        assert "**Achieved:** 98.0%" in cert
        assert "✓ **MET TARGET**" in cert
    
    def test_certification_with_high_accuracy(self, generator):
        """Test certification with very high classification accuracy (>99%)."""
        results = {
            'timestamp': '2026-01-20T10:30:00',
            'reports_processed': 17,
            'accuracy_metrics': {
                'total_parameters': 300,
                'correct_classifications': 298,
                'incorrect_classifications': 2,
                'accuracy_percentage': 99.33
            },
            'target_met': True
        }
        
        cert = generator.generate_certification(results)
        
        # Should generate certification with high accuracy
        assert "# Milestone 1 Completion Certification" in cert
        assert "99.33%" in cert
        assert "✓ **MET TARGET**" in cert
    
    def test_certification_structure_consistency(self, generator, passing_validation_results):
        """Test that certification has consistent structure and formatting."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check that sections appear in correct order
        sections = [
            "# Milestone 1 Completion Certification",
            "## Certification Statement",
            "## Final Metrics",
            "## Evidence",
            "## Technical Achievements",
            "## Test Dataset",
            "## Sign-Off",
            "## Status"
        ]
        
        last_pos = -1
        for section in sections:
            pos = cert.find(section)
            assert pos > last_pos, f"Section '{section}' is out of order or missing"
            last_pos = pos
    
    def test_certification_includes_parameter_counts(self, generator, passing_validation_results):
        """Test that certification includes total parameter counts."""
        cert = generator.generate_certification(passing_validation_results)
        
        # Check for parameter counts
        assert "255 parameters" in cert
        assert "251 correct classifications" in cert
    
    def test_certification_not_generated_message_is_clear(self, generator, failing_validation_results):
        """Test that the message when certification cannot be generated is clear."""
        cert = generator.generate_certification(failing_validation_results)
        
        # Check for clear messaging
        assert "Certification Not Generated" in cert
        assert "targets have not been met" in cert
        assert "cannot be issued at this time" in cert
        
        # Should be brief and to the point
        lines = cert.split('\n')
        assert len(lines) < 10, "Non-certification message should be brief"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

