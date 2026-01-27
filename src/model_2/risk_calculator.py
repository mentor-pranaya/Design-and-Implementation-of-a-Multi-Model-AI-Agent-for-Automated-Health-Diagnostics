import math
from src.config.reference_loader import get_thresholds


def get_value_and_range(param_name, results):
    
    if param_name not in results or results[param_name] is None:
        return None
    
    param_data = results[param_name]
    
    return {
        "value": param_data.get("value"),
        "status": param_data.get("status", "UNKNOWN"),
        "value_range": param_data.get("value_range"),
        "contextual_range": param_data.get("contextual_range", "N/A")
    }


def calculate_anemia_risk(results, contextual_results=None, gender=None, age=None):
    
    risk_score = 0
    risk_factors = []
    
    hgb_data = get_value_and_range("Hemoglobin", results)
    rbc_data = get_value_and_range("RBC", results)
    hct_data = get_value_and_range("HCT", results)
    
    thresholds = get_thresholds("anemia")
    
    # Risk based on Hemoglobin
    if hgb_data and hgb_data["status"] == "LOW":
        hgb = hgb_data["value"]
        hgb_range = hgb_data["value_range"]  # Tuple
        display_range = hgb_data["contextual_range"]
        
        hgb_severe = thresholds.get("hemoglobin_severe", 8.0)
        hgb_moderate = thresholds.get("hemoglobin_moderate", 10.0)
        
        if hgb < hgb_severe:
            risk_score += 50
            risk_factors.append(f"Severely low Hemoglobin: {hgb} g/dl (+50)")
        elif hgb < hgb_moderate:
            risk_score += 30
            risk_factors.append(f"Moderately low Hemoglobin: {hgb} g/dl (+30)")
        else:
            risk_score += 15
            risk_factors.append(f"Low Hemoglobin: {hgb} g/dl (range: {display_range}) (+15)")
    
    # Risk based on RBC - BUG 2 FIX: Use RBC's own range
    if rbc_data and rbc_data["status"] == "LOW":
        rbc = rbc_data["value"]
        rbc_range = rbc_data["value_range"]  # BUG 2 FIX: Use RBC range, not Hgb
        display_range = rbc_data["contextual_range"]
        
        # BUG 4 FIX: Use contextual min from tuple
        if rbc_range:
            rbc_min = rbc_range[0]
            rbc_critical = rbc_min - 0.5
        else:
            rbc_min = 4.0
            rbc_critical = 3.5
        
        if rbc < rbc_critical:
            risk_score += 25
            risk_factors.append(f"Very low RBC: {rbc} 10^6/uL (+25)")
        else:
            risk_score += 10
            risk_factors.append(f"Low RBC: {rbc} 10^6/uL (range: {display_range}) (+10)")
    
    # Risk based on HCT
    if hct_data and hct_data["status"] == "LOW":
        hct = hct_data["value"]
        hct_range = hct_data["value_range"]  # Tuple
        display_range = hct_data["contextual_range"]
        
        # BUG 4 FIX: Use contextual min from tuple
        if hct_range:
            hct_min = hct_range[0]
            hct_critical = hct_min - 5
        else:
            hct_min = 36.0
            hct_critical = 31.0
        
        if hct < hct_critical:
            risk_score += 25
            risk_factors.append(f"Very low HCT: {hct}% (+25)")
        else:
            risk_score += 10
            risk_factors.append(f"Low HCT: {hct}% (range: {display_range}) (+10)")
    
    return {
        "category": "Anemia Risk",
        "score": min(risk_score, 100),
        "risk_factors": risk_factors
    }


def calculate_kidney_risk(results, contextual_results=None, gender=None, age=None):
  
    risk_score = 0
    risk_factors = []
    
    creat_data = get_value_and_range("Creatinine", results)
    urea_data = get_value_and_range("Urea", results)
    uric_data = get_value_and_range("Uric Acid", results)
    
    thresholds = get_thresholds("kidney")
    
    if creat_data and creat_data["status"] == "HIGH":
        creat = creat_data["value"]
        display_range = creat_data["contextual_range"]
        
        creat_high = thresholds.get("creatinine_high", 2.0)
        creat_elevated = thresholds.get("creatinine_elevated", 1.5)
        
        if creat > creat_high:
            risk_score += 50
            risk_factors.append(f"Highly elevated Creatinine: {creat} mg/dl (+50)")
        elif creat > creat_elevated:
            risk_score += 30
            risk_factors.append(f"Elevated Creatinine: {creat} mg/dl (+30)")
        else:
            risk_score += 15
            risk_factors.append(f"Slightly elevated Creatinine: {creat} mg/dl (range: {display_range}) (+15)")
    
    if urea_data and urea_data["status"] == "HIGH":
        urea = urea_data["value"]
        display_range = urea_data["contextual_range"]
        urea_high = thresholds.get("urea_high", 60.0)
        
        if urea > urea_high:
            risk_score += 30
            risk_factors.append(f"Highly elevated Urea: {urea} mg/dl (+30)")
        else:
            risk_score += 15
            risk_factors.append(f"Elevated Urea: {urea} mg/dl (range: {display_range}) (+15)")
    
    if uric_data and uric_data["status"] == "HIGH":
        uric = uric_data["value"]
        display_range = uric_data["contextual_range"]
        uric_high = thresholds.get("uric_acid_high", 9.0)
        
        if uric > uric_high:
            risk_score += 20
            risk_factors.append(f"Highly elevated Uric Acid: {uric} mg/dl (+20)")
        else:
            risk_score += 10
            risk_factors.append(f"Elevated Uric Acid: {uric} mg/dl (range: {display_range}) (+10)")
    
    return {
        "category": "Kidney Risk",
        "score": min(risk_score, 100),
        "risk_factors": risk_factors
    }


def calculate_infection_risk(results, contextual_results=None, gender=None, age=None):
    
    risk_score = 0
    risk_factors = []
    
    wbc_data = get_value_and_range("WBC", results)
    
    if wbc_data:
        wbc = wbc_data["value"]
        wbc_status = wbc_data["status"]
        wbc_range = wbc_data["value_range"]  # Tuple
        display_range = wbc_data["contextual_range"]
        
        thresholds = get_thresholds("infection")
        wbc_very_high = thresholds.get("wbc_high", 15.0)
        
        if wbc_status == "HIGH":
            if wbc > wbc_very_high:
                risk_score += 60
                risk_factors.append(f"Highly elevated WBC: {wbc} 10^3/uL (+60)")
            else:
                risk_score += 30
                risk_factors.append(f"Elevated WBC: {wbc} 10^3/uL (range: {display_range}) (+30)")
        
        elif wbc_status == "LOW":
            risk_score += 40
            risk_factors.append(f"Low WBC (Leukopenia): {wbc} 10^3/uL (range: {display_range}) (+40)")
    
    return {
        "category": "Infection Risk",
        "score": min(risk_score, 100),
        "risk_factors": risk_factors
    }


def get_risk_level(score):
    
    if score >= 70:
        return "HIGH RISK"
    elif score >= 40:
        return "MODERATE RISK"
    elif score >= 20:
        return "LOW RISK"
    else:
        return "MINIMAL RISK"


def get_recommendation(overall_score, risk_scores):
    
    if overall_score >= 70:
        return "URGENT: Please consult a doctor immediately for comprehensive evaluation."
    elif overall_score >= 40:
        return "ATTENTION: Schedule an appointment with your doctor for further evaluation."
    elif overall_score >= 20:
        return "ADVISORY: Consider a follow-up test in 2-4 weeks. Maintain healthy lifestyle."
    else:
        return "GOOD: Your results look generally normal. Continue regular health checkups."


def calculate_overall_risk(results, contextual_results=None, gender=None, age=None):
    
    anemia_risk = calculate_anemia_risk(results, contextual_results, gender, age)
    kidney_risk = calculate_kidney_risk(results, contextual_results, gender, age)
    infection_risk = calculate_infection_risk(results, contextual_results, gender, age)
    
    all_risks = [anemia_risk, kidney_risk, infection_risk]
    
    individual_scores = [r["score"] for r in all_risks]
    max_score = max(individual_scores) if individual_scores else 0
    avg_score = sum(individual_scores) / len(individual_scores) if individual_scores else 0
    
    overall_score = round(0.6 * max_score + 0.4 * avg_score, 1)
    
    risk_level = get_risk_level(overall_score)
    recommendation = get_recommendation(overall_score, all_risks)
    
    return {
        "overall_score": overall_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "individual_risks": all_risks
    }