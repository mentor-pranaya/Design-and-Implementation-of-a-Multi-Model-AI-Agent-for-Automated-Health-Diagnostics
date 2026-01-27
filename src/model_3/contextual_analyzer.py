from src.config.reference_loader import get_range, get_age_group

def get_contextual_range(param_name, age=None, gender=None):
    """
    Get the appropriate reference range based on age and gender
    Returns tuple (min, max) or None
    """
    ref_range = get_range(param_name, gender=gender, age=age)
    return ref_range  # Already returns tuple (min, max)


def interpret_with_context(value, param_name, age=None, gender=None):
   
    result = {
        "status": "UNKNOWN",
        "value_range": None,          
        "contextual_range": None,     
        "context_applied": False,
        "notes": ""
    }
    
    if value is None:
        result["status"] = "NO VALUE"
        return result
    
    # Skip non-numeric values
    if not isinstance(value, (int, float)):
        result["status"] = "N/A"
        result["notes"] = "Non-numeric value"
        return result
    
    # Get contextual range from external file
    contextual_range = get_contextual_range(param_name, age, gender)
    
    if contextual_range:
        min_val, max_val = contextual_range
        
        # BUG 3 FIX: Store as tuple for calculations
        result["value_range"] = (min_val, max_val)
        # String version for display only
        result["contextual_range"] = f"{min_val}-{max_val}"
        result["context_applied"] = True
        
        age_group = get_age_group(age)
        
        if value < min_val:
            result["status"] = "LOW"
            result["notes"] = f"Below range for {age_group}"
            if gender:
                result["notes"] += f" {gender.lower()}"
        elif value > max_val:
            result["status"] = "HIGH"
            result["notes"] = f"Above range for {age_group}"
            if gender:
                result["notes"] += f" {gender.lower()}"
        else:
            result["status"] = "NORMAL"
            result["notes"] = f"Within range for {age_group}"
            if gender:
                result["notes"] += f" {gender.lower()}"
    else:
        result["notes"] = "No contextual adjustment available"
    
    return result


def analyze_with_context(results, age=None, gender=None):
    
    contextual_results = {}
    age_group = get_age_group(age)
    
    context_summary = {
        "age": age,
        "age_group": age_group,
        "gender": gender,
        "parameters_analyzed": 0,
        "parameters_changed": 0,
        "adjustments": []
    }
    
    for param_name, param_data in results.items():
        if param_data is None:
            continue
        
        value = param_data.get("value")
        original_status = param_data.get("status", "UNKNOWN")
        
        # Get contextual interpretation
        context_result = interpret_with_context(value, param_name, age, gender)
        
        # Store detailed results
        contextual_results[param_name] = {
            "value": value,
            "original_status": original_status,
            "contextual_status": context_result["status"] if context_result["context_applied"] else original_status,
            "value_range": context_result["value_range"],           
            "contextual_range": context_result["contextual_range"], 
            "context_applied": context_result["context_applied"],
            "notes": context_result["notes"]
        }
        
        
        if context_result["context_applied"]:
            context_summary["parameters_analyzed"] += 1
            
            new_status = context_result["status"]
            
            # Update the original results dict (BUG 6 FIX)
            param_data["status"] = new_status
            param_data["contextual_range"] = context_result["contextual_range"]
            param_data["value_range"] = context_result["value_range"]
            
            # Track if status changed
            if (new_status != original_status and 
                new_status not in ["UNKNOWN", "NO VALUE", "N/A"] and
                original_status not in ["UNKNOWN", "NO VALUE", "N/A"]):
                
                context_summary["parameters_changed"] += 1
                context_summary["adjustments"].append({
                    "parameter": param_name,
                    "original_status": original_status,
                    "new_status": new_status,
                    "reason": context_result["notes"]
                })
    
    return {
        "summary": context_summary,
        "detailed_results": contextual_results
    }