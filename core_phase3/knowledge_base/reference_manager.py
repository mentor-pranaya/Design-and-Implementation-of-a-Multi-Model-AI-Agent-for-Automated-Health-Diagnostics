"""
Reference Range Manager - Phase 3
Manages laboratory reference ranges for clinical evaluation.

This module provides:
- Reference range loading and lookup
- Age/sex-specific range selection
- Value classification (Low/Normal/High/Critical)
- Unit normalization
- Clinical significance retrieval

Design Philosophy:
- Data-driven, not hard-coded
- Extensible and maintainable
- Clinically grounded
- Academic rigor for evaluation
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from enum import Enum


class EvaluationStatus(Enum):
    """Status classifications for laboratory values."""
    CRITICAL_LOW = "Critical Low"
    LOW = "Low"
    NORMAL = "Normal"
    BORDERLINE_HIGH = "Borderline High"
    HIGH = "High"
    CRITICAL_HIGH = "Critical High"
    UNKNOWN = "Unknown"


class ReferenceRangeManager:
    """
    Manages laboratory reference ranges for evidence-based evaluation.
    
    Responsibilities:
    1. Load reference ranges from JSON
    2. Provide parameter lookup by name
    3. Select appropriate ranges based on sex/age
    4. Classify values against reference ranges
    5. Return clinical significance information
    """
    
    def __init__(self, reference_path: str = None):
        """
        Initialize the reference range manager.
        
        Args:
            reference_path: Path to reference_ranges.json
                          If None, uses default path relative to this module
        """
        if reference_path is None:
            script_dir = Path(__file__).parent
            reference_path = os.path.join(script_dir, 'reference_ranges.json')
        
        self.reference_path = reference_path
        self.reference_ranges = self._load_reference_ranges()
    
    def _load_reference_ranges(self) -> Dict[str, Any]:
        """
        Load reference ranges from JSON file.
        
        Returns:
            Dictionary of reference ranges
            
        Raises:
            FileNotFoundError: If reference file not found
            json.JSONDecodeError: If JSON is invalid
        """
        try:
            with open(self.reference_path, 'r', encoding='utf-8') as f:
                ranges = json.load(f)
            
            # Remove metadata from working dict
            if '_metadata' in ranges:
                metadata = ranges.pop('_metadata')
                print(f"✓ Loaded reference ranges")
                print(f"  Source: {metadata.get('source', 'Unknown')}")
            
            print(f"✓ {len(ranges)} parameters available for evaluation")
            return ranges
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Reference ranges file not found: {self.reference_path}\n"
                f"Ensure reference_ranges.json exists in knowledge_base/"
            )
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in reference ranges: {e}",
                e.doc, e.pos
            )
    
    def get_parameter_names(self) -> list:
        """
        Get list of all available parameter names.
        
        Returns:
            List of parameter names that can be evaluated
        """
        return list(self.reference_ranges.keys())
    
    def get_reference_range(
        self, 
        parameter: str, 
        sex: Optional[str] = None,
        age: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get reference range for a specific parameter.
        
        Args:
            parameter: Parameter name (e.g., "Hemoglobin", "Glucose")
            sex: Optional sex specification ("male" or "female")
            age: Optional age (for age-specific ranges in future)
        
        Returns:
            Dictionary containing reference range information
            None if parameter not found
        """
        # Normalize parameter name (handle case variations)
        param_normalized = self._normalize_parameter_name(parameter)
        
        if param_normalized not in self.reference_ranges:
            return None
        
        ref_range = self.reference_ranges[param_normalized].copy()
        
        # Select sex-specific range if available
        if sex and sex.lower() in ['male', 'female']:
            sex_key = sex.lower()
            if sex_key in ref_range:
                # Merge sex-specific range with general info
                sex_specific = ref_range[sex_key]
                ref_range.update(sex_specific)
        
        return ref_range
    
    def _normalize_parameter_name(self, parameter: str) -> str:
        """
        Normalize parameter name to match reference ranges.
        
        Handles common variations:
        - Case insensitivity
        - Common abbreviations
        - Whitespace variations
        
        Args:
            parameter: Raw parameter name
        
        Returns:
            Normalized parameter name
        """
        # Remove extra whitespace
        param = parameter.strip()
        
        # Check exact match first (case-sensitive)
        if param in self.reference_ranges:
            return param
        
        # Case-insensitive lookup
        param_lower = param.lower()
        for ref_param in self.reference_ranges:
            if ref_param.lower() == param_lower:
                return ref_param
        
        # Check full_name field for abbreviations
        for ref_param, ref_data in self.reference_ranges.items():
            if 'full_name' in ref_data:
                if ref_data['full_name'].lower() == param_lower:
                    return ref_param
        
        # Return original if no match found
        return param
    
    def evaluate_value(
        self,
        parameter: str,
        value: float,
        sex: Optional[str] = None,
        age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a laboratory value against reference ranges.
        
        Args:
            parameter: Parameter name
            value: Measured value
            sex: Optional sex ("male" or "female")
            age: Optional age
        
        Returns:
            Evaluation result containing:
            - status: EvaluationStatus enum
            - severity: "Mild", "Moderate", "Severe" (for abnormal values)
            - reference_range: The reference range used
            - deviation: How far from normal (percentage)
            - clinical_significance: Medical interpretation
        """
        ref_range = self.get_reference_range(parameter, sex, age)
        
        if ref_range is None:
            return {
                'parameter': parameter,
                'value': value,
                'status': EvaluationStatus.UNKNOWN,
                'message': f'No reference range available for {parameter}',
                'reference_available': False
            }
        
        # Classify the value
        status, severity = self._classify_value(value, ref_range)
        
        # Calculate deviation from normal range
        deviation = self._calculate_deviation(value, ref_range)
        
        return {
            'parameter': parameter,
            'value': value,
            'unit': ref_range.get('unit', 'N/A'),
            'status': status,
            'severity': severity,
            'reference_range': self._format_reference_range(ref_range),
            'deviation_percent': deviation,
            'clinical_significance': ref_range.get('clinical_significance', 'Not available'),
            'reference_available': True
        }
    
    def _classify_value(
        self, 
        value: float, 
        ref_range: Dict[str, Any]
    ) -> Tuple[EvaluationStatus, Optional[str]]:
        """
        Classify a value into status categories.
        
        Args:
            value: Measured value
            ref_range: Reference range dictionary
        
        Returns:
            Tuple of (EvaluationStatus, severity)
            severity is None for normal values
        """
        # Check critical ranges first
        if 'critical_low' in ref_range and value <= ref_range['critical_low']:
            return EvaluationStatus.CRITICAL_LOW, "Severe"
        
        if 'critical_high' in ref_range and value >= ref_range['critical_high']:
            return EvaluationStatus.CRITICAL_HIGH, "Severe"
        
        # Handle multi-category ranges (e.g., glucose, cholesterol)
        if 'normal' in ref_range:
            normal_range = ref_range['normal']
            if 'min' in normal_range and 'max' in normal_range:
                if normal_range['min'] <= value <= normal_range['max']:
                    return EvaluationStatus.NORMAL, None
            elif 'max' in normal_range and value <= normal_range['max']:
                return EvaluationStatus.NORMAL, None
            
            # Check for prediabetes, borderline, etc.
            if 'prediabetes' in ref_range:
                prediabetes = ref_range['prediabetes']
                if prediabetes.get('min', 0) <= value <= prediabetes.get('max', float('inf')):
                    return EvaluationStatus.BORDERLINE_HIGH, "Mild"
            
            if 'diabetes' in ref_range:
                diabetes = ref_range['diabetes']
                if value >= diabetes.get('min', float('inf')):
                    return EvaluationStatus.HIGH, "Moderate"
        
        # Standard min/max range
        if 'min' in ref_range and 'max' in ref_range:
            min_val, max_val = ref_range['min'], ref_range['max']
            
            if min_val <= value <= max_val:
                return EvaluationStatus.NORMAL, None
            elif value < min_val:
                # Determine severity based on how far below normal
                deviation = ((min_val - value) / min_val) * 100
                if deviation > 30:
                    return EvaluationStatus.LOW, "Severe"
                elif deviation > 15:
                    return EvaluationStatus.LOW, "Moderate"
                else:
                    return EvaluationStatus.LOW, "Mild"
            else:  # value > max_val
                # Determine severity based on how far above normal
                deviation = ((value - max_val) / max_val) * 100
                if deviation > 30:
                    return EvaluationStatus.HIGH, "Severe"
                elif deviation > 15:
                    return EvaluationStatus.HIGH, "Moderate"
                else:
                    return EvaluationStatus.HIGH, "Mild"
        
        # Handle ranges with only max (e.g., "desirable: max")
        if 'desirable' in ref_range:
            desirable = ref_range['desirable']
            if 'max' in desirable and value <= desirable['max']:
                return EvaluationStatus.NORMAL, None
        
        if 'optimal' in ref_range:
            optimal = ref_range['optimal']
            if 'max' in optimal and value <= optimal['max']:
                return EvaluationStatus.NORMAL, None
        
        # Default to unknown if unable to classify
        return EvaluationStatus.UNKNOWN, None
    
    def _calculate_deviation(
        self, 
        value: float, 
        ref_range: Dict[str, Any]
    ) -> Optional[float]:
        """
        Calculate percentage deviation from normal range.
        
        Args:
            value: Measured value
            ref_range: Reference range
        
        Returns:
            Percentage deviation (positive = above normal, negative = below)
            None if cannot calculate
        """
        if 'min' in ref_range and 'max' in ref_range:
            min_val, max_val = ref_range['min'], ref_range['max']
            mid_point = (min_val + max_val) / 2
            
            if value < min_val:
                return -((min_val - value) / min_val) * 100
            elif value > max_val:
                return ((value - max_val) / max_val) * 100
            else:
                return 0.0
        
        return None
    
    def _format_reference_range(self, ref_range: Dict[str, Any]) -> str:
        """
        Format reference range for display.
        
        Args:
            ref_range: Reference range dictionary
        
        Returns:
            Human-readable range string
        """
        unit = ref_range.get('unit', '')
        
        if 'min' in ref_range and 'max' in ref_range:
            return f"{ref_range['min']}-{ref_range['max']} {unit}"
        elif 'normal' in ref_range:
            normal = ref_range['normal']
            if 'min' in normal and 'max' in normal:
                return f"{normal['min']}-{normal['max']} {unit}"
            elif 'max' in normal:
                return f"<{normal['max']} {unit}"
        elif 'optimal' in ref_range:
            optimal = ref_range['optimal']
            if 'max' in optimal:
                return f"<{optimal['max']} {unit} (optimal)"
        
        return "Range varies by category"
    
    def get_clinical_significance(self, parameter: str) -> str:
        """
        Get clinical significance for a parameter.
        
        Args:
            parameter: Parameter name
        
        Returns:
            Clinical significance description
        """
        ref_range = self.get_reference_range(parameter)
        if ref_range:
            return ref_range.get(
                'clinical_significance', 
                'Clinical significance not available'
            )
        return 'Parameter not found'


# Convenience function for quick evaluation
def evaluate_lab_value(
    parameter: str,
    value: float,
    sex: Optional[str] = None,
    age: Optional[int] = None
) -> Dict[str, Any]:
    """
    Quick evaluation function without instantiating manager.
    
    Args:
        parameter: Parameter name
        value: Measured value
        sex: Optional sex specification
        age: Optional age
    
    Returns:
        Evaluation result dictionary
    """
    manager = ReferenceRangeManager()
    return manager.evaluate_value(parameter, value, sex, age)
