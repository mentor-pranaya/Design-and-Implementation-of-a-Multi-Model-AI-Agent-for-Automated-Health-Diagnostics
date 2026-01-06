def interpret_value(value, reference_range):
    if value is None or reference_range is None:
        return "UNKNOWN"
    
    try: 
        lower, upper = reference_range.split("-")
        lower = float(lower.strip())
        upper = float(upper.strip())
        
        if value <lower :
            return "LOW"
        elif value > upper:
            return "HIGH"
        else: 
            return "NORMAL"
    except Exception:
        return "UNKNOWN"