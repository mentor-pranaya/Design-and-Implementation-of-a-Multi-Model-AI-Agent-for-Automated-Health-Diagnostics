#!/usr/bin/env python3
"""
Quick test script for run_validation.py

Tests the validation pipeline with a small subset of reports.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.run_validation import ValidationRunner


def test_validation_runner():
    """Test the validation runner with default settings."""
    print("Testing ValidationRunner...")
    print()
    
    # Create runner
    runner = ValidationRunner(
        reports_dir='data/test_reports',
        ground_truth_dir='evaluation/test_dataset/ground_truth',
        output_dir='evaluation/test_results',
        verbose=True
    )
    
    # Test ground truth change detection
    print("Testing ground truth change detection...")
    changes = runner._check_ground_truth_changes()
    print(f"Changes detected: {changes}")
    print()
    
    # Test validation pipeline (this will run the full validation)
    print("Running validation pipeline...")
    try:
        results = runner.run_validation()
        
        if results.get('success'):
            print("\n✓ Validation runner test PASSED")
            print(f"  Target met: {results.get('target_met')}")
            print(f"  Elapsed time: {results.get('elapsed_time', 0):.1f}s")
            return True
        else:
            print("\n✗ Validation runner test FAILED")
            print(f"  Error: {results.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ Validation runner test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_validation_runner()
    sys.exit(0 if success else 1)
