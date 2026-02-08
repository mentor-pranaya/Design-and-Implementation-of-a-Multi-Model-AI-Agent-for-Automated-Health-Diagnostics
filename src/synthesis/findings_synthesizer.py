"""
Findings Synthesis Engine
Aggregates and combines outputs from all analysis models into a coherent summary
"""

from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FindingsSynthesizer:
    """Synthesize findings from all analysis models"""
    
    def __init__(self):
        self.synthesized_findings = {}
    
    def synthesize(self, 
                  interpretations: List[Dict[str, Any]],
                  pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize findings from Model 1 and Model 2
        
        Args:
            interpretations: Parameter interpretations from Model 1
            pattern_analysis: Pattern analysis results from Model 2
            
        Returns:
            Synthesized findings dictionary
        """
        
        # Categorize parameters by status
        categorized_params = self._categorize_parameters(interpretations)
        
        # Synthesize key findings
        key_findings = self._identify_key_findings(
            categorized_params, 
            pattern_analysis
        )
        
        # Create priority list
        priority_issues = self._prioritize_issues(
            categorized_params,
            pattern_analysis
        )
        
        # Generate summary text
        summary_text = self._generate_summary_text(
            categorized_params,
            pattern_analysis,
            key_findings
        )
        
        self.synthesized_findings = {
            'categorized_parameters': categorized_params,
            'key_findings': key_findings,
            'priority_issues': priority_issues,
            'summary_text': summary_text,
            'overall_status': self._determine_overall_status(categorized_params, pattern_analysis)
        }
        
        logger.info("Findings synthesis completed")
        
        return self.synthesized_findings
    
    def _categorize_parameters(self, interpretations: List[Dict[str, Any]]) -> Dict[str, List]:
        """Categorize parameters by their status"""
        categories = {
            'critical': [],
            'abnormal': [],
            'borderline': [],
            'normal': []
        }
        
        for param in interpretations:
            status = param['status']
            param_summary = {
                'name': param['standard_name'],
                'value': param['value'],
                'unit': param['unit'],
                'reference_range': f"{param['reference_min']} - {param['reference_max']}",
                'status': status,
                'message': param['interpretation_message']
            }
            
            if status in ['critical_high', 'critical_low']:
                categories['critical'].append(param_summary)
            elif status in ['high', 'low']:
                categories['abnormal'].append(param_summary)
            elif status in ['borderline_high', 'borderline_low']:
                categories['borderline'].append(param_summary)
            else:
                categories['normal'].append(param_summary)
        
        return categories
    
    def _identify_key_findings(self, 
                              categorized_params: Dict[str, List],
                              pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify the most important findings"""
        key_findings = []
        
        # Critical parameters are always key findings
        for param in categorized_params['critical']:
            key_findings.append({
                'type': 'critical_parameter',
                'severity': 'critical',
                'title': f"Critical: {param['name']} Level",
                'description': param['message'],
                'details': param
            })
        
        # Identified patterns are key findings
        for pattern in pattern_analysis.get('patterns', []):
            severity = 'high' if pattern['confidence'] >= 0.75 else 'moderate'
            key_findings.append({
                'type': 'clinical_pattern',
                'severity': severity,
                'title': pattern['description'],
                'description': f"Pattern identified with {pattern['confidence']*100:.0f}% confidence",
                'details': pattern
            })
        
        # High risk scores are key findings
        for risk_type, risk_data in pattern_analysis.get('risk_scores', {}).items():
            if risk_data['level'] in ['high', 'moderate']:
                key_findings.append({
                    'type': 'risk_score',
                    'severity': risk_data['level'],
                    'title': f"{risk_type.title()} Risk",
                    'description': risk_data['description'],
                    'details': risk_data
                })
        
        # Abnormal ratios
        for ratio_name, ratio_data in pattern_analysis.get('ratios', {}).items():
            if 'high risk' in ratio_data['interpretation'].lower():
                key_findings.append({
                    'type': 'abnormal_ratio',
                    'severity': 'moderate',
                    'title': ratio_data['description'],
                    'description': f"Ratio is {ratio_data['interpretation']} ({ratio_data['value']})",
                    'details': ratio_data
                })
        
        return key_findings
    
    def _prioritize_issues(self,
                          categorized_params: Dict[str, List],
                          pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create prioritized list of health issues"""
        issues = []
        
        # Priority 1: Critical parameters
        if categorized_params['critical']:
            issues.append({
                'priority': 1,
                'category': 'Critical Values',
                'count': len(categorized_params['critical']),
                'items': [p['name'] for p in categorized_params['critical']],
                'action_required': 'Immediate medical attention recommended'
            })
        
        # Priority 2: High-risk patterns or scores
        high_risk_items = []
        for pattern in pattern_analysis.get('patterns', []):
            if pattern['confidence'] >= 0.75:
                high_risk_items.append(pattern['description'])
        
        for risk_type, risk_data in pattern_analysis.get('risk_scores', {}).items():
            if risk_data['level'] == 'high':
                high_risk_items.append(f"{risk_type.title()} risk")
        
        if high_risk_items:
            issues.append({
                'priority': 2,
                'category': 'High Risk Indicators',
                'count': len(high_risk_items),
                'items': high_risk_items,
                'action_required': 'Consult healthcare provider soon'
            })
        
        # Priority 3: Abnormal parameters
        if categorized_params['abnormal']:
            issues.append({
                'priority': 3,
                'category': 'Abnormal Parameters',
                'count': len(categorized_params['abnormal']),
                'items': [p['name'] for p in categorized_params['abnormal']],
                'action_required': 'Medical consultation recommended'
            })
        
        # Priority 4: Borderline values
        if categorized_params['borderline']:
            issues.append({
                'priority': 4,
                'category': 'Borderline Values',
                'count': len(categorized_params['borderline']),
                'items': [p['name'] for p in categorized_params['borderline']],
                'action_required': 'Monitoring and lifestyle modifications recommended'
            })
        
        return issues
    
    def _generate_summary_text(self,
                               categorized_params: Dict[str, List],
                               pattern_analysis: Dict[str, Any],
                               key_findings: List[Dict[str, Any]]) -> str:
        """Generate human-readable summary text"""
        
        total_params = sum(len(params) for params in categorized_params.values())
        normal_count = len(categorized_params['normal'])
        
        summary = "BLOOD TEST ANALYSIS SUMMARY\n"
        summary += "=" * 60 + "\n\n"
        
        # Overall status
        summary += "OVERALL ASSESSMENT:\n"
        summary += f"Analyzed {total_params} parameters. "
        summary += f"{normal_count} within normal range.\n\n"
        
        # Critical findings
        if categorized_params['critical']:
            summary += "⚠️ CRITICAL FINDINGS:\n"
            for param in categorized_params['critical']:
                summary += f"  • {param['name']}: {param['value']} {param['unit']}\n"
                summary += f"    {param['message']}\n"
            summary += "\n"
        
        # Key findings
        if key_findings:
            summary += "KEY FINDINGS:\n"
            for i, finding in enumerate(key_findings[:5], 1):  # Top 5
                summary += f"{i}. {finding['title']}\n"
                summary += f"   {finding['description']}\n"
            summary += "\n"
        
        # Patterns
        if pattern_analysis.get('patterns'):
            summary += "IDENTIFIED PATTERNS:\n"
            for pattern in pattern_analysis['patterns']:
                summary += f"  • {pattern['description']} "
                summary += f"(Confidence: {pattern['confidence']*100:.0f}%)\n"
            summary += "\n"
        
        # Risk assessment
        if pattern_analysis.get('risk_scores'):
            summary += "RISK ASSESSMENT:\n"
            for risk_type, risk_data in pattern_analysis['risk_scores'].items():
                summary += f"  • {risk_type.title()}: {risk_data['level'].upper()} "
                summary += f"(Score: {risk_data['score']}/10)\n"
            summary += "\n"
        
        # Recommendations preview
        summary += "RECOMMENDATIONS:\n"
        summary += "Detailed recommendations have been generated based on your results.\n"
        summary += "Please review the personalized recommendations section below.\n"
        
        return summary
    
    def _determine_overall_status(self,
                                  categorized_params: Dict[str, List],
                                  pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine overall health status"""
        
        if categorized_params['critical']:
            status = 'critical'
            color = 'red'
            message = 'Critical values detected - immediate medical attention recommended'
        elif pattern_analysis.get('overall_risk_level', {}).get('level') == 'high':
            status = 'high_concern'
            color = 'orange'
            message = 'High risk indicators present - consult healthcare provider'
        elif categorized_params['abnormal'] or pattern_analysis.get('patterns'):
            status = 'needs_attention'
            color = 'yellow'
            message = 'Some abnormalities detected - medical consultation recommended'
        elif categorized_params['borderline']:
            status = 'monitor'
            color = 'blue'
            message = 'Borderline values present - monitoring recommended'
        else:
            status = 'healthy'
            color = 'green'
            message = 'All parameters within acceptable ranges'
        
        return {
            'status': status,
            'color': color,
            'message': message
        }
    
    def get_summary(self) -> str:
        """Get the synthesized summary text"""
        return self.synthesized_findings.get('summary_text', 'No summary available')