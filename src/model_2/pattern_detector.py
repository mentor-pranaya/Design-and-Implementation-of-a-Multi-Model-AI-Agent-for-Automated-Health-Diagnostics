import math
from src.config.reference_loader import get_thresholds


def get_value_and_range(param_name, results):
    
    if param_name not in results or results[param_name] is None:
        return None
    
    param_data = results[param_name]
    
    return {
        "value": param_data.get("value"),
        "status": param_data.get("status", "UNKNOWN"),
        "value_range": param_data.get("value_range"),  # Tuple (min, max)
        "contextual_range": param_data.get("contextual_range", "N/A")  # String for display
    }


def calculate_confidence(abnormal_count, available_count, severity_factor=1.0, max_confidence=90):
    
    if available_count == 0:
        return 0
    
    base_confidence = (abnormal_count / available_count) * 100
    adjusted_confidence = base_confidence * severity_factor
    
    return round(min(adjusted_confidence, max_confidence), 1)


def calculate_severity_factor(value, threshold, is_low=True):
  
    if value is None or threshold is None:
        return 1.0
    
    try:
        value = float(value)
        threshold = float(threshold)
    except (ValueError, TypeError):
        return 1.0
    
    if is_low:
        if value >= threshold:
            return 1.0
        deviation = (threshold - value) / threshold if threshold != 0 else 0
    else:
        if value <= threshold:
            return 1.0
        deviation = (value - threshold) / threshold if threshold != 0 else 0
    
    log_factor = math.log1p(deviation * 2)
    return min(1.0 + log_factor * 0.3, 1.5)


def detect_anemia_pattern(results, contextual_results=None, gender=None, age=None):
    
    findings = {
        "pattern": None,
        "confidence": 0,
        "indicators": [],
        "description": "",
        "data_quality": ""
    }
    
   
    hgb_data = get_value_and_range("Hemoglobin", results)
    rbc_data = get_value_and_range("RBC", results)
    hct_data = get_value_and_range("HCT", results)
    
    available_params = sum([
        hgb_data is not None,
        rbc_data is not None,
        hct_data is not None
    ])
    
    if available_params == 0:
        return findings
    
    indicators = []
    severity_factors = []
    
    thresholds = get_thresholds("anemia")
    hgb_severe = thresholds.get("hemoglobin_severe", 8.0)
    
    
    if hgb_data and hgb_data["status"] == "LOW":
        hgb = hgb_data["value"]
        hgb_range = hgb_data["value_range"]  # Tuple (min, max)
        display_range = hgb_data["contextual_range"]
        
        indicators.append(f"Low Hemoglobin: {hgb} g/dl (range: {display_range})")
        
        
        if hgb_range:
            hgb_min = hgb_range[0]
            severity_factors.append(calculate_severity_factor(hgb, hgb_min, is_low=True))
        else:
            severity_factors.append(1.2)
    
    
    if rbc_data and rbc_data["status"] == "LOW":
        rbc = rbc_data["value"]
        rbc_range = rbc_data["value_range"]  # Tuple (min, max) - BUG 2 FIX
        display_range = rbc_data["contextual_range"]
        
        indicators.append(f"Low RBC: {rbc} 10^6/uL (range: {display_range})")
        
        
        if rbc_range:
            rbc_min = rbc_range[0]
            severity_factors.append(calculate_severity_factor(rbc, rbc_min, is_low=True))
        else:
            severity_factors.append(1.2)
    
    
    if hct_data and hct_data["status"] == "LOW":
        hct = hct_data["value"]
        hct_range = hct_data["value_range"]  # Tuple (min, max)
        display_range = hct_data["contextual_range"]
        
        indicators.append(f"Low HCT: {hct}% (range: {display_range})")
        
        
        if hct_range:
            hct_min = hct_range[0]
            severity_factors.append(calculate_severity_factor(hct, hct_min, is_low=True))
        else:
            severity_factors.append(1.2)
    
    
    should_trigger = False
    hgb_value = hgb_data["value"] if hgb_data else None
    
    if available_params == 1:
        
        if hgb_value is not None and hgb_value < hgb_severe:
            should_trigger = True
            findings["description"] = "Severe Anemia (Hb critically low) - Urgent evaluation needed"
    else:
        
        if len(indicators) >= 2:
            should_trigger = True
        elif len(indicators) == 1 and hgb_value is not None and hgb_value < hgb_severe:
            should_trigger = True
    
    if should_trigger and len(indicators) >= 1:
        findings["pattern"] = "Anemia Indicators"
        
        avg_severity = sum(severity_factors) / len(severity_factors) if severity_factors else 1.0
        findings["confidence"] = calculate_confidence(len(indicators), available_params, avg_severity)
        findings["indicators"] = indicators
        findings["data_quality"] = f"{available_params}/3 parameters available"
        
        if not findings["description"]:
            hgb_moderate = thresholds.get("hemoglobin_moderate", 10.0)
            if hgb_value is not None:
                if hgb_value < hgb_severe:
                    findings["description"] = "Severe Anemia - Urgent medical attention recommended"
                elif hgb_value < hgb_moderate:
                    findings["description"] = "Moderate Anemia - Medical consultation recommended"
                else:
                    findings["description"] = "Mild Anemia - Monitor and consider dietary changes"
            else:
                findings["description"] = "Anemia pattern detected - Further evaluation needed"
    
    return findings


def detect_iron_deficiency_pattern(results, contextual_results=None, gender=None, age=None):
  
    findings = {
        "pattern": None,
        "confidence": 0,
        "indicators": [],
        "description": "",
        "data_quality": ""
    }
    
    mcv_data = get_value_and_range("MCV", results)
    mch_data = get_value_and_range("MCH", results)
    mchc_data = get_value_and_range("MCHC", results)
    rdw_cv_data = get_value_and_range("RDW-CV", results)
    rdw_sd_data = get_value_and_range("RDW-SD", results)
    
    available_params = sum([
        mcv_data is not None,
        mch_data is not None,
        mchc_data is not None,
        rdw_cv_data is not None or rdw_sd_data is not None
    ])
    
    if available_params == 0:
        return findings
    
    indicators = []
    severity_factors = []
    
    if mcv_data and mcv_data["status"] == "LOW":
        mcv_range = mcv_data["value_range"]
        display_range = mcv_data["contextual_range"]
        indicators.append(f"Low MCV (Microcytic): {mcv_data['value']} fl (range: {display_range})")
        if mcv_range:
            severity_factors.append(calculate_severity_factor(mcv_data["value"], mcv_range[0], is_low=True))
    
    if mch_data and mch_data["status"] == "LOW":
        mch_range = mch_data["value_range"]
        display_range = mch_data["contextual_range"]
        indicators.append(f"Low MCH (Hypochromic): {mch_data['value']} pg (range: {display_range})")
        if mch_range:
            severity_factors.append(calculate_severity_factor(mch_data["value"], mch_range[0], is_low=True))
    
    if mchc_data and mchc_data["status"] == "LOW":
        mchc_range = mchc_data["value_range"]
        display_range = mchc_data["contextual_range"]
        indicators.append(f"Low MCHC: {mchc_data['value']} g/dl (range: {display_range})")
        if mchc_range:
            severity_factors.append(calculate_severity_factor(mchc_data["value"], mchc_range[0], is_low=True))
    
    if rdw_cv_data and rdw_cv_data["status"] == "HIGH":
        rdw_range = rdw_cv_data["value_range"]
        display_range = rdw_cv_data["contextual_range"]
        indicators.append(f"High RDW-CV (Anisocytosis): {rdw_cv_data['value']}% (range: {display_range})")
        if rdw_range:
            severity_factors.append(calculate_severity_factor(rdw_cv_data["value"], rdw_range[1], is_low=False))
    elif rdw_sd_data and rdw_sd_data["status"] == "HIGH":
        rdw_range = rdw_sd_data["value_range"]
        display_range = rdw_sd_data["contextual_range"]
        indicators.append(f"High RDW-SD (Anisocytosis): {rdw_sd_data['value']} fl (range: {display_range})")
        if rdw_range:
            severity_factors.append(calculate_severity_factor(rdw_sd_data["value"], rdw_range[1], is_low=False))
    
    has_microcytic = any("MCV" in ind for ind in indicators)
    has_high_rdw = any("RDW" in ind for ind in indicators)
    
    if len(indicators) >= 2:
        if has_microcytic and has_high_rdw:
            findings["pattern"] = "Iron Deficiency Anemia Indicators"
            findings["description"] = "Classic iron deficiency pattern (Microcytic + High RDW) - Consider iron studies"
        else:
            findings["pattern"] = "Microcytic Hypochromic Pattern"
            findings["description"] = "Could be iron deficiency or thalassemia - Consider iron studies and Hb electrophoresis"
        
        avg_severity = sum(severity_factors) / len(severity_factors) if severity_factors else 1.0
        findings["confidence"] = calculate_confidence(len(indicators), available_params, avg_severity)
        findings["indicators"] = indicators
        findings["data_quality"] = f"{available_params}/4 parameters available"
    
    return findings


def detect_kidney_pattern(results, contextual_results=None, gender=None, age=None):
   
    findings = {
        "pattern": None,
        "confidence": 0,
        "indicators": [],
        "description": "",
        "data_quality": "",
        "severity": "none"
    }
    
    creat_data = get_value_and_range("Creatinine", results)
    urea_data = get_value_and_range("Urea", results)
    uric_data = get_value_and_range("Uric Acid", results)
    
    available_params = sum([
        creat_data is not None,
        urea_data is not None,
        uric_data is not None
    ])
    
    if available_params == 0:
        return findings
    
    indicators = []
    severity_factors = []
    thresholds = get_thresholds("kidney")
    
    creat_severity = "none"
    if creat_data and creat_data["status"] == "HIGH":
        creat = creat_data["value"]
        creat_range = creat_data["value_range"]
        display_range = creat_data["contextual_range"]
        
        creat_high = thresholds.get("creatinine_high", 2.0)
        creat_elevated = thresholds.get("creatinine_elevated", 1.5)
        
        if creat > creat_high:
            indicators.append(f"Highly elevated Creatinine: {creat} mg/dl (range: {display_range})")
            severity_factors.append(1.5)
            creat_severity = "high"
        elif creat > creat_elevated:
            indicators.append(f"Elevated Creatinine: {creat} mg/dl (range: {display_range})")
            severity_factors.append(1.3)
            creat_severity = "moderate"
        else:
            indicators.append(f"Slightly elevated Creatinine: {creat} mg/dl (range: {display_range})")
            if creat_range:
                severity_factors.append(calculate_severity_factor(creat, creat_range[1], is_low=False))
            else:
                severity_factors.append(1.1)
            creat_severity = "mild"
    
    if urea_data and urea_data["status"] == "HIGH":
        urea = urea_data["value"]
        display_range = urea_data["contextual_range"]
        urea_high = thresholds.get("urea_high", 60.0)
        
        if urea > urea_high:
            indicators.append(f"Highly elevated Urea: {urea} mg/dl (range: {display_range})")
            severity_factors.append(1.4)
        else:
            indicators.append(f"Elevated Urea: {urea} mg/dl (range: {display_range})")
            severity_factors.append(1.2)
    
    if uric_data and uric_data["status"] == "HIGH":
        uric = uric_data["value"]
        display_range = uric_data["contextual_range"]
        uric_high = thresholds.get("uric_acid_high", 9.0)
        
        if uric > uric_high:
            indicators.append(f"Highly elevated Uric Acid: {uric} mg/dl (range: {display_range})")
            severity_factors.append(1.3)
        else:
            indicators.append(f"Elevated Uric Acid: {uric} mg/dl (range: {display_range})")
            severity_factors.append(1.1)
    
    if len(indicators) >= 1:
        findings["pattern"] = "Kidney Function Concern"
        
        avg_severity = sum(severity_factors) / len(severity_factors) if severity_factors else 1.0
        findings["confidence"] = calculate_confidence(len(indicators), available_params, avg_severity)
        findings["indicators"] = indicators
        findings["data_quality"] = f"{available_params}/3 parameters available"
        
        if len(indicators) >= 2 or creat_severity == "high":
            findings["severity"] = "high"
            findings["description"] = "Multiple kidney markers elevated - Medical consultation strongly recommended"
        elif creat_severity == "moderate":
            findings["severity"] = "moderate"
            findings["description"] = "Kidney markers moderately elevated - Schedule follow-up with doctor"
        else:
            findings["severity"] = "mild"
            findings["description"] = "Minor kidney marker elevation - Monitor and retest in 4-6 weeks"
    
    return findings


def detect_infection_pattern(results, contextual_results=None, gender=None, age=None):
   
    findings = {
        "pattern": None,
        "confidence": 0,
        "indicators": [],
        "description": "",
        "data_quality": ""
    }
    
    wbc_data = get_value_and_range("WBC", results)
    
    if not wbc_data:
        return findings
    
    wbc = wbc_data["value"]
    wbc_status = wbc_data["status"]
    wbc_range = wbc_data["value_range"]  # Tuple (min, max) - BUG 5 FIX
    display_range = wbc_data["contextual_range"]
    
    if wbc is None:
        return findings
    
    if wbc_range:
        wbc_min, wbc_max = wbc_range
    else:
        wbc_min, wbc_max = 4.5, 11.0  # Fallback only if no range
    
    thresholds = get_thresholds("infection")
    wbc_very_high = thresholds.get("wbc_high", 15.0)
    
    if wbc_status == "HIGH":
        
        deviation = (wbc - wbc_max) / wbc_max if wbc_max != 0 else 0
        
        log_factor = math.log1p(deviation)
        confidence = min(50 + (log_factor * 25), 85)
        
        if wbc > wbc_very_high:
            findings["pattern"] = "Significant Infection/Inflammation"
            findings["description"] = "Significantly elevated WBC suggests active infection or inflammation"
        else:
            findings["pattern"] = "Possible Infection/Inflammation"
            findings["description"] = "Elevated WBC may indicate infection or inflammation"
        
        findings["confidence"] = round(confidence, 1)
        findings["indicators"] = [f"Elevated WBC: {wbc} 10^3/uL (range: {display_range})"]
        
    elif wbc_status == "LOW":
       
        deviation = (wbc_min - wbc) / wbc_min if wbc_min != 0 else 0
        
        log_factor = math.log1p(deviation)
        confidence = min(55 + (log_factor * 25), 85)
        
        findings["pattern"] = "Low WBC (Leukopenia)"
        findings["indicators"] = [f"Low WBC: {wbc} 10^3/uL (range: {display_range})"]
        findings["description"] = "Low WBC may indicate immune system issues, viral infection, or bone marrow problems"
        findings["confidence"] = round(confidence, 1)
    
    if findings["pattern"]:
        findings["data_quality"] = "1/1 parameters available"
    
    return findings


def detect_all_patterns(results, contextual_results=None, gender=None, age=None):
  
    patterns = []
    
    anemia = detect_anemia_pattern(results, contextual_results, gender, age)
    if anemia["pattern"]:
        patterns.append(anemia)
    
    iron_def = detect_iron_deficiency_pattern(results, contextual_results, gender, age)
    if iron_def["pattern"]:
        patterns.append(iron_def)
    
    kidney = detect_kidney_pattern(results, contextual_results, gender, age)
    if kidney["pattern"]:
        patterns.append(kidney)
    
    infection = detect_infection_pattern(results, contextual_results, gender, age)
    if infection["pattern"]:
        patterns.append(infection)
    
    return patterns