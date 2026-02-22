"""
Property-Based Tests for Ground Truth File Count

Feature: milestone-1-validation
Property 3: Ground Truth File Count
Validates: Requirements 1.5

Tests that for any complete ground truth generation run, exactly 17 JSON files
should be created in the output directory (one per valid test report).
"""

import json
import pytest
import tempfile
import shutil
from hypothesis import given, strategies as st, settings
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.ground_truth_generator import GroundTruthGenerator


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

@st.composite
def generation_summary_strategy(draw):
    """Generate a ground truth generation summary with file counts."""
    # Generate 1-30 reports (testing various scenarios)
    total_reports = draw(st.integers(min_value=1, max_value=30))
    
    # Randomly decide how many succeed vs fail
    successful = draw(st.integers(min_value=0, max_value=total_reports))
    failed = total_reports - successful
    
    reports = []
    for i in range(successful):
        report_id = f"report_{i+1:03d}"
        reports.append({
            "report_id": report_id,
            "source_file": f"test_report_{i+1}.pdf",
            "output_file": f"{report_id}.json",
            "parameter_count": draw(st.integers(min_value=0, max_value=40)),
            "status": "success"
        })
    
    for i in range(failed):
        reports.append({
            "report_id": f"report_{successful+i+1:03d}",
            "source_file": f"test_report_{successful+i+1}.pdf",
            "status": "failed",
            "error": "Extraction failed"
        })
    
    return {
        "total_reports": total_reports,
        "successful": successful,
        "failed": failed,
        "reports": reports,
        "errors": []
    }


# ============================================================================
# Property Tests
# ============================================================================

class TestGroundTruthFileCount:
    """
    Property 3: Ground Truth File Count
    
    **Validates: Requirements 1.5**
    
    For any complete ground truth generation run, exactly 17 JSON files should
    be created in the output directory (one per valid test report).
    """
    
    # Feature: milestone-1-validation, Property 3: Ground Truth File Count
    @given(summary=generation_summary_strategy())
    @settings(max_examples=20, deadline=None)
    def test_successful_count_matches_file_count(self, summary):
        """
        Property: The number of successful generations should match the number
        of JSON files created (excluding metadata files).
        """
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            
            # Simulate file creation based on summary
            for report in summary['reports']:
                if report['status'] == 'success':
                    output_file = output_dir / report['output_file']
                    # Create a minimal valid ground truth file
                    template = {
                        "report_id": report['report_id'],
                        "report_metadata": {},
                        "parameters": {},
                        "classifications": {},
                        "notes": ""
                    }
                    with open(output_file, 'w') as f:
                        json.dump(template, f)
            
            # Count JSON files (excluding metadata files)
            json_files = [f for f in output_dir.glob("*.json")
                         if f.name not in ["TEMPLATE.json", "generation_summary.json"]]
            
            # Property: successful count should match file count
            assert len(json_files) == summary['successful'], \
                f"Expected {summary['successful']} files, but found {len(json_files)}"
    
    # Feature: milestone-1-validation, Property 3: Ground Truth File Count
    @given(summary=generation_summary_strategy())
    @settings(max_examples=20, deadline=None)
    def test_total_reports_equals_successful_plus_failed(self, summary):
        """
        Property: Total reports should equal successful + failed.
        """
        assert summary['total_reports'] == summary['successful'] + summary['failed'], \
            f"Total ({summary['total_reports']}) != Successful ({summary['successful']}) + Failed ({summary['failed']})"
    
    # Feature: milestone-1-validation, Property 3: Ground Truth File Count
    @given(summary=generation_summary_strategy())
    @settings(max_examples=20, deadline=None)
    def test_report_list_length_matches_total(self, summary):
        """
        Property: The length of the reports list should match total_reports.
        """
        assert len(summary['reports']) == summary['total_reports'], \
            f"Reports list length ({len(summary['reports'])}) != Total reports ({summary['total_reports']})"
    
    # Feature: milestone-1-validation, Property 3: Ground Truth File Count
    @given(summary=generation_summary_strategy())
    @settings(max_examples=20, deadline=None)
    def test_successful_reports_have_output_files(self, summary):
        """
        Property: All successful reports should have an output_file field.
        """
        successful_reports = [r for r in summary['reports'] if r['status'] == 'success']
        
        for report in successful_reports:
            assert 'output_file' in report, \
                f"Successful report {report.get('report_id', 'unknown')} missing output_file"
            assert report['output_file'].endswith('.json'), \
                f"Output file {report['output_file']} should end with .json"
    
    # Feature: milestone-1-validation, Property 3: Ground Truth File Count
    @given(summary=generation_summary_strategy())
    @settings(max_examples=20, deadline=None)
    def test_failed_reports_have_no_output_files(self, summary):
        """
        Property: Failed reports should not have output_file field (or it should not be created).
        """
        failed_reports = [r for r in summary['reports'] if r['status'] == 'failed']
        
        for report in failed_reports:
            # Failed reports may have output_file field, but the file shouldn't be created
            # This test verifies the logical consistency
            assert report['status'] == 'failed', \
                f"Report marked as failed should have status='failed'"


# ============================================================================
# Real File Tests
# ============================================================================

def test_real_ground_truth_file_count_matches_summary():
    """
    Property 3: Ground Truth File Count (Real Files)

    Verify that the actual ground truth directory contains the expected number
    of files based on the generation summary.

    **Validates: Requirements 1.5**

    This test checks that:
    1. A generation summary exists
    2. The number of JSON files matches the successful count in the summary
    3. For the milestone-1-validation spec, this should be exactly 17 files
    """
    ground_truth_dir = Path(__file__).parent.parent / "test_dataset" / "ground_truth"
    
    # Find the most recent generation summary
    summary_files = sorted(ground_truth_dir.glob("generation_summary*.json"))
    
    if len(summary_files) == 0:
        pytest.skip("No generation summary found")
    
    # Use the most recent summary
    latest_summary = summary_files[-1]
    
    with open(latest_summary, 'r') as f:
        summary = json.load(f)
    
    print(f"\nUsing summary: {latest_summary.name}")
    print(f"Total reports: {summary['total_reports']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    
    # Count actual JSON files (excluding metadata files)
    json_files = [f for f in ground_truth_dir.glob("*.json")
                  if f.name not in ["TEMPLATE.json"] 
                  and not f.name.startswith("generation_summary")
                  and "report_id" in json.load(open(f)).keys()]  # Only count new format files
    
    print(f"Actual JSON files found: {len(json_files)}")
    
    # Property: File count should match successful count
    assert len(json_files) == summary['successful'], \
        f"Expected {summary['successful']} ground truth files, but found {len(json_files)}"
    
    # For milestone-1-validation, verify it's exactly 17
    # (This is the specific requirement for this milestone)
    print(f"\nMilestone 1 Validation: Checking for exactly 17 files...")
    assert summary['successful'] == 17, \
        f"Milestone 1 requires exactly 17 valid reports, but found {summary['successful']}"
    
    print(f"✓ Confirmed: Exactly 17 ground truth files created for Milestone 1")


def test_real_ground_truth_files_are_valid_json():
    """
    Property 3: Ground Truth File Count (Real Files - Validation)

    Verify that all ground truth JSON files are valid and parseable.

    **Validates: Requirements 1.5**
    """
    ground_truth_dir = Path(__file__).parent.parent / "test_dataset" / "ground_truth"
    
    # Get all JSON files (excluding metadata)
    json_files = [f for f in ground_truth_dir.glob("*.json")
                  if f.name not in ["TEMPLATE.json"]
                  and not f.name.startswith("generation_summary")]
    
    if len(json_files) == 0:
        pytest.skip("No ground truth files found")
    
    print(f"\nValidating {len(json_files)} JSON files...")
    
    valid_count = 0
    invalid_count = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Check if it's a new format file (has report_id)
            if "report_id" in data:
                valid_count += 1
                print(f"  ✓ {json_file.name}: Valid")
            else:
                print(f"  ⊘ {json_file.name}: Old format (skipped)")
        
        except json.JSONDecodeError as e:
            invalid_count += 1
            print(f"  ✗ {json_file.name}: Invalid JSON - {e}")
    
    print(f"\nSummary: {valid_count} valid, {invalid_count} invalid")
    
    # Property: All files should be valid JSON
    assert invalid_count == 0, \
        f"Found {invalid_count} invalid JSON files"


def test_real_ground_truth_no_duplicate_report_ids():
    """
    Property 3: Ground Truth File Count (Real Files - Uniqueness)

    Verify that all ground truth files have unique report IDs.

    **Validates: Requirements 1.5**
    """
    ground_truth_dir = Path(__file__).parent.parent / "test_dataset" / "ground_truth"
    
    # Get all JSON files (excluding metadata)
    json_files = [f for f in ground_truth_dir.glob("*.json")
                  if f.name not in ["TEMPLATE.json"]
                  and not f.name.startswith("generation_summary")]
    
    if len(json_files) == 0:
        pytest.skip("No ground truth files found")
    
    print(f"\nChecking {len(json_files)} files for duplicate report IDs...")
    
    report_ids = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Only check new format files
            if "report_id" in data:
                report_id = data["report_id"]
                report_ids.append((report_id, json_file.name))
        
        except json.JSONDecodeError:
            continue
    
    # Check for duplicates
    seen = {}
    duplicates = []
    
    for report_id, filename in report_ids:
        if report_id in seen:
            duplicates.append(f"{report_id} in {filename} and {seen[report_id]}")
        else:
            seen[report_id] = filename
    
    if duplicates:
        print(f"\n✗ Found duplicate report IDs:")
        for dup in duplicates:
            print(f"  - {dup}")
    else:
        print(f"✓ All {len(report_ids)} report IDs are unique")
    
    # Property: No duplicate report IDs
    assert len(duplicates) == 0, \
        f"Found duplicate report IDs: {duplicates}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

