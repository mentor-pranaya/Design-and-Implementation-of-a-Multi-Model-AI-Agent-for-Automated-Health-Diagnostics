#!/usr/bin/env python3
"""
Main Validation Pipeline Script

Orchestrates the complete validation workflow for Milestone 1.
Validates Requirements 9.1, 9.2, 9.3, 9.4, 9.5 from milestone-1-validation spec.

Usage:
    python evaluation/run_validation.py [options]

Options:
    --reports-dir PATH       Directory containing test reports (default: data/test_reports)
    --ground-truth-dir PATH  Directory containing ground truth files (default: evaluation/test_dataset/ground_truth)
    --output-dir PATH        Directory to save results (default: evaluation/results)
    --skip-certification     Skip certification generation even if targets are met
    --verbose                Enable verbose output
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.validation_pipeline import ValidationPipeline
from evaluation.error_analyzer import ErrorAnalyzer
from evaluation.report_generator import ReportGenerator


class ValidationRunner:
    """Main validation pipeline orchestrator."""
    
    def __init__(
        self,
        reports_dir: str,
        ground_truth_dir: str,
        output_dir: str,
        verbose: bool = False
    ):
        """
        Initialize validation runner.
        
        Args:
            reports_dir: Directory containing test reports
            ground_truth_dir: Directory containing ground truth files
            output_dir: Directory to save results
            verbose: Enable verbose output
        """
        self.reports_dir = Path(reports_dir)
        self.ground_truth_dir = Path(ground_truth_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.pipeline = ValidationPipeline()
        self.error_analyzer = ErrorAnalyzer()
        self.report_generator = ReportGenerator()
        
        # Track validation state
        self.last_validation_time = None
        self.ground_truth_timestamps = {}
    
    def _print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*70}")
        print(f"{title:^70}")
        print(f"{'='*70}\n")
    
    def _print_progress(self, message: str):
        """Print a progress message."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def _check_ground_truth_changes(self) -> bool:
        """
        Check if ground truth files have changed since last validation.
        
        Validates Requirement 9.5: Detect ground truth changes
        
        Returns:
            True if changes detected, False otherwise
        """
        if not self.ground_truth_dir.exists():
            return False
        
        # Load last validation timestamp if available
        timestamp_file = self.output_dir / 'last_validation_timestamp.json'
        if timestamp_file.exists():
            try:
                with open(timestamp_file, 'r') as f:
                    data = json.load(f)
                    self.last_validation_time = datetime.fromisoformat(data['timestamp'])
                    self.ground_truth_timestamps = data.get('ground_truth_files', {})
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not load last validation timestamp: {e}")
                return False
        else:
            # First run, no previous validation
            return False
        
        # Check each ground truth file
        changes_detected = False
        changed_files = []
        
        for json_file in self.ground_truth_dir.glob("*.json"):
            # Skip template and summary files
            if json_file.stem in ['TEMPLATE', 'generation_summary']:
                continue
            
            # Get current modification time
            current_mtime = json_file.stat().st_mtime
            
            # Compare with stored timestamp
            stored_mtime = self.ground_truth_timestamps.get(str(json_file.name))
            
            if stored_mtime is None or current_mtime > stored_mtime:
                changes_detected = True
                changed_files.append(json_file.name)
        
        if changes_detected:
            print(f"\n⚠️  WARNING: Ground truth files have changed since last validation!")
            print(f"   Changed files: {len(changed_files)}")
            if self.verbose:
                for filename in changed_files[:5]:
                    print(f"   - {filename}")
                if len(changed_files) > 5:
                    print(f"   ... and {len(changed_files) - 5} more")
            print()
        
        return changes_detected
    
    def _save_validation_timestamp(self):
        """Save current validation timestamp and ground truth file states."""
        timestamp_file = self.output_dir / 'last_validation_timestamp.json'
        
        # Collect current ground truth file timestamps
        gt_timestamps = {}
        for json_file in self.ground_truth_dir.glob("*.json"):
            if json_file.stem not in ['TEMPLATE', 'generation_summary']:
                gt_timestamps[str(json_file.name)] = json_file.stat().st_mtime
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'ground_truth_files': gt_timestamps
        }
        
        with open(timestamp_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run_validation(self) -> Dict:
        """
        Run complete validation pipeline.
        
        Validates Requirement 9.1: Load ground truth, process reports, compare,
        calculate accuracy, and generate reports
        
        Returns:
            Complete validation results
        """
        start_time = time.time()
        
        self._print_header("MILESTONE 1 VALIDATION PIPELINE")
        
        # Configuration
        print("Configuration:")
        print(f"  Reports directory: {self.reports_dir}")
        print(f"  Ground truth directory: {self.ground_truth_dir}")
        print(f"  Output directory: {self.output_dir}")
        print(f"  Verbose mode: {self.verbose}")
        print()
        
        # Requirement 9.5: Check for ground truth changes
        self._check_ground_truth_changes()
        
        # Step 1: Run validation pipeline
        self._print_progress("Starting validation pipeline...")
        
        try:
            # Requirement 9.3: Continue on individual report failures
            validation_results = self.pipeline.run_validation(
                reports_dir=str(self.reports_dir),
                ground_truth_dir=str(self.ground_truth_dir)
            )
        except Exception as e:
            print(f"\n❌ ERROR: Validation pipeline failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
        
        # Step 2: Analyze errors
        self._print_progress("Analyzing classification errors...")
        
        error_analysis = None
        accuracy_metrics = validation_results.get('accuracy_metrics', {})
        all_mismatches = accuracy_metrics.get('all_mismatches', [])
        
        if all_mismatches:
            # Add report_id to each mismatch for error analysis
            errors_with_report_id = []
            per_report = validation_results.get('per_report_results', [])
            
            # This is a simplified approach - in production, we'd track report_id during comparison
            for mismatch in all_mismatches:
                errors_with_report_id.append({
                    **mismatch,
                    'report_id': 'unknown'  # Would be tracked during validation
                })
            
            error_analysis = self.error_analyzer.analyze_errors(errors_with_report_id)
            
            if self.verbose:
                print(f"  Total errors: {error_analysis['total_errors']}")
                print(f"  Error categories: {list(error_analysis['category_summary'].keys())}")
        else:
            print("  ✓ No classification errors detected!")
        
        # Step 3: Generate reports
        self._print_progress("Generating validation reports...")
        
        # Generate validation report
        validation_report = self.report_generator.generate_validation_report(
            validation_results=validation_results,
            error_analysis=error_analysis
        )
        
        validation_report_path = self.output_dir / 'MILESTONE_1_VALIDATION_REPORT.md'
        self.report_generator.save_report(validation_report, str(validation_report_path))
        
        # Generate error analysis report if there are errors
        if error_analysis and error_analysis.get('total_errors', 0) > 0:
            error_report = self.error_analyzer.generate_error_report(error_analysis)
            error_report_path = self.output_dir / 'ERROR_ANALYSIS_REPORT.md'
            self.report_generator.save_report(error_report, str(error_report_path))
        
        # Generate certification if targets are met
        target_met = validation_results.get('target_met', False)
        if target_met:
            self._print_progress("Generating Milestone 1 certification...")
            certification = self.report_generator.generate_certification(validation_results)
            certification_path = self.output_dir / 'MILESTONE_1_CERTIFICATION.md'
            self.report_generator.save_report(certification, str(certification_path))
        
        # Step 4: Save detailed results to JSON
        self._print_progress("Saving detailed results...")
        
        results_json_path = self.output_dir / 'validation_results.json'
        with open(results_json_path, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        # Save validation timestamp
        self._save_validation_timestamp()
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Requirement 9.2: Complete in under 5 minutes
        if elapsed_time > 300:  # 5 minutes
            print(f"\n⚠️  WARNING: Validation took {elapsed_time:.1f}s (target: <300s)")
        
        # Print summary
        self._print_header("VALIDATION COMPLETE")
        
        # Requirement 9.4: Output summary to console
        print("Summary:")
        print(f"  Reports processed: {validation_results.get('reports_processed', 0)}")
        print(f"  Reports with errors: {validation_results.get('reports_with_errors', 0)}")
        print(f"  Classification accuracy: {accuracy_metrics.get('accuracy_percentage', 0)}%")
        print(f"  Target (≥98%): {'✓ MET' if target_met else '✗ NOT MET'}")
        print(f"  Elapsed time: {elapsed_time:.1f}s")
        print()
        
        print("Generated files:")
        print(f"  ✓ {validation_report_path}")
        if error_analysis and error_analysis.get('total_errors', 0) > 0:
            print(f"  ✓ {error_report_path}")
        if target_met:
            print(f"  ✓ {certification_path}")
        print(f"  ✓ {results_json_path}")
        print()
        
        if target_met:
            print("🎉 MILESTONE 1 COMPLETE! All targets achieved.")
        else:
            print("⚠️  Milestone 1 targets not yet met. Review error analysis for details.")
        
        print()
        
        return {
            'success': True,
            'validation_results': validation_results,
            'error_analysis': error_analysis,
            'elapsed_time': elapsed_time,
            'target_met': target_met
        }


def main():
    """Main entry point for validation pipeline."""
    parser = argparse.ArgumentParser(
        description='Run Milestone 1 validation pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python evaluation/run_validation.py
  
  # Run with custom directories
  python evaluation/run_validation.py --reports-dir data/test_reports --output-dir results
  
  # Run with verbose output
  python evaluation/run_validation.py --verbose
        """
    )
    
    parser.add_argument(
        '--reports-dir',
        default='data/test_reports',
        help='Directory containing test reports (default: data/test_reports)'
    )
    
    parser.add_argument(
        '--ground-truth-dir',
        default='evaluation/test_dataset/ground_truth',
        help='Directory containing ground truth files (default: evaluation/test_dataset/ground_truth)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='evaluation/results',
        help='Directory to save results (default: evaluation/results)'
    )
    
    parser.add_argument(
        '--skip-certification',
        action='store_true',
        help='Skip certification generation even if targets are met'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create and run validation runner
    runner = ValidationRunner(
        reports_dir=args.reports_dir,
        ground_truth_dir=args.ground_truth_dir,
        output_dir=args.output_dir,
        verbose=args.verbose
    )
    
    try:
        results = runner.run_validation()
        
        # Exit with appropriate code
        if results.get('success') and results.get('target_met'):
            sys.exit(0)  # Success
        elif results.get('success'):
            sys.exit(1)  # Validation ran but targets not met
        else:
            sys.exit(2)  # Validation failed
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
