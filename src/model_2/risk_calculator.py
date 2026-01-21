"""
Model 2: Risk Calculator
Calculates overall health risk score based on detected patterns and parameter values
"""


def calculate_anemia_risk(results): # Calculate anemia risk score (0-100) based on Hemoglobin, RBC, HCT
  
    risk_score = 0
    risk_factors = []
    
    
    hgb_data = results.get("Hemoglobin") # Get values
    rbc_data = results.get("RBC")
    hct_data = results.get("HCT")
    
    hgb = hgb_data. get("value") if hgb_data else None
    rbc = rbc_data.get("value") if rbc_data else None
    hct = hct_data.get("value") if hct_data else None
    
   
    if hgb is not None:   # Calculate risk based on Hemoglobin
        if hgb < 8.0:
            risk_score += 50
            risk_factors.append(f"Severely low Hemoglobin: {hgb} g/dl (+50)")
        elif hgb < 10.0:
            risk_score += 30
            risk_factors.append(f"Moderately low Hemoglobin: {hgb} g/dl (+30)")
        elif hgb < 12.0:
            risk_score += 15
            risk_factors.append(f"Mildly low Hemoglobin: {hgb} g/dl (+15)")
    
    
    if rbc is not None: # Calculate risk based on RBC
        if rbc < 3.5:
            risk_score += 25
            risk_factors.append(f"Low RBC: {rbc} 10^6/uL (+25)")
        elif rbc < 4.5:
            risk_score += 10
            risk_factors.append(f"Slightly low RBC: {rbc} 10^6/uL (+10)")
    
    
    if hct is not None: # Calculate risk based on HCT
        if hct < 30.0:
            risk_score += 25
            risk_factors.append(f"Low HCT: {hct}% (+25)")
        elif hct < 37.0:
            risk_score += 10
            risk_factors.append(f"Slightly low HCT: {hct}% (+10)")
    
   
    risk_score = min(risk_score, 100)  # Cap at 100
    
    return {
        "category": "Anemia Risk",
        "score": risk_score,
        "risk_factors": risk_factors
    }


def calculate_kidney_risk(results): #Calculate kidney disease risk score (0-100) based on Creatinine, Urea, Uric Acid
 
    risk_score = 0
    risk_factors = []
    
    
    creat_data = results.get("Creatinine")
    urea_data = results.get("Urea")
    uric_data = results.get("Uric Acid")
    
    creat = creat_data.get("value") if creat_data else None
    urea = urea_data.get("value") if urea_data else None
    uric = uric_data.get("value") if uric_data else None
    
    
    if creat is not None: # Calculate risk based on Creatinine
        if creat > 2.0:
            risk_score += 50
            risk_factors.append(f"Highly elevated Creatinine: {creat} mg/dl (+50)")
        elif creat > 1.5:
            risk_score += 30
            risk_factors.append(f"Elevated Creatinine: {creat} mg/dl (+30)")
        elif creat > 1.3:
            risk_score += 15
            risk_factors.append(f"Slightly elevated Creatinine: {creat} mg/dl (+15)")
    
    
    if urea is not None: # Calculate risk based on Urea
        if urea > 60.0:
            risk_score += 30
            risk_factors.append(f"Highly elevated Urea: {urea} mg/dl (+30)")
        elif urea > 43.0:
            risk_score += 15
            risk_factors.append(f"Elevated Urea: {urea} mg/dl (+15)")
    
    
    if uric is not None: # Calculate risk based on Uric Acid
        if uric > 9.0:
            risk_score += 20
            risk_factors.append(f"Highly elevated Uric Acid: {uric} mg/dl (+20)")
        elif uric > 7.2:
            risk_score += 10
            risk_factors.append(f"Elevated Uric Acid: {uric} mg/dl (+10)")
    
    
    risk_score = min(risk_score, 100)
    
    return {
        "category": "Kidney Risk",
        "score": risk_score,
        "risk_factors": risk_factors
    }


def calculate_infection_risk(results): #Calculate infection/inflammation risk score (0-100) based on WBC
 
    risk_score = 0
    risk_factors = []
    
    wbc_data = results.get("WBC")
    wbc = wbc_data.get("value") if wbc_data else None
    
    if wbc is not None:
        if wbc > 15.0:
            risk_score += 60
            risk_factors.append(f"Highly elevated WBC: {wbc} 10^3/uL (+60)")
        elif wbc > 11.0:
            risk_score += 30
            risk_factors.append(f"Elevated WBC: {wbc} 10^3/uL (+30)")
        elif wbc < 4.0:
            risk_score += 40
            risk_factors.append(f"Low WBC (Leukopenia): {wbc} 10^3/uL (+40)")
    
    
    risk_score = min(risk_score, 100) # Cap at 100
    
    return {
        "category": "Infection Risk",
        "score": risk_score,
        "risk_factors": risk_factors
    }


def get_risk_level(score): #Convert numeric score to risk level text
    
    if score >= 70:
        return "HIGH RISK"
    elif score >= 40:
        return "MODERATE RISK"
    elif score >= 20:
        return "LOW RISK"
    else:
        return "MINIMAL RISK"


def get_recommendation(overall_score, risk_scores): # Generate recommendation based on overall risk score
   
    if overall_score >= 70:
        return "URGENT:  Please consult a doctor immediately for comprehensive evaluation."
    elif overall_score >= 40:
        return "ATTENTION: Schedule an appointment with your doctor for further evaluation."
    elif overall_score >= 20:
        return "ADVISORY: Consider a follow-up test in 2-4 weeks.  Maintain healthy lifestyle."
    else:
        return "GOOD: Your results look generally normal. Continue regular health checkups."


def calculate_overall_risk(results): #Calculate overall health risk by combining all individual risk scores
   
    anemia_risk = calculate_anemia_risk(results) # Calculate individual risks
    kidney_risk = calculate_kidney_risk(results)
    infection_risk = calculate_infection_risk(results)
    
    
    all_risks = [anemia_risk, kidney_risk, infection_risk] # Collect all risk scores
    
    # Calculate weighted overall score
   
    individual_scores = [r["score"] for r in all_risks]  # Using max score approach - overall risk is driven by highest concern
    max_score = max(individual_scores) if individual_scores else 0
    avg_score = sum(individual_scores) / len(individual_scores) if individual_scores else 0
    
    
    overall_score = round(0.6 * max_score + 0.4 * avg_score, 1) # Overall score:  60% max risk + 40% average risk
    
    risk_level = get_risk_level(overall_score) # Get risk level and recommendation
    recommendation = get_recommendation(overall_score, all_risks)
    
    return {
        "overall_score":  overall_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "individual_risks": all_risks
    }