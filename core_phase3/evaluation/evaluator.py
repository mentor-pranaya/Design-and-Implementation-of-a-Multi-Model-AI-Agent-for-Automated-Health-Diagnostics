"""
Evaluation Engine - Phase 3A
Reference-based evaluation of extracted medical parameters.

This is the foundational layer of Phase 3 that:
1. Takes extracted parameters from Phase 2
2. Classifies each against authoritative reference ranges
3. Generates evaluation results with severity levels
4. Prepares data for pattern recognition and recommendations

Architecture Position:
Phase 2 (Extraction) → Phase 3A (Evaluation) → Phase 3B (Pattern Analysis) → Phase 3C (Recommendations)

Design Philosophy:
- Evidence-based, not heuristic
- Clinically grounded through reference ranges
- Transparent and auditable
- Separates evaluation from recommendation
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_base.reference_manager import ReferenceRangeManager, EvaluationStatus


class ParameterEvaluator:
    """
    Evaluates extracted medical parameters against reference ranges.
    
    Responsibilities:
    1. Accept structured parameters from Phase 2
    2. Evaluate each parameter using ReferenceRangeManager
    3. Classify status (Low/Normal/High/Critical)
    4. Assess severity (Mild/Moderate/Severe)
    5. Generate comprehensive evaluation report
    """
    
    def __init__(self):
        """Initialize the evaluator with reference range manager."""
        self.reference_manager = ReferenceRangeManager()
        print("✓ Parameter Evaluator initialized")
    
    def evaluate_parameters(
        self,
        extracted_parameters: List[Dict[str, Any]],
        patient_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate all extracted parameters against reference ranges.
        
        Args:
            extracted_parameters: List of extracted parameters from Phase 2
                Format: [{"parameter": "Hemoglobin", "value": 12.5, "unit": "g/dL"}, ...]
            patient_info: Optional patient demographics
                Format: {"sex": "female", "age": 45}
        
        Returns:
            Comprehensive evaluation report with:
            - Individual parameter evaluations
            - Summary of abnormal findings
            - Risk indicators
            - Flags for pattern recognition
        """
        if not extracted_parameters:
            return {
                'status': 'error',
                'message': 'No parameters provided for evaluation',
                'evaluations': []
            }
        
        # Extract patient demographics
        sex = patient_info.get('sex') if patient_info else None
        age = patient_info.get('age') if patient_info else None
        
        # Evaluate each parameter
        evaluations = []
        abnormal_findings = []
        critical_findings = []
        
        for param in extracted_parameters:
            parameter_name = param.get('parameter')
            value = param.get('value')
            
            if parameter_name is None or value is None:
                continue
            
            # Perform evaluation
            evaluation = self.reference_manager.evaluate_value(
                parameter=parameter_name,
                value=value,
                sex=sex,
                age=age
            )
            
            # Add original extracted info
            evaluation['extracted_unit'] = param.get('unit')
            evaluations.append(evaluation)
            
            # Flag abnormal findings
            if evaluation['status'] not in [EvaluationStatus.NORMAL, EvaluationStatus.UNKNOWN]:
                abnormal_findings.append({
                    'parameter': parameter_name,
                    'status': evaluation['status'].value,
                    'severity': evaluation['severity'],
                    'value': value
                })
            
            # Flag critical findings
            if evaluation['status'] in [EvaluationStatus.CRITICAL_LOW, EvaluationStatus.CRITICAL_HIGH]:
                critical_findings.append({
                    'parameter': parameter_name,
                    'status': evaluation['status'].value,
                    'value': value,
                    'immediate_action': 'Requires immediate medical attention'
                })
        
        # Generate summary
        summary = self._generate_summary(evaluations, abnormal_findings, critical_findings)
        
        # Create comprehensive report
        evaluation_report = {
            'phase': 'Phase 3A: Reference-Based Evaluation',
            'status': 'success',
            'patient_info': patient_info or {'sex': 'not_specified', 'age': 'not_specified'},
            'total_parameters_evaluated': len(evaluations),
            'parameters_with_reference': sum(1 for e in evaluations if e['reference_available']),
            'parameters_without_reference': sum(1 for e in evaluations if not e['reference_available']),
            'evaluations': evaluations,
            'abnormal_findings': abnormal_findings,
            'critical_findings': critical_findings,
            'summary': summary,
            'flags_for_pattern_recognition': self._generate_pattern_flags(evaluations)
        }
        
        return evaluation_report
    
    def _generate_summary(
        self,
        evaluations: List[Dict[str, Any]],
        abnormal_findings: List[Dict[str, Any]],
        critical_findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics from evaluations.
        
        Args:
            evaluations: All parameter evaluations
            abnormal_findings: List of abnormal findings
            critical_findings: List of critical findings
        
        Returns:
            Summary dictionary with counts and statistics
        """
        # Count by status
        status_counts = {
            'normal': 0,
            'low': 0,
            'high': 0,
            'borderline': 0,
            'critical': 0,
            'unknown': 0
        }
        
        # Count by severity
        severity_counts = {
            'mild': 0,
            'moderate': 0,
            'severe': 0
        }
        
        for evaluation in evaluations:
            status = evaluation['status']
            severity = evaluation.get('severity')
            
            if status == EvaluationStatus.NORMAL:
                status_counts['normal'] += 1
            elif status == EvaluationStatus.LOW:
                status_counts['low'] += 1
            elif status in [EvaluationStatus.HIGH, EvaluationStatus.BORDERLINE_HIGH]:
                status_counts['high'] += 1
            elif status in [EvaluationStatus.CRITICAL_LOW, EvaluationStatus.CRITICAL_HIGH]:
                status_counts['critical'] += 1
            elif status == EvaluationStatus.UNKNOWN:
                status_counts['unknown'] += 1
            
            if severity:
                severity_key = severity.lower()
                if severity_key in severity_counts:
                    severity_counts[severity_key] += 1
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            len(evaluations), 
            abnormal_findings, 
            critical_findings
        )
        
        return {
            'status_counts': status_counts,
            'severity_counts': severity_counts,
            'abnormal_count': len(abnormal_findings),
            'critical_count': len(critical_findings),
            'interpretation': interpretation
        }
    
    def _generate_interpretation(
        self,
        total_params: int,
        abnormal_findings: List[Dict[str, Any]],
        critical_findings: List[Dict[str, Any]]
    ) -> str:
        """
        Generate human-readable interpretation of evaluation.
        
        Args:
            total_params: Total parameters evaluated
            abnormal_findings: Abnormal findings list
            critical_findings: Critical findings list
        
        Returns:
            Interpretation string
        """
        if critical_findings:
            return (
                f"CRITICAL: {len(critical_findings)} parameter(s) require immediate medical attention. "
                f"Additionally, {len(abnormal_findings)} abnormal finding(s) detected."
            )
        elif len(abnormal_findings) > total_params * 0.5:
            return (
                f"Multiple abnormalities detected ({len(abnormal_findings)}/{total_params} parameters). "
                f"Comprehensive medical evaluation recommended."
            )
        elif abnormal_findings:
            return (
                f"{len(abnormal_findings)} parameter(s) outside normal range. "
                f"Follow-up with healthcare provider recommended."
            )
        else:
            return "All evaluated parameters within normal reference ranges."
    
    def _generate_pattern_flags(
        self,
        evaluations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate flags for pattern recognition (Phase 3B).
        
        This bridges evaluation to pattern-based analysis by identifying
        parameter combinations that suggest specific conditions.
        
        Args:
            evaluations: All parameter evaluations
        
        Returns:
            List of pattern flags to guide Phase 3B analysis
        """
        flags = []
        
        # Create lookup for quick access
        eval_dict = {
            e['parameter']: e 
            for e in evaluations 
            if e['reference_available']
        }
        
        # Flag 1: Anemia indicators
        if 'Hemoglobin' in eval_dict:
            hgb_status = eval_dict['Hemoglobin']['status']
            if hgb_status in [EvaluationStatus.LOW, EvaluationStatus.CRITICAL_LOW]:
                flags.append({
                    'pattern_type': 'Anemia Indicator',
                    'triggered_by': ['Hemoglobin'],
                    'severity': eval_dict['Hemoglobin']['severity'],
                    'confidence': 'high'
                })
        
        # Flag 2: Diabetes risk indicators
        glucose_high = False
        hba1c_high = False
        
        if 'Glucose' in eval_dict:
            glucose_status = eval_dict['Glucose']['status']
            if glucose_status in [EvaluationStatus.HIGH, EvaluationStatus.BORDERLINE_HIGH]:
                glucose_high = True
        
        if 'HbA1c' in eval_dict:
            hba1c_status = eval_dict['HbA1c']['status']
            if hba1c_status in [EvaluationStatus.HIGH, EvaluationStatus.BORDERLINE_HIGH]:
                hba1c_high = True
        
        if glucose_high or hba1c_high:
            triggered = []
            if glucose_high:
                triggered.append('Glucose')
            if hba1c_high:
                triggered.append('HbA1c')
            
            flags.append({
                'pattern_type': 'Diabetes Risk',
                'triggered_by': triggered,
                'confidence': 'high' if hba1c_high else 'moderate'
            })
        
        # Flag 3: Cardiovascular risk (lipid panel)
        lipid_issues = []
        
        if 'LDL' in eval_dict and eval_dict['LDL']['status'] == EvaluationStatus.HIGH:
            lipid_issues.append('LDL')
        if 'HDL' in eval_dict and eval_dict['HDL']['status'] == EvaluationStatus.LOW:
            lipid_issues.append('HDL')
        if 'Triglycerides' in eval_dict and eval_dict['Triglycerides']['status'] == EvaluationStatus.HIGH:
            lipid_issues.append('Triglycerides')
        if 'Cholesterol Total' in eval_dict and eval_dict['Cholesterol Total']['status'] == EvaluationStatus.HIGH:
            lipid_issues.append('Cholesterol Total')
        
        if lipid_issues:
            flags.append({
                'pattern_type': 'High Cholesterol',
                'triggered_by': lipid_issues,
                'confidence': 'high' if len(lipid_issues) >= 2 else 'moderate'
            })
        
        # Flag 4: Kidney function concerns
        kidney_markers = []
        
        if 'Creatinine' in eval_dict and eval_dict['Creatinine']['status'] == EvaluationStatus.HIGH:
            kidney_markers.append('Creatinine')
        if 'BUN' in eval_dict and eval_dict['BUN']['status'] == EvaluationStatus.HIGH:
            kidney_markers.append('BUN')
        
        if kidney_markers:
            flags.append({
                'pattern_type': 'Kidney Function Alert',
                'triggered_by': kidney_markers,
                'confidence': 'moderate'
            })
        
        # Flag 5: Liver function concerns
        liver_markers = []
        
        if 'ALT' in eval_dict and eval_dict['ALT']['status'] == EvaluationStatus.HIGH:
            liver_markers.append('ALT')
        if 'AST' in eval_dict and eval_dict['AST']['status'] == EvaluationStatus.HIGH:
            liver_markers.append('AST')
        if 'Bilirubin Total' in eval_dict and eval_dict['Bilirubin Total']['status'] == EvaluationStatus.HIGH:
            liver_markers.append('Bilirubin Total')
        
        if liver_markers:
            flags.append({
                'pattern_type': 'Liver Function Alert',
                'triggered_by': liver_markers,
                'confidence': 'moderate' if len(liver_markers) >= 2 else 'low'
            })
        
        return flags
    
    def evaluate_single_parameter(
        self,
        parameter: str,
        value: float,
        sex: Optional[str] = None,
        age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to evaluate a single parameter.
        
        Args:
            parameter: Parameter name
            value: Measured value
            sex: Optional sex
            age: Optional age
        
        Returns:
            Evaluation result
        """
        return self.reference_manager.evaluate_value(
            parameter=parameter,
            value=value,
            sex=sex,
            age=age
        )


# Convenience function for quick evaluation
def evaluate_blood_report(
    parameters: List[Dict[str, Any]],
    patient_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Quick evaluation function without instantiating evaluator.
    
    Args:
        parameters: List of extracted parameters
        patient_info: Optional patient information
    
    Returns:
        Complete evaluation report
    """
    evaluator = ParameterEvaluator()
    return evaluator.evaluate_parameters(parameters, patient_info)
