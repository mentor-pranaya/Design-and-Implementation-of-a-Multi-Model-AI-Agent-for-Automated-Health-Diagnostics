import re
from src.config.reference_loader import get_range


def parse_reference_range(reference_range):
   
    if reference_range is None:
        return None, None
    
    
    if isinstance(reference_range, (tuple, list)) and len(reference_range) == 2:
        try:
            return float(reference_range[0]), float(reference_range[1])
        except (ValueError, TypeError):
            return None, None
    
    
    if isinstance(reference_range, dict):
        try:
            lower = reference_range.get("min") or reference_range.get("lower")
            upper = reference_range.get("max") or reference_range.get("upper")
            if lower is not None and upper is not None:
                return float(lower), float(upper)
        except (ValueError, TypeError):
            pass
        return None, None
    
    
    if isinstance(reference_range, str):
        
        reference_range = reference_range.strip()
        
       
        if not reference_range or reference_range.upper() in ["N/A", "NA", "NONE", ""]:
            return None, None
        
        
        patterns = [
            r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)',      # "13.5-17.5" or "13.5 - 17.5"
            r'(\d+\.?\d*)\s+to\s+(\d+\.?\d*)',         # "13.5 to 17.5"
            r'(\d+\.?\d*)\s*,\s*(\d+\.?\d*)',          # "13.5, 17.5"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, reference_range, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1)), float(match.group(2))
                except ValueError:
                    continue
        
        
        numbers = re.findall(r'\d+\.?\d*', reference_range)
        if len(numbers) >= 2:
            try:
                return float(numbers[0]), float(numbers[1])
            except ValueError:
                pass
    
    return None, None


def interpret_value(value, reference_range=None, param_name=None, gender=None, age=None):
    
    if value is None:
        return "UNKNOWN"
    
    
    if not isinstance(value, (int, float)):
        return "N/A"
    
    lower = None
    upper = None
    
    
    if param_name:
        dynamic_range = get_range(param_name, gender=gender, age=age)
        if dynamic_range:
            lower, upper = dynamic_range
    
    
    if lower is None or upper is None:
        parsed_lower, parsed_upper = parse_reference_range(reference_range)
        if parsed_lower is not None and parsed_upper is not None:
            lower, upper = parsed_lower, parsed_upper
    
    
    if lower is None or upper is None:
        return "UNKNOWN"
    
    
    try:
        value = float(value)
        if value < lower:
            return "LOW"
        elif value > upper:
            return "HIGH"
        else:
            return "NORMAL"
    except (ValueError, TypeError):
        return "UNKNOWN"