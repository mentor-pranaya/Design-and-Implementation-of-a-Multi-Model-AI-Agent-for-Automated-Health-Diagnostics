"""
Integration test for ErrorAnalyzer with ValidationPipeline

This script demonstrates how the ErrorAnalyzer integrates with the validation pipeline.
"""

from error_analyzer import ErrorAnalyzer


def test_integration():
    """Test ErrorAnalyzer with sample validation results."""
    
    # Create analyzer
    analyzer = ErrorAnalyzer()
    
    # Sample errors from validation pipeline (matching the structure from validation_pipeline.py)
    sample_errors = [
        {
            'parameter': 'glucose',
            'system_name': 'Glucose',
            'report_id': 'report_001',
            'system_value': 110,
            'ground_truth_value': 110,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        {
            'parameter': 'hemoglobin',
            'system_name': 'Hemoglobin',
            'report_id': 'report_002',
            'system_value': 13.1,
            'ground_truth_value': 13.1,
            'system_classification': 'Low',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 13.0, 'max': 17.5}
        },
        {
            'parameter': 'glucose',
            'system_name': 'Glucose',
            'report_id': 'report_003',
            'system_value': 105,
            'ground_truth_value': 105,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        },
        {
            'parameter': 'glucose',
            'system_name': 'Glucose',
            'report_id': 'report_005',
            'system_value': 102,
            'ground_truth_value': 102,
            'system_classification': 'High',
            'ground_truth_classification': 'Normal',
            'reference_range': {'min': 70, 'max': 100}
        }
    ]
    
    print("="*70)
    print("ERROR ANALYZER INTEGRATION TEST")
    print("="*70)
    print()
    
    # Analyze errors
    print("Analyzing errors...")
    analysis = analyzer.analyze_errors(sample_errors)
    
    print(f"Total errors: {analysis['total_errors']}")
    print(f"Categories: {list(analysis['category_summary'].keys())}")
    print(f"Systematic errors: {len(analysis['systematic_errors'])}")
    print(f"Edge cases: {len(analysis['edge_cases'])}")
    print()
    
    # Show systematic errors
    if analysis['systematic_errors']:
        print("SYSTEMATIC ERRORS DETECTED:")
        for sys_error in analysis['systematic_errors']:
            print(f"  - {sys_error['parameter']}: {sys_error['frequency']} occurrences")
            print(f"    Primary issue: {sys_error['most_common_category']}")
        print()
    
    # Generate report
    print("Generating error report...")
    report = analyzer.generate_error_report(analysis)
    
    print()
    print("="*70)
    print("ERROR ANALYSIS REPORT")
    print("="*70)
    print()
    print(report)
    
    # Save report to file
    output_path = "evaluation/ERROR_ANALYSIS_SAMPLE.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print(f"Report saved to: {output_path}")
    print()
    print("="*70)
    print("INTEGRATION TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_integration()
