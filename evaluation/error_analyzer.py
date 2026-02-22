"""
Error Analyzer Module

Analyzes classification errors and identifies patterns.
Validates Requirements 5.1, 5.2, 5.3, 5.4, 5.5 from milestone-1-validation spec.
"""

from typing import Dict, List, Any
from collections import defaultdict


class ErrorAnalyzer:
    """Analyzes classification errors and identifies patterns."""
    
    def __init__(self):
        """Initialize error analyzer."""
        self.error_categories = [
            'extraction_error',
            'reference_range_error',
            'classification_logic_error',
            'edge_case'
        ]
    
    def categorize_error(self, error: Dict) -> str:
        """
        Categorize an error by type.
        
        Validates Requirement 5.2: Categorize errors by type
        
        Args:
            error: Error details with keys:
                - parameter: Parameter name
                - system_value: Value extracted by system
                - ground_truth_value: Correct value from ground truth
                - system_classification: System's classification
                - ground_truth_classification: Correct classification
                - reference_range: Reference range used (dict with min/max)
                
        Returns:
            Error category: extraction_error, reference_range_error,
                          classification_logic_error, or edge_case
        """
        sys_value = error.get('system_value')
        gt_value = error.get('ground_truth_value')
        sys_classification = error.get('system_classification')
        gt_classification = error.get('ground_truth_classification')
        ref_range = error.get('reference_range', {})
        
        # Check if values are different (extraction error)
        if sys_value is not None and gt_value is not None:
            # Allow small floating point differences
            if abs(sys_value - gt_value) > 0.01:
                return 'extraction_error'
        
        # Check if it's an edge case (within 5% of boundaries)
        # Requirement 5.4: Edge case detection
        if gt_value is not None and ref_range:
            min_val = ref_range.get('min')
            max_val = ref_range.get('max')
            
            if min_val is not None and max_val is not None:
                range_span = max_val - min_val
                threshold = range_span * 0.05  # 5% of range
                
                # Check if value is within 5% of either boundary
                near_min = abs(gt_value - min_val) <= threshold
                near_max = abs(gt_value - max_val) <= threshold
                
                if near_min or near_max:
                    return 'edge_case'
        
        # Check if reference range might be wrong
        # This is harder to detect automatically, but we can flag suspicious cases
        if sys_value is not None and ref_range:
            min_val = ref_range.get('min')
            max_val = ref_range.get('max')
            
            # If the value is way outside the range but classified as Normal in GT,
            # or inside the range but classified as High/Low in GT,
            # it might be a reference range issue
            if min_val is not None and max_val is not None:
                value_in_range = min_val <= sys_value <= max_val
                gt_is_normal = gt_classification == 'Normal'
                
                if value_in_range != gt_is_normal:
                    return 'reference_range_error'
        
        # Otherwise, it's a classification logic error
        # (correct value, correct range, wrong classification)
        return 'classification_logic_error'
    
    def identify_systematic_errors(self, errors: List[Dict]) -> List[Dict]:
        """
        Identify errors that occur across multiple reports.
        
        Validates Requirement 5.3: Flag systematic errors (same parameter failing ≥3 times)
        
        Args:
            errors: List of all classification errors
            
        Returns:
            List of systematic errors with frequency counts
        """
        # Count errors by parameter name
        parameter_errors = defaultdict(list)
        
        for error in errors:
            param_name = error.get('parameter', '').lower()
            parameter_errors[param_name].append(error)
        
        # Find parameters that fail 3 or more times
        systematic = []
        
        for param_name, param_errors in parameter_errors.items():
            if len(param_errors) >= 3:
                # Calculate statistics for this parameter
                categories = [self.categorize_error(e) for e in param_errors]
                category_counts = defaultdict(int)
                for cat in categories:
                    category_counts[cat] += 1
                
                systematic.append({
                    'parameter': param_name,
                    'frequency': len(param_errors),
                    'errors': param_errors,
                    'category_breakdown': dict(category_counts),
                    'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0]
                })
        
        # Sort by frequency (most common first)
        systematic.sort(key=lambda x: x['frequency'], reverse=True)
        
        return systematic
    
    def analyze_errors(self, errors: List[Dict]) -> Dict:
        """
        Analyze all errors and identify patterns.
        
        Validates Requirements 5.1, 5.2, 5.3, 5.4
        
        Args:
            errors: List of classification errors from validation pipeline
            
        Returns:
            Analysis dictionary with categories, patterns, and recommendations
        """
        if not errors:
            return {
                'total_errors': 0,
                'by_category': {},
                'category_summary': {},
                'systematic_errors': [],
                'edge_cases': [],
                'recommendations': [
                    "No errors detected. System is performing within expected parameters."
                ]
            }
        
        # Categorize all errors (Requirement 5.2)
        categorized = defaultdict(list)
        
        for error in errors:
            category = self.categorize_error(error)
            
            # Requirement 5.1: Ensure all required fields are logged
            error_with_category = {
                'parameter': error.get('parameter'),
                'report_id': error.get('report_id', 'unknown'),
                'system_value': error.get('system_value'),
                'ground_truth_value': error.get('ground_truth_value'),
                'system_classification': error.get('system_classification'),
                'ground_truth_classification': error.get('ground_truth_classification'),
                'reference_range': error.get('reference_range'),
                'category': category
            }
            
            categorized[category].append(error_with_category)
        
        # Identify systematic errors (Requirement 5.3)
        systematic_errors = self.identify_systematic_errors(errors)
        
        # Separate edge cases (Requirement 5.4)
        edge_cases = categorized.get('edge_case', [])
        
        # Generate category summary
        category_summary = {
            category: len(errors_list)
            for category, errors_list in categorized.items()
        }
        
        # Generate recommendations based on error patterns
        recommendations = self._generate_recommendations(
            categorized,
            systematic_errors,
            edge_cases
        )
        
        return {
            'total_errors': len(errors),
            'by_category': dict(categorized),
            'category_summary': category_summary,
            'systematic_errors': systematic_errors,
            'edge_cases': edge_cases,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(
        self,
        categorized: Dict[str, List[Dict]],
        systematic_errors: List[Dict],
        edge_cases: List[Dict]
    ) -> List[str]:
        """
        Generate recommendations for fixing errors.
        
        Validates Requirement 5.5: Generate recommendations
        
        Args:
            categorized: Errors grouped by category
            systematic_errors: Systematic errors identified
            edge_cases: Edge case errors
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Recommendations for extraction errors
        extraction_errors = categorized.get('extraction_error', [])
        if extraction_errors:
            recommendations.append(
                f"EXTRACTION ERRORS ({len(extraction_errors)}): "
                f"Review extraction patterns and OCR quality. "
                f"Consider improving text preprocessing or pattern matching."
            )
        
        # Recommendations for reference range errors
        ref_range_errors = categorized.get('reference_range_error', [])
        if ref_range_errors:
            recommendations.append(
                f"REFERENCE RANGE ERRORS ({len(ref_range_errors)}): "
                f"Verify reference ranges in UnifiedReferenceManager. "
                f"Check if age/sex-specific ranges are being applied correctly."
            )
        
        # Recommendations for classification logic errors
        logic_errors = categorized.get('classification_logic_error', [])
        if logic_errors:
            recommendations.append(
                f"CLASSIFICATION LOGIC ERRORS ({len(logic_errors)}): "
                f"Review classification logic in validation pipeline. "
                f"Ensure boundary conditions are handled correctly."
            )
        
        # Recommendations for edge cases
        if edge_cases:
            recommendations.append(
                f"EDGE CASES ({len(edge_cases)}): "
                f"These are borderline values within 5% of reference range boundaries. "
                f"Consider if these require special handling or if the reference ranges need adjustment."
            )
        
        # Recommendations for systematic errors
        if systematic_errors:
            top_systematic = systematic_errors[0]
            recommendations.append(
                f"SYSTEMATIC ERROR DETECTED: Parameter '{top_systematic['parameter']}' "
                f"fails {top_systematic['frequency']} times. "
                f"Priority investigation required. "
                f"Most common issue: {top_systematic['most_common_category']}."
            )
        
        # Always provide at least one recommendation
        if not recommendations:
            recommendations.append(
                "No errors detected. System is performing within expected parameters."
            )
        
        return recommendations
    
    def generate_error_report(self, analysis: Dict, report_id: str = None) -> str:
        """
        Generate markdown error analysis report.
        
        Validates Requirement 5.5: Generate error analysis report
        
        Args:
            analysis: Error analysis results from analyze_errors()
            report_id: Optional report ID for per-report analysis
            
        Returns:
            Markdown formatted error analysis report
        """
        lines = []
        
        # Header
        lines.append("# Error Analysis Report")
        lines.append("")
        if report_id:
            lines.append(f"**Report ID:** {report_id}")
            lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"**Total Errors:** {analysis['total_errors']}")
        lines.append("")
        
        if analysis['total_errors'] == 0:
            lines.append("✓ No errors detected. All classifications match ground truth.")
            lines.append("")
            return "\n".join(lines)
        
        # Category breakdown
        lines.append("## Error Categories")
        lines.append("")
        
        category_summary = analysis.get('category_summary', {})
        for category, count in sorted(category_summary.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / analysis['total_errors']) * 100
            lines.append(f"- **{category}**: {count} ({percentage:.1f}%)")
        lines.append("")
        
        # Systematic errors
        systematic = analysis.get('systematic_errors', [])
        if systematic:
            lines.append("## Systematic Errors")
            lines.append("")
            lines.append("Parameters failing across multiple reports (≥3 occurrences):")
            lines.append("")
            
            for sys_error in systematic:
                lines.append(f"### {sys_error['parameter'].title()}")
                lines.append(f"- **Frequency:** {sys_error['frequency']} reports")
                lines.append(f"- **Primary Issue:** {sys_error['most_common_category']}")
                lines.append("")
                
                # Show category breakdown
                lines.append("**Category Breakdown:**")
                for cat, count in sys_error['category_breakdown'].items():
                    lines.append(f"  - {cat}: {count}")
                lines.append("")
        
        # Edge cases
        edge_cases = analysis.get('edge_cases', [])
        if edge_cases:
            lines.append("## Edge Cases")
            lines.append("")
            lines.append(f"Found {len(edge_cases)} borderline values within 5% of reference range boundaries:")
            lines.append("")
            
            for edge in edge_cases[:5]:  # Show first 5
                param = edge.get('parameter', 'unknown')
                value = edge.get('ground_truth_value', edge.get('system_value'))
                ref_range = edge.get('reference_range', {})
                lines.append(f"- **{param}**: {value} (range: {ref_range.get('min')}-{ref_range.get('max')})")
            
            if len(edge_cases) > 5:
                lines.append(f"- ... and {len(edge_cases) - 5} more")
            lines.append("")
        
        # Detailed error list by category
        lines.append("## Detailed Error List")
        lines.append("")
        
        by_category = analysis.get('by_category', {})
        for category in self.error_categories:
            errors = by_category.get(category, [])
            if errors:
                lines.append(f"### {category.replace('_', ' ').title()}")
                lines.append("")
                
                for error in errors[:10]:  # Show first 10 per category
                    param = error.get('parameter', 'unknown')
                    sys_class = error.get('system_classification', 'N/A')
                    gt_class = error.get('ground_truth_classification', 'N/A')
                    value = error.get('ground_truth_value', error.get('system_value', 'N/A'))
                    
                    lines.append(f"- **{param}**: System={sys_class}, Ground Truth={gt_class}, Value={value}")
                
                if len(errors) > 10:
                    lines.append(f"- ... and {len(errors) - 10} more")
                lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        
        recommendations = analysis.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
            lines.append("")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    analyzer = ErrorAnalyzer()
    
    # Example errors
    example_errors = [
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
    
    # Analyze errors
    analysis = analyzer.analyze_errors(example_errors)
    
    # Generate report
    report = analyzer.generate_error_report(analysis)
    print(report)
