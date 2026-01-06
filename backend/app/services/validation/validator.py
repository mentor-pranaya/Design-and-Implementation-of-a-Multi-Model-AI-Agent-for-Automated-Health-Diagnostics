"""
Data validation and standardization module
"""

import logging
from typing import Dict, List, Any, Optional
from app.services.reference_ranges import reference_range_service

logger = logging.getLogger(__name__)

# Unit conversion mappings
UNIT_CONVERSIONS = {
    "hemoglobin": {
        "g/L": lambda x: x / 10,  # to g/dL
        "mmol/L": lambda x: x * 1.611,  # to g/dL
    },
    "glucose": {
        "mmol/L": lambda x: x * 18.018,  # to mg/dL
        "g/L": lambda x: x * 100,  # to mg/dL
    },
    "cholesterol": {
        "mmol/L": lambda x: x * 38.67,  # to mg/dL
    },
    "creatinine": {
        "μmol/L": lambda x: x / 88.4,  # to mg/dL
        "umol/L": lambda x: x / 88.4,  # to mg/dL
    },
}

class DataValidator:
    """Validate and standardize extracted blood parameters"""
    
    def __init__(self):
        self.ref_service = reference_range_service
    
    async def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and standardize extracted parameters
        Returns: Dict with validated parameters
        """
        parameters = extracted_data.get("parameters", [])
        
        validated_params = []
        validation_issues = []
        
        for param in parameters:
            result = await self._validate_parameter(param)
            
            if result["is_valid"]:
                validated_params.append(result["parameter"])
            else:
                validation_issues.append({
                    "parameter": param["name"],
                    "issue": result["reason"]
                })
        
        return {
            "validated_parameters": validated_params,
            "validation_issues": validation_issues,
            "total_validated": len(validated_params),
            "total_invalid": len(validation_issues)
        }
    
    async def _validate_parameter(self, param: Dict) -> Dict[str, Any]:
        """Validate a single parameter"""
        name = param.get("name", "").strip()
        value = param.get("value")
        unit = param.get("unit", "").strip()
        
        # Check if parameter is recognized
        normalized_name = self.ref_service.normalize_parameter_name(name)
        
        if not normalized_name:
            return {
                "is_valid": False,
                "reason": f"Unknown parameter: {name}"
            }
        
        # Check value is numeric
        if value is None or not isinstance(value, (int, float)):
            return {
                "is_valid": False,
                "reason": f"Invalid value for {name}: {value}"
            }
        
        # Get expected unit
        ref_range = self.ref_service.get_reference_range(normalized_name)
        expected_unit = ref_range["unit"] if ref_range else unit
        
        # Convert unit if necessary
        standardized_value = value
        if unit and unit != expected_unit:
            standardized_value = self._convert_unit(normalized_name, value, unit, expected_unit)
            
            if standardized_value is None:
                logger.warning(f"Could not convert {name} from {unit} to {expected_unit}")
                standardized_value = value  # Keep original
        
        # Plausibility check (extreme values)
        if not self._is_plausible_value(normalized_name, standardized_value):
            return {
                "is_valid": False,
                "reason": f"Implausible value for {name}: {standardized_value}"
            }
        
        # Build validated parameter
        validated_param = {
            "name": normalized_name,
            "value": round(standardized_value, 2),
            "unit": expected_unit,
            "original_name": name,
            "original_value": value,
            "original_unit": unit,
            "confidence": param.get("confidence", 1.0)
        }
        
        # Add reference range if available
        if ref_range:
            validated_param["reference_min"] = ref_range.get("normal_min")
            validated_param["reference_max"] = ref_range.get("normal_max")
        
        return {
            "is_valid": True,
            "parameter": validated_param
        }
    
    def _convert_unit(
        self, 
        parameter: str, 
        value: float, 
        from_unit: str, 
        to_unit: str
    ) -> Optional[float]:
        """Convert value from one unit to another"""
        
        if parameter in UNIT_CONVERSIONS:
            conversions = UNIT_CONVERSIONS[parameter]
            
            if from_unit in conversions:
                return conversions[from_unit](value)
        
        # No conversion available
        return None
    
    def _is_plausible_value(self, parameter: str, value: float) -> bool:
        """Check if value is within plausible range"""
        
        # Extreme bounds (beyond which values are likely errors)
        plausibility_bounds = {
            "hemoglobin": (0, 30),
            "glucose": (10, 1000),
            "creatinine": (0, 20),
            "wbc": (0, 100000),
            "platelets": (0, 2000000),
            "cholesterol": (50, 600),
            "hdl": (10, 200),
            "ldl": (10, 500),
            "triglycerides": (10, 5000),
        }
        
        if parameter in plausibility_bounds:
            min_val, max_val = plausibility_bounds[parameter]
            return min_val <= value <= max_val
        
        # For unknown parameters, accept positive values
        return value >= 0

# Global instance
data_validator = DataValidator()
