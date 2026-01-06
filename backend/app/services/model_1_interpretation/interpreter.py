"""
Model 1: Parameter Interpretation
Rule-based classification of blood parameters
"""

import logging
from typing import Dict, List, Any, Optional
from app.services.reference_ranges import reference_range_service, Gender, ParameterStatus

logger = logging.getLogger(__name__)

class ParameterInterpreter:
    """Interpret individual blood parameters against reference ranges"""
    
    def __init__(self):
        self.ref_service = reference_range_service
    
    async def interpret(
        self, 
        validated_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Interpret validated parameters
        Returns: Dict with interpretations for each parameter
        """
        parameters = validated_data.get("validated_parameters", [])
        
        # Extract user context
        gender = None
        age = None
        
        if user_context:
            gender_str = user_context.get("gender")
            if gender_str:
                try:
                    gender = Gender(gender_str.lower())
                except ValueError:
                    gender = None
            
            age = user_context.get("age")
        
        interpretations = []
        critical_findings = []
        abnormal_findings = []
        normal_findings = []
        
        for param in parameters:
            interpretation = self._interpret_parameter(param, gender, age)
            interpretations.append(interpretation)
            
            # Categorize by status
            status = interpretation["status"]
            if status in [ParameterStatus.CRITICAL_LOW, ParameterStatus.CRITICAL_HIGH]:
                critical_findings.append(interpretation)
            elif status in [ParameterStatus.LOW, ParameterStatus.HIGH, 
                          ParameterStatus.BORDERLINE_LOW, ParameterStatus.BORDERLINE_HIGH]:
                abnormal_findings.append(interpretation)
            else:
                normal_findings.append(interpretation)
        
        return {
            "interpretations": interpretations,
            "summary": {
                "total_parameters": len(interpretations),
                "critical_count": len(critical_findings),
                "abnormal_count": len(abnormal_findings),
                "normal_count": len(normal_findings)
            },
            "critical_findings": critical_findings,
            "abnormal_findings": abnormal_findings,
            "normal_findings": normal_findings,
            "user_context": {
                "gender": gender.value if gender else None,
                "age": age
            }
        }
    
    def _interpret_parameter(
        self, 
        param: Dict, 
        gender: Optional[Gender],
        age: Optional[int]
    ) -> Dict[str, Any]:
        """Interpret a single parameter"""
        
        name = param["name"]
        value = param["value"]
        unit = param["unit"]
        
        # Classify value
        status, explanation = self.ref_service.classify_value(
            name, value, gender, age
        )
        
        # Get clinical significance
        clinical_significance = self.ref_service.get_clinical_significance(name, status)
        
        # Determine severity level
        severity = self._determine_severity(status)
        
        # Get reference range
        ref_range = self.ref_service.get_reference_range(name, gender, age)
        
        return {
            "parameter": name,
            "value": value,
            "unit": unit,
            "status": status.value,
            "severity": severity,
            "explanation": explanation,
            "clinical_significance": clinical_significance,
            "reference_range": {
                "min": ref_range.get("normal_min") if ref_range else None,
                "max": ref_range.get("normal_max") if ref_range else None
            },
            "confidence": param.get("confidence", 1.0)
        }
    
    def _determine_severity(self, status: ParameterStatus) -> str:
        """Determine severity level from status"""
        severity_map = {
            ParameterStatus.CRITICAL_LOW: "critical",
            ParameterStatus.CRITICAL_HIGH: "critical",
            ParameterStatus.LOW: "moderate",
            ParameterStatus.HIGH: "moderate",
            ParameterStatus.BORDERLINE_LOW: "mild",
            ParameterStatus.BORDERLINE_HIGH: "mild",
            ParameterStatus.NORMAL: "normal"
        }
        
        return severity_map.get(status, "unknown")

# Global instance
parameter_interpreter = ParameterInterpreter()
