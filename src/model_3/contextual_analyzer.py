# Gender-specific reference ranges
# Format: { "parameter_name": { "male":  (min, max), "female": (min, max) } }
GENDER_SPECIFIC_RANGES = {
    "Hemoglobin": {
        "male": (13.5, 17.5),
        "female": (12.0, 15.5)
    },
    "RBC": {
        "male": (4.5, 5.5),
        "female": (4.0, 5.0)
    },
    "HCT":  {
        "male": (40.0, 54.0),
        "female": (36.0, 48.0)
    },
    "Creatinine": {
        "male": (0.7, 1.3),
        "female": (0.6, 1.1)
    }
}

# Age-specific adjustments
# Format: { "age_group": { "parameter_name": (min, max) } }
AGE_SPECIFIC_RANGES = {
    "child": {  # 0-12 years
        "Hemoglobin": (11.0, 14.0),
        "RBC": (4.0, 5.0),
        "WBC": (5.0, 13.0),
        "Creatinine": (0.3, 0.7)
    },
    "teenager": {  # 13-17 years
        "Hemoglobin": (12.0, 16.0),
        "RBC": (4.2, 5.4),
        "WBC": (4.5, 11.0),
        "Creatinine": (0.5, 1.0)
    },
    "adult": {  # 18-60 years
        # Uses gender-specific ranges (default)
    },
    "senior": {  # 60+ years
        "Hemoglobin": (11.5, 16.5),
        "RBC": (3.8, 5.2),
        "WBC": (3.5, 10.5),
        "Creatinine": (0.7, 1.4)
    }
}


def get_age_group(age):
    
    if age is None:
        return "adult"  # Default to adult if age not provided
    
    if age < 13:
        return "child"
    elif age < 18:
        return "teenager"
    elif age < 60:
        return "adult"
    else: 
        return "senior"


def get_contextual_range(param_name, age=None, gender=None):
   
    age_group = get_age_group(age)
    
    # Priority 1: Check age-specific ranges for children/teenagers/seniors
    if age_group in ["child", "teenager", "senior"]:
        if age_group in AGE_SPECIFIC_RANGES: 
            if param_name in AGE_SPECIFIC_RANGES[age_group]:
                return AGE_SPECIFIC_RANGES[age_group][param_name]
    
    # Priority 2: Check gender-specific ranges for adults
    if gender and gender. lower() in ["male", "female"]:
        gender_lower = gender.lower()
        if param_name in GENDER_SPECIFIC_RANGES: 
            return GENDER_SPECIFIC_RANGES[param_name][gender_lower]
    
    # Priority 3: Return None (use default range from report)
    return None


def interpret_with_context(value, param_name, age=None, gender=None):
  
    result = {
        "status": "UNKNOWN",
        "contextual_range": None,
        "context_applied": False,
        "notes": ""
    }
    
    if value is None:
        result["status"] = "NO VALUE"
        return result
    
   
    contextual_range = get_contextual_range(param_name, age, gender)
    
    if contextual_range: 
        result["contextual_range"] = f"{contextual_range[0]}-{contextual_range[1]}"
        result["context_applied"] = True
        
        min_val, max_val = contextual_range
        
        if value < min_val: 
            result["status"] = "LOW"
            result["notes"] = f"Below range for {get_age_group(age)}"
            if gender: 
                result["notes"] += f" {gender.lower()}"
        elif value > max_val:
            result["status"] = "HIGH"
            result["notes"] = f"Above range for {get_age_group(age)}"
            if gender: 
                result["notes"] += f" {gender.lower()}"
        else:
            result["status"] = "NORMAL"
            result["notes"] = f"Within range for {get_age_group(age)}"
            if gender:
                result["notes"] += f" {gender.lower()}"
    else:
        result["notes"] = "No contextual adjustment available"
    
    return result


def analyze_with_context(results, age=None, gender=None):
   
    contextual_results = {}
    context_summary = {
        "age":  age,
        "age_group": get_age_group(age),
        "gender": gender,
        "parameters_adjusted": 0,
        "adjustments":  []
    }
    
    for param_name, param_data in results.items():
        if param_data is None:
            continue
        
        value = param_data.get("value")
        original_status = param_data.get("status", "UNKNOWN")
        
        # Get contextual interpretation
        context_result = interpret_with_context(value, param_name, age, gender)
        
        contextual_results[param_name] = {
            "value": value,
            "original_status": original_status,
            "contextual_status": context_result["status"] if context_result["context_applied"] else original_status,
            "contextual_range": context_result["contextual_range"],
            "context_applied": context_result["context_applied"],
            "notes":  context_result["notes"]
        }
        
        # Track if status changed due to context
        if context_result["context_applied"]:
            context_summary["parameters_adjusted"] += 1
            
            if context_result["status"] != original_status and context_result["status"] != "UNKNOWN":
                context_summary["adjustments"].append({
                    "parameter": param_name,
                    "original_status": original_status,
                    "new_status": context_result["status"],
                    "reason": context_result["notes"]
                })
    
    return {
        "summary": context_summary,
        "detailed_results": contextual_results
    }