"""
Model 1: Parameter Interpretation
Classifies individual parameters as high, low, normal, or borderline
"""

from typing import List, Dict, Any
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParameterStatus(Enum):
    """Parameter status classifications"""
    NORMAL = "normal"
    HIGH = "high"
    LOW = "low"
    BORDERLINE_HIGH = "borderline_high"
    BORDERLINE_LOW = "borderline_low"
    CRITICAL_HIGH = "critical_high"
    CRITICAL_LOW = "critical_low"


class ParameterInterpreter:
    """Classify blood parameters against reference ranges"""
    
    # Standard reference ranges (gender-neutral defaults)
    STANDARD_REFERENCE_RANGES = {
        'HEMOGLOBIN': {'min': 12.0, 'max': 17.0, 'unit': 'g/dL', 
                       'male': (13.5, 17.5), 'female': (12.0, 15.5),
                       'critical_low': 7.0, 'critical_high': 20.0},
        'WBC': {'min': 4.0, 'max': 11.0, 'unit': '10^3/μL',
                'critical_low': 2.0, 'critical_high': 30.0},
        'RBC': {'min': 4.2, 'max': 6.1, 'unit': '10^6/μL',
                'male': (4.7, 6.1), 'female': (4.2, 5.4),
                'critical_low': 2.0, 'critical_high': 8.0},
        'PLATELETS': {'min': 150, 'max': 400, 'unit': '10^3/μL',
                      'critical_low': 50, 'critical_high': 1000},
        'GLUCOSE': {'min': 70, 'max': 100, 'unit': 'mg/dL',
                    'critical_low': 50, 'critical_high': 400},
        'CHOLESTEROL': {'min': 0, 'max': 200, 'unit': 'mg/dL'},
        'HDL': {'min': 40, 'max': 999, 'unit': 'mg/dL',
                'male': (40, 999), 'female': (50, 999)},
        'LDL': {'min': 0, 'max': 100, 'unit': 'mg/dL'},
        'TRIGLYCERIDES': {'min': 0, 'max': 150, 'unit': 'mg/dL'},
        'CREATININE': {'min': 0.6, 'max': 1.3, 'unit': 'mg/dL',
                       'male': (0.7, 1.3), 'female': (0.6, 1.1),
                       'critical_low': 0.3, 'critical_high': 10.0},
        'BUN': {'min': 7, 'max': 20, 'unit': 'mg/dL',
                'critical_low': 2, 'critical_high': 80},
        'ALT': {'min': 7, 'max': 56, 'unit': 'U/L',
                'critical_low': 0, 'critical_high': 500},
        'AST': {'min': 10, 'max': 40, 'unit': 'U/L',
                'critical_low': 0, 'critical_high': 500},
        'TSH': {'min': 0.4, 'max': 4.0, 'unit': 'mIU/L',
                'critical_low': 0.01, 'critical_high': 20.0},
        'HBA1C': {'min': 4.0, 'max': 5.6, 'unit': '%',
                  'critical_high': 10.0}
    }
    
    # Borderline threshold (percentage of range)
    BORDERLINE_THRESHOLD = 0.10  # 10% from boundary
    
    def __init__(self, gender: str = None, age: int = None):
        """
        Initialize interpreter
        
        Args:
            gender: Patient gender ('male' or 'female') for gender-specific ranges
            age: Patient age for age-specific adjustments
        """
        self.gender = gender.lower() if gender else None
        self.age = age
        self.interpretations = []
    
    def interpret(self, validated_params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Interpret all parameters
        
        Args:
            validated_params: List of validated parameters
            
        Returns:
            List of parameters with interpretation results
        """
        self.interpretations = []
        
        for param in validated_params:
            interpretation = self._interpret_parameter(param)
            self.interpretations.append(interpretation)
        
        logger.info(f"Interpreted {len(self.interpretations)} parameters")
        return self.interpretations
    
    def _interpret_parameter(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret a single parameter"""
        standard_name = param['standard_name']
        value = param['value']
        
        # Get reference range
        ref_min, ref_max = self._get_reference_range(param)
        
        # Classify the value
        status = self._classify_value(standard_name, value, ref_min, ref_max)
        
        # Calculate deviation percentage
        deviation_pct = self._calculate_deviation(value, ref_min, ref_max)
        
        # Generate interpretation message
        message = self._generate_message(standard_name, value, status, ref_min, ref_max)
        
        # Create interpretation result
        interpretation = {
            **param,  # Include all original parameter data
            'reference_min': ref_min,
            'reference_max': ref_max,
            'status': status.value,
            'deviation_percentage': round(deviation_pct, 1),
            'interpretation_message': message,
            'requires_attention': status in [ParameterStatus.HIGH, ParameterStatus.LOW, 
                                             ParameterStatus.CRITICAL_HIGH, ParameterStatus.CRITICAL_LOW],
            'is_critical': status in [ParameterStatus.CRITICAL_HIGH, ParameterStatus.CRITICAL_LOW]
        }
        
        return interpretation
    
    def _get_reference_range(self, param: Dict[str, Any]) -> tuple:
        """Get appropriate reference range for parameter"""
        standard_name = param['standard_name']
        
        # Use provided reference range if available and valid
        if param.get('reference_min') is not None and param.get('reference_max') is not None:
            return param['reference_min'], param['reference_max']
        
        # Use standard ranges
        if standard_name not in self.STANDARD_REFERENCE_RANGES:
            logger.warning(f"No standard range for {standard_name}")
            return None, None
        
        ref_data = self.STANDARD_REFERENCE_RANGES[standard_name]
        
        # Check for gender-specific ranges
        if self.gender and self.gender in ref_data:
            return ref_data[self.gender]
        
        # Return default range
        return ref_data['min'], ref_data['max']
    
    def _classify_value(self, param_name: str, value: float, ref_min: float, ref_max: float) -> ParameterStatus:
        """Classify parameter value"""
        if ref_min is None or ref_max is None:
            return ParameterStatus.NORMAL  # Cannot classify without ranges
        
        # Check critical ranges
        if param_name in self.STANDARD_REFERENCE_RANGES:
            ref_data = self.STANDARD_REFERENCE_RANGES[param_name]
            if 'critical_low' in ref_data and value <= ref_data['critical_low']:
                return ParameterStatus.CRITICAL_LOW
            if 'critical_high' in ref_data and value >= ref_data['critical_high']:
                return ParameterStatus.CRITICAL_HIGH
        
        # Calculate borderline thresholds
        range_width = ref_max - ref_min
        borderline_range = range_width * self.BORDERLINE_THRESHOLD
        
        # Classify
        if value < ref_min:
            if value >= (ref_min - borderline_range):
                return ParameterStatus.BORDERLINE_LOW
            else:
                return ParameterStatus.LOW
        elif value > ref_max:
            if value <= (ref_max + borderline_range):
                return ParameterStatus.BORDERLINE_HIGH
            else:
                return ParameterStatus.HIGH
        else:
            return ParameterStatus.NORMAL
    
    def _calculate_deviation(self, value: float, ref_min: float, ref_max: float) -> float:
        """Calculate deviation percentage from normal range"""
        if ref_min is None or ref_max is None:
            return 0.0
        
        if value < ref_min:
            # Below range
            return ((ref_min - value) / ref_min) * -100
        elif value > ref_max:
            # Above range
            return ((value - ref_max) / ref_max) * 100
        else:
            # Within range
            return 0.0
    
    def _generate_message(self, param_name: str, value: float, status: ParameterStatus, 
                         ref_min: float, ref_max: float) -> str:
        """Generate human-readable interpretation message"""
        param_display = param_name.replace('_', ' ').title()
        
        if status == ParameterStatus.NORMAL:
            return f"{param_display} is within normal range."
        elif status == ParameterStatus.BORDERLINE_HIGH:
            return f"{param_display} is slightly elevated (borderline high)."
        elif status == ParameterStatus.BORDERLINE_LOW:
            return f"{param_display} is slightly decreased (borderline low)."
        elif status == ParameterStatus.HIGH:
            return f"{param_display} is elevated above normal range."
        elif status == ParameterStatus.LOW:
            return f"{param_display} is below normal range."
        elif status == ParameterStatus.CRITICAL_HIGH:
            return f"⚠️ {param_display} is critically high. Immediate medical attention may be required."
        elif status == ParameterStatus.CRITICAL_LOW:
            return f"⚠️ {param_display} is critically low. Immediate medical attention may be required."
    
    def get_summary(self) -> Dict[str, Any]:
        """Get interpretation summary"""
        summary = {
            'total_parameters': len(self.interpretations),
            'normal': 0,
            'abnormal': 0,
            'critical': 0,
            'borderline': 0,
            'parameters_by_status': {}
        }
        
        for interp in self.interpretations:
            status = interp['status']
            
            if status == 'normal':
                summary['normal'] += 1
            elif status in ['borderline_high', 'borderline_low']:
                summary['borderline'] += 1
            elif status in ['critical_high', 'critical_low']:
                summary['critical'] += 1
            else:
                summary['abnormal'] += 1
            
            if status not in summary['parameters_by_status']:
                summary['parameters_by_status'][status] = []
            summary['parameters_by_status'][status].append(interp['standard_name'])
        
        return summary
    
    def get_attention_required(self) -> List[Dict[str, Any]]:
        """Get parameters that require attention"""
        return [i for i in self.interpretations if i['requires_attention']]