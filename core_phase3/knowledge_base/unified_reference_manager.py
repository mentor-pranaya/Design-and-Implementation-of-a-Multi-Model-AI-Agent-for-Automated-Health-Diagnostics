"""
Unified Reference Manager - Intelligent Multi-Source Reference Ranges

This module provides a unified interface for reference ranges from multiple sources:
1. Lab-provided ranges (from blood report) - HIGHEST PRIORITY
2. NHANES population data (age/sex-specific) - POPULATION-BASED
3. ABIM clinical guidelines - CLINICAL STANDARD

NO HARDCODING - All ranges loaded from data sources.

Design Philosophy:
- Intelligent fallback hierarchy
- Age/sex-specific ranges when available
- Source attribution and confidence scoring
- Transparent decision-making
- Clinically defensible
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime


class ReferenceSource(Enum):
    """Source of reference range."""
    LAB_PROVIDED = "lab_provided"
    NHANES_POPULATION = "nhanes_population"
    ABIM_GUIDELINE = "abim_guideline"
    FALLBACK = "fallback"


class ConfidenceLevel(Enum):
    """Confidence in reference range."""
    VERY_HIGH = "very_high"  # Lab-provided, patient-specific
    HIGH = "high"  # NHANES age/sex-specific
    MEDIUM = "medium"  # NHANES overall or ABIM
    LOW = "low"  # Fallback/generic


class UnifiedReferenceManager:
    """
    Unified reference manager with intelligent multi-source fallback.
    
    Priority Hierarchy:
    1. Lab-provided range (if available from report)
    2. NHANES age/sex-specific percentiles
    3. NHANES overall percentiles
    4. ABIM clinical guidelines
    5. Fallback (if absolutely necessary)
    
    All ranges are data-driven with NO hardcoding.
    """
    
    def __init__(
        self,
        nhanes_path: str = None,
        abim_path: str = None
    ):
        """
        Initialize unified reference manager.
        
        Args:
            nhanes_path: Path to NHANES reference ranges JSON
            abim_path: Path to ABIM reference ranges JSON
        """
        script_dir = Path(__file__).parent
        
        # Load NHANES ranges
        if nhanes_path is None:
            nhanes_path = script_dir / "nhanes_reference_ranges.json"
        self.nhanes_path = Path(nhanes_path)
        self.nhanes_ranges = self._load_nhanes_ranges()
        
        # Load ABIM ranges
        if abim_path is None:
            abim_path = script_dir / "reference_ranges.json"
        self.abim_path = Path(abim_path)
        self.abim_ranges = self._load_abim_ranges()
        
        print("="*70)
        print("UNIFIED REFERENCE MANAGER")
        print("="*70)
        print(f"✓ NHANES ranges loaded: {len([k for k in self.nhanes_ranges.keys() if not k.startswith('_')])} parameters")
        print(f"✓ ABIM ranges loaded: {len([k for k in self.abim_ranges.keys() if not k.startswith('_')])} parameters")
        print(f"✓ Total unique parameters: {len(self._get_all_parameters())}")
        print("="*70)
    
    def _load_nhanes_ranges(self) -> Dict:
        """Load NHANES reference ranges."""
        if not self.nhanes_path.exists():
            print(f"⚠ NHANES ranges not found: {self.nhanes_path}")
            print("  Run: python core_phase3/knowledge_base/nhanes_processor.py")
            return {}
        
        with open(self.nhanes_path, 'r') as f:
            return json.load(f)
    
    def _load_abim_ranges(self) -> Dict:
        """Load ABIM reference ranges."""
        if not self.abim_path.exists():
            print(f"⚠ ABIM ranges not found: {self.abim_path}")
            return {}
        
        with open(self.abim_path, 'r') as f:
            data = json.load(f)
            # Remove metadata
            if '_metadata' in data:
                data.pop('_metadata')
            return data
    
    def get_reference_range(
        self,
        parameter: str,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        lab_provided_range: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Get best available reference range for parameter.
        
        Intelligent fallback hierarchy:
        1. Lab-provided (if available)
        2. NHANES age/sex-specific
        3. NHANES sex-specific
        4. NHANES overall
        5. ABIM guideline
        
        Args:
            parameter: Parameter name
            age: Patient age (optional)
            sex: Patient sex ("male" or "female", optional)
            lab_provided_range: Lab-provided range from report
        
        Returns:
            Dictionary with reference range and metadata
        """
        # Priority 1: Lab-provided range
        if lab_provided_range and self._is_valid_range(lab_provided_range):
            return {
                'parameter': parameter,
                'min': lab_provided_range['min'],
                'max': lab_provided_range['max'],
                'unit': lab_provided_range.get('unit', 'N/A'),
                'source': ReferenceSource.LAB_PROVIDED.value,
                'confidence': ConfidenceLevel.VERY_HIGH.value,
                'source_detail': 'Laboratory-specific reference range',
                'age_specific': False,
                'sex_specific': False
            }
        
        # Priority 2-4: NHANES ranges (age/sex-specific → sex-specific → overall)
        if parameter in self.nhanes_ranges:
            nhanes_range = self._get_nhanes_range(parameter, age, sex)
            if nhanes_range:
                return nhanes_range
        
        # Priority 5: ABIM guideline
        if parameter in self.abim_ranges:
            abim_range = self._get_abim_range(parameter, sex)
            if abim_range:
                return abim_range
        
        # No range found
        return {
            'parameter': parameter,
            'source': ReferenceSource.FALLBACK.value,
            'confidence': ConfidenceLevel.LOW.value,
            'error': f'No reference range available for {parameter}',
            'available': False
        }
    
    def _get_nhanes_range(
        self,
        parameter: str,
        age: Optional[int],
        sex: Optional[str]
    ) -> Optional[Dict]:
        """Get NHANES range with age/sex specificity."""
        nhanes_data = self.nhanes_ranges[parameter]
        
        # Try age/sex-specific first
        if age and sex:
            age_group = self._get_age_group(age)
            if age_group:
                key = f"{sex.lower()}_{age_group}"
                if key in nhanes_data.get('by_age_sex', {}):
                    age_sex_data = nhanes_data['by_age_sex'][key]
                    return {
                        'parameter': parameter,
                        'min': age_sex_data['reference_range']['min'],
                        'max': age_sex_data['reference_range']['max'],
                        'unit': nhanes_data.get('unit', 'N/A'),
                        'source': ReferenceSource.NHANES_POPULATION.value,
                        'confidence': ConfidenceLevel.HIGH.value,
                        'source_detail': f'NHANES {sex} {age_group} years (n={age_sex_data["n"]})',
                        'age_specific': True,
                        'sex_specific': True,
                        'percentiles': {
                            'p5': age_sex_data['p5'],
                            'p25': age_sex_data['p25'],
                            'p50': age_sex_data['median'],
                            'p75': age_sex_data['p75'],
                            'p95': age_sex_data['p95']
                        }
                    }
        
        # Try sex-specific
        if sex and sex.lower() in nhanes_data.get('by_sex', {}):
            sex_data = nhanes_data['by_sex'][sex.lower()]
            return {
                'parameter': parameter,
                'min': sex_data['reference_range']['min'],
                'max': sex_data['reference_range']['max'],
                'unit': nhanes_data.get('unit', 'N/A'),
                'source': ReferenceSource.NHANES_POPULATION.value,
                'confidence': ConfidenceLevel.HIGH.value,
                'source_detail': f'NHANES {sex} population (n={sex_data["n"]})',
                'age_specific': False,
                'sex_specific': True,
                'percentiles': {
                    'p5': sex_data['p5'],
                    'p25': sex_data['p25'],
                    'p50': sex_data['median'],
                    'p75': sex_data['p75'],
                    'p95': sex_data['p95']
                }
            }
        
        # Use overall NHANES
        if 'overall' in nhanes_data:
            overall_data = nhanes_data['overall']
            return {
                'parameter': parameter,
                'min': overall_data['reference_range']['min'],
                'max': overall_data['reference_range']['max'],
                'unit': nhanes_data.get('unit', 'N/A'),
                'source': ReferenceSource.NHANES_POPULATION.value,
                'confidence': ConfidenceLevel.MEDIUM.value,
                'source_detail': f'NHANES overall population (n={overall_data["n"]})',
                'age_specific': False,
                'sex_specific': False,
                'percentiles': {
                    'p5': overall_data['p5'],
                    'p25': overall_data['p25'],
                    'p50': overall_data['median'],
                    'p75': overall_data['p75'],
                    'p95': overall_data['p95']
                }
            }
        
        return None
    
    def _get_abim_range(self, parameter: str, sex: Optional[str]) -> Optional[Dict]:
        """Get ABIM guideline range."""
        abim_data = self.abim_ranges[parameter]
        
        # Try sex-specific
        if sex and sex.lower() in ['male', 'female']:
            if sex.lower() in abim_data:
                sex_data = abim_data[sex.lower()]
                return {
                    'parameter': parameter,
                    'min': sex_data['min'],
                    'max': sex_data['max'],
                    'unit': abim_data.get('unit', 'N/A'),
                    'source': ReferenceSource.ABIM_GUIDELINE.value,
                    'confidence': ConfidenceLevel.MEDIUM.value,
                    'source_detail': f'ABIM clinical guideline ({sex})',
                    'age_specific': False,
                    'sex_specific': True,
                    'clinical_significance': abim_data.get('clinical_significance', '')
                }
        
        # Use overall ABIM
        if 'min' in abim_data and 'max' in abim_data:
            return {
                'parameter': parameter,
                'min': abim_data['min'],
                'max': abim_data['max'],
                'unit': abim_data.get('unit', 'N/A'),
                'source': ReferenceSource.ABIM_GUIDELINE.value,
                'confidence': ConfidenceLevel.MEDIUM.value,
                'source_detail': 'ABIM clinical guideline',
                'age_specific': False,
                'sex_specific': False,
                'clinical_significance': abim_data.get('clinical_significance', '')
            }
        
        return None
    
    def _get_age_group(self, age: int) -> Optional[str]:
        """Get age group label for age."""
        age_groups = [
            (18, 29, '18-29'),
            (30, 39, '30-39'),
            (40, 49, '40-49'),
            (50, 59, '50-59'),
            (60, 69, '60-69'),
            (70, 120, '70+')
        ]
        
        for min_age, max_age, label in age_groups:
            if min_age <= age <= max_age:
                return label
        
        return None
    
    def _is_valid_range(self, range_dict: Dict) -> bool:
        """Check if range dictionary is valid."""
        return (
            'min' in range_dict and
            'max' in range_dict and
            range_dict['min'] is not None and
            range_dict['max'] is not None and
            range_dict['min'] < range_dict['max']
        )
    
    def _get_all_parameters(self) -> set:
        """Get set of all available parameters."""
        params = set()
        params.update([k for k in self.nhanes_ranges.keys() if not k.startswith('_')])
        params.update([k for k in self.abim_ranges.keys() if not k.startswith('_')])
        return params
    
    def evaluate_value(
        self,
        parameter: str,
        value: float,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        lab_provided_range: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a laboratory value against best available reference range.
        
        Args:
            parameter: Parameter name
            value: Measured value
            age: Patient age
            sex: Patient sex
            lab_provided_range: Lab-provided range
        
        Returns:
            Evaluation result with classification and metadata
        """
        # Get reference range
        ref_range = self.get_reference_range(parameter, age, sex, lab_provided_range)
        
        if not ref_range.get('available', True):
            return {
                'parameter': parameter,
                'value': value,
                'status': 'Unknown',
                'message': ref_range.get('error', 'No reference range available'),
                'reference_available': False
            }
        
        # Classify value
        min_val = ref_range['min']
        max_val = ref_range['max']
        
        if value < min_val:
            deviation = ((min_val - value) / min_val) * 100
            if deviation > 50:
                status, severity = 'Low', 'Severe'
            elif deviation > 25:
                status, severity = 'Low', 'Moderate'
            else:
                status, severity = 'Low', 'Mild'
        elif value > max_val:
            deviation = ((value - max_val) / max_val) * 100
            if deviation > 50:
                status, severity = 'High', 'Severe'
            elif deviation > 25:
                status, severity = 'High', 'Moderate'
            else:
                status, severity = 'High', 'Mild'
        else:
            status, severity = 'Normal', None
            deviation = 0.0
        
        return {
            'parameter': parameter,
            'value': value,
            'unit': ref_range['unit'],
            'status': status,
            'severity': severity,
            'reference_range': f"{min_val:.2f}-{max_val:.2f}",
            'deviation_percent': deviation if status != 'Normal' else 0.0,
            'source': ref_range['source'],
            'confidence': ref_range['confidence'],
            'source_detail': ref_range['source_detail'],
            'age_specific': ref_range.get('age_specific', False),
            'sex_specific': ref_range.get('sex_specific', False),
            'percentiles': ref_range.get('percentiles'),
            'clinical_significance': ref_range.get('clinical_significance'),
            'reference_available': True
        }
    
    def get_source_summary(self) -> Dict:
        """Get summary of available sources."""
        return {
            'nhanes': {
                'available': len(self.nhanes_ranges) > 0,
                'parameters': len([k for k in self.nhanes_ranges.keys() if not k.startswith('_')]),
                'sample_size': self.nhanes_ranges.get('_metadata', {}).get('sample_size', 0)
            },
            'abim': {
                'available': len(self.abim_ranges) > 0,
                'parameters': len([k for k in self.abim_ranges.keys() if not k.startswith('_')])
            },
            'total_parameters': len(self._get_all_parameters())
        }


if __name__ == "__main__":
    # Test unified reference manager
    print("\n🔬 Testing Unified Reference Manager\n")
    
    manager = UnifiedReferenceManager()
    
    # Test case 1: Age/sex-specific NHANES
    print("\n" + "="*70)
    print("Test 1: Hemoglobin for 55-year-old male")
    print("="*70)
    result = manager.evaluate_value('Hemoglobin', 13.5, age=55, sex='male')
    print(json.dumps(result, indent=2))
    
    # Test case 2: Lab-provided range (highest priority)
    print("\n" + "="*70)
    print("Test 2: Glucose with lab-provided range")
    print("="*70)
    lab_range = {'min': 70, 'max': 100, 'unit': 'mg/dL'}
    result = manager.evaluate_value('Glucose', 95, lab_provided_range=lab_range)
    print(json.dumps(result, indent=2))
    
    # Test case 3: Source summary
    print("\n" + "="*70)
    print("Source Summary")
    print("="*70)
    summary = manager.get_source_summary()
    print(json.dumps(summary, indent=2))
