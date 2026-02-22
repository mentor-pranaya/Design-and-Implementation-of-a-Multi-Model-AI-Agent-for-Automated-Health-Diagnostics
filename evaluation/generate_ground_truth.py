#!/usr/bin/env python3
"""
Command-line script for ground truth generation.

This script processes all test reports and generates ground truth JSON files
for validation purposes. It uses the GroundTruthGenerator class to extract
parameters, get reference ranges, and classify values.

Usage:
    python generate_ground_truth.py [--input INPUT_DIR] [--output OUTPUT_DIR] [--age AGE] [--sex SEX]

Examples:
    # Generate ground truth for all reports with default directories
    python generate_ground_truth.py

    # Specify custom directories
    python generate_ground_truth.py --input data/test_reports --output evaluation/test_dataset/ground_truth

    # Generate with patient demographics for age/sex-specific ranges
    python generate_ground_truth.py --age 45 --sex M
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.ground_truth_generator import GroundTruthGenerator


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate ground truth templates for blood test report validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate ground truth for all reports with default directories
  python generate_ground_truth.py

  # Specify custom directories
  python generate_ground_truth.py --input data/test_reports --output evaluation/test_dataset/ground_truth

  # Generate with patient demographics for age/sex-specific ranges
  python generate_ground_truth.py --age 45 --sex M
        """
    )
    
    parser.add_argument(
        '--input',
        '-i',
        type=str,
        default='data/test_reports',
        help='Input directory containing test reports (PDF/PNG files). Default: data/test_reports'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        default='evaluation/test_dataset/ground_truth',
        help='Output directory for ground truth JSON files. Default: evaluation/test_dataset/ground_truth'
    )
    
    parser.add_argument(
        '--age',
        '-a',
        type=int,
        default=None,
        help='Patient age for age-specific reference ranges (optional)'
    )
    
    parser.add_argument(
        '--sex',
        '-s',
        type=str,
        choices=['M', 'F', 'male', 'female'],
        default=None,
        help='Patient sex for sex-specific reference ranges (optional): M/F or male/female'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output with detailed progress information'
    )
    
    return parser.parse_args()


def normalize_sex(sex: str) -> str:
    """Normalize sex input to standard format."""
    if not sex:
        return None
    
    sex_lower = sex.lower()
    if sex_lower in ['m', 'male']:
        return 'M'
    elif sex_lower in ['f', 'female']:
        return 'F'
    return sex


def print_banner(title: str):
    """Print a formatted banner."""
    width = 70
    print(f"\n{'='*width}")
    print(f"{title.center(width)}")
    print(f"{'='*width}\n")


def print_summary_table(summary: dict):
    """Print a formatted summary table."""
    print("\nDetailed Report Summary:")
    print(f"{'='*70}")
    print(f"{'Report ID':<20} {'Source File':<30} {'Parameters':<10} {'Status':<10}")
    print(f"{'-'*70}")
    
    for report in summary['reports']:
        report_id = report.get('report_id', 'N/A')
        source_file = report.get('source_file', 'N/A')
        param_count = report.get('parameter_count', 0)
        status = report.get('status', 'unknown')
        
        # Truncate long filenames
        if len(source_file) > 28:
            source_file = source_file[:25] + "..."
        
        status_symbol = "✓" if status == "success" else "✗"
        print(f"{report_id:<20} {source_file:<30} {param_count:<10} {status_symbol} {status:<8}")
    
    print(f"{'='*70}\n")


def save_summary_report(summary: dict, output_dir: Path):
    """Save a detailed summary report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = output_dir / f"generation_summary_{timestamp}.json"
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary_file


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Normalize inputs
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    sex = normalize_sex(args.sex)
    
    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Print configuration
    print_banner("GROUND TRUTH GENERATION")
    print(f"Configuration:")
    print(f"  Input directory:  {input_dir}")
    print(f"  Output directory: {output_dir}")
    print(f"  Patient age:      {args.age if args.age else 'Not specified (using default ranges)'}")
    print(f"  Patient sex:      {sex if sex else 'Not specified (using default ranges)'}")
    print(f"  Verbose mode:     {'Enabled' if args.verbose else 'Disabled'}")
    print()
    
    # Initialize generator
    try:
        print("Initializing ground truth generator...")
        generator = GroundTruthGenerator()
        print("✓ Generator initialized successfully\n")
    except Exception as e:
        print(f"✗ Failed to initialize generator: {e}")
        sys.exit(1)
    
    # Generate templates
    try:
        summary = generator.generate_all_templates(
            reports_dir=str(input_dir),
            output_dir=str(output_dir),
            age=args.age,
            sex=sex
        )
    except Exception as e:
        print(f"\n✗ Generation failed with error: {e}")
        sys.exit(1)
    
    # Print detailed summary if verbose
    if args.verbose:
        print_summary_table(summary)
    
    # Print final statistics
    print_banner("GENERATION STATISTICS")
    print(f"Total reports processed:  {summary['total_reports']}")
    print(f"Successfully generated:   {summary['successful']} ({summary['successful']/summary['total_reports']*100:.1f}%)")
    print(f"Failed:                   {summary['failed']}")
    
    if summary['successful'] > 0:
        total_params = sum(r.get('parameter_count', 0) for r in summary['reports'] if r.get('status') == 'success')
        avg_params = total_params / summary['successful']
        print(f"Total parameters:         {total_params}")
        print(f"Average per report:       {avg_params:.1f}")
    
    # Print errors if any
    if summary['errors']:
        print(f"\n{'='*70}")
        print("ERRORS:")
        print(f"{'='*70}")
        for error in summary['errors']:
            print(f"  Report: {error['report']}")
            print(f"  Error:  {error['error']}\n")
    
    # Save summary report
    summary_file = save_summary_report(summary, output_dir)
    print(f"\nDetailed summary saved to: {summary_file}")
    
    # Print next steps
    print_banner("NEXT STEPS")
    print("1. Review the generated ground truth files in:")
    print(f"   {output_dir}")
    print()
    print("2. Manually verify each file by comparing against original reports:")
    print("   - Check that extracted values match the report")
    print("   - Verify classifications are correct (Normal/High/Low)")
    print("   - Correct any errors and add notes")
    print("   - Set 'verified': true when complete")
    print()
    print("3. Run the validation pipeline once all files are verified:")
    print("   python evaluation/run_validation.py")
    print()
    
    # Exit with appropriate code
    if summary['failed'] > 0:
        print(f"⚠ Warning: {summary['failed']} report(s) failed to process")
        sys.exit(1)
    else:
        print("✓ All reports processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
