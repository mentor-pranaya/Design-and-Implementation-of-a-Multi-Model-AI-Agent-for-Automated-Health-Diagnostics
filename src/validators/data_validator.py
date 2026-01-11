"""
Data Validation & Standardization Module
Cleans, validates, and standardizes extracted blood parameters
"""

from typing import List, Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validate and standardize blood test parameters"""
    
    # Plausibility ranges (wider than reference ranges to catch data entry errors)
    PLAUSIBILITY_RANGES = {
        'HEMOGLOBIN': {'min': 3.0, 'max': 25.0, 'unit': 'g/dL'},
        'WBC': {'min': 0.5, 'max': 50.0, 'unit': '10^3/μL'},
        'RBC': {'min': 1.0, 'max': 10.0, 'unit': '10^6/μL'},
        'PLATELETS': {'min': 10, 'max': 1000, 'unit': '10^3/μL'},
        'GLUCOSE': {'min': 30, 'max': 600, 'unit': 'mg/dL'},
        'CHOLESTEROL': {'min': 50, 'max': 500, 'unit': 'mg/dL'},
        'HDL': {'min': 10, 'max': 150, 'unit': 'mg/dL'},
        'LDL': {'min': 10, 'max': 300, 'unit': 'mg/dL'},
        'TRIGLYCERIDES': {'min': 20, 'max': 1000, 'unit': 'mg/dL'},
        'CREATININE': {'min': 0.1, 'max': 15.0, 'unit': 'mg/dL'},
        'BUN': {'min': 2, 'max': 100, 'unit': 'mg/dL'},
        'ALT': {'min': 1, 'max': 500, 'unit': 'U/L'},
        'AST': {'min': 1, 'max': 500, 'unit': 'U/L'},
        'TSH': {'min': 0.01, 'max': 50.0, 'unit': 'mIU/L'},
        'HBA1C': {'min': 3.0, 'max': 20.0, 'unit': '%'}
    }
    
    # Unit conversion factors (all convert to standard units)
    UNIT_CONVERSIONS = {
        'GLUCOSE': {
            'mmol/L': 18.0,  # multiply by this to get mg/dL
        },
        'CHOLESTEROL': {
            'mmol/L': 38.67,
        },
        'HDL': {
            'mmol/L': 38.67,
        },
        'LDL': {
            'mmol/L': 38.67,
        },
        'TRIGLYCERIDES': {
            'mmol/L': 88.57,
        }
    }
    
    def __init__(self):
        self.validation_results = {
            'total_parameters': 0,
            'valid_parameters': 0,
            'invalid_parameters': 0,
            'converted_parameters': 0,
            'issues': []
        }
    
    def validate_and_standardize(self, parameters: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Validate and standardize extracted parameters
        
        Args:
            parameters: List of extracted parameters
            
        Returns:
            Tuple of (validated_parameters, validation_report)
        """
        self.validation_results['total_parameters'] = len(parameters)
        validated_params = []
        
        for param in parameters:
            try:
                validated_param = self._validate_parameter(param)
                if validated_param:
                    validated_params.append(validated_param)
                    self.validation_results['valid_parameters'] += 1
                else:
                    self.validation_results['invalid_parameters'] += 1
            except Exception as e:
                logger.error(f"Error validating parameter {param.get('standard_name')}: {e}")
                self.validation_results['invalid_parameters'] += 1
                self.validation_results['issues'].append({
                    'parameter': param.get('standard_name', 'Unknown'),
                    'issue': str(e)
                })
        
        logger.info(f"Validation complete: {self.validation_results['valid_parameters']}/{self.validation_results['total_parameters']} valid")
        
        return validated_params, self.validation_results
    
    def _validate_parameter(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single parameter"""
        standard_name = param.get('standard_name')
        value = param.get('value')
        unit = param.get('standard_unit')
        
        # Check if value exists
        if value is None:
            self.validation_results['issues'].append({
                'parameter': standard_name,
                'issue': 'Missing value'
            })
            return None
        
        # Convert value if needed
        converted_value, converted_unit = self._convert_unit(standard_name, value, unit)
        if converted_value != value:
            self.validation_results['converted_parameters'] += 1
            logger.info(f"Converted {standard_name}: {value} {unit} → {converted_value} {converted_unit}")
        
        # Check plausibility
        if standard_name in self.PLAUSIBILITY_RANGES:
            plausibility = self.PLAUSIBILITY_RANGES[standard_name]
            if not (plausibility['min'] <= converted_value <= plausibility['max']):
                self.validation_results['issues'].append({
                    'parameter': standard_name,
                    'issue': f'Value {converted_value} outside plausible range [{plausibility["min"]}, {plausibility["max"]}]',
                    'severity': 'warning'
                })
                # Still include it but flag it
        
        # Validate reference ranges if present
        ref_min = param.get('reference_min')
        ref_max = param.get('reference_max')
        
        if ref_min is not None and ref_max is not None:
            if ref_min >= ref_max:
                self.validation_results['issues'].append({
                    'parameter': standard_name,
                    'issue': f'Invalid reference range: min ({ref_min}) >= max ({ref_max})',
                    'severity': 'error'
                })
                # Use standard ranges instead
                ref_min, ref_max = None, None
        
        # Create validated parameter
        validated_param = {
            'original_name': param.get('original_name'),
            'standard_name': standard_name,
            'value': round(converted_value, 2),
            'unit': converted_unit,
            'reference_min': ref_min,
            'reference_max': ref_max,
            'extraction_confidence': param.get('extraction_confidence', 1.0),
            'is_valid': True,
            'validation_notes': []
        }
        
        # Add completeness check
        if ref_min is None or ref_max is None:
            validated_param['validation_notes'].append('Missing reference range')
        
        return validated_param
    
    def _convert_unit(self, param_name: str, value: float, unit: str) -> Tuple[float, str]:
        """Convert value to standard unit if needed"""
        if param_name not in self.UNIT_CONVERSIONS:
            return value, unit
        
        conversions = self.UNIT_CONVERSIONS[param_name]
        
        if unit in conversions:
            conversion_factor = conversions[unit]
            converted_value = value * conversion_factor
            standard_unit = self.PLAUSIBILITY_RANGES[param_name]['unit']
            return converted_value, standard_unit
        
        return value, unit
    
    def get_validation_summary(self) -> str:
        """Get human-readable validation summary"""
        summary = f"""
Validation Summary:
------------------
Total Parameters: {self.validation_results['total_parameters']}
Valid Parameters: {self.validation_results['valid_parameters']}
Invalid Parameters: {self.validation_results['invalid_parameters']}
Converted Parameters: {self.validation_results['converted_parameters']}

Issues Found: {len(self.validation_results['issues'])}
"""
        if self.validation_results['issues']:
            summary += "\nIssue Details:\n"
            for i, issue in enumerate(self.validation_results['issues'], 1):
                summary += f"  {i}. {issue['parameter']}: {issue['issue']}\n"
        
        return summary
    
    def check_completeness(self, validated_params: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check data completeness"""
        common_params = {'HEMOGLOBIN', 'WBC', 'GLUCOSE', 'CHOLESTEROL'}
        present_params = {p['standard_name'] for p in validated_params}
        
        completeness = {
            'total_expected': len(common_params),
            'present': len(common_params & present_params),
            'missing': list(common_params - present_params),
            'completeness_ratio': len(common_params & present_params) / len(common_params)
        }
        
        return completeness