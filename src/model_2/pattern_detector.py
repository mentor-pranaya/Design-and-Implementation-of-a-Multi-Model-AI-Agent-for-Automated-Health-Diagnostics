def detect_anemia(results): # detects anemia based on Hemoglobin, RBC , and HCT values
    findings = {
        "pattern" : None,
        "confidence" : 0,
        "indicators" : [],
        "description" : ""
    }

    hgb_data = results.get("Hemoglobin") # getting values
    rbc_data = results.get("RBC")
    hct_data = results.get("HCT")

    hgb = hgb_data.get("value") if hgb_data else None  
    rbc = rbc_data.get("value") if rbc_data else None
    hct = hct_data.get("value") if hct_data else None

    low_count = 0 # low counter

    if hgb is not None and hgb < 12.0:
        low_count += 1
        findings["indicators"].append(f"Low Hemoglobin: {hgb} g/dl")

    if rbc is not None and rbc < 4.5:
        low_count += 1
        findings["indicators"].append(f"Low RBC: {rbc} 10^6/ul")

    if hct is not None and hct < 37.0:
        low_count += 1
        findings["indicators"].append(f"Low HCT: {hct}%")
    
    
   
    if low_count >= 2:    # Determine pattern and confidence
        findings["pattern"] = "Anemia Indicators"
        findings["confidence"] = round(low_count/3*100,1)
        
        if hgb is not None:# Classify severity based on hemoglobin
            
            if hgb < 8.0:
                findings["description"] = "Severe Anemia - Urgent medical attention recommended"
            elif hgb < 10:
                findings["description"] = "Moderate Anemia - Medical consultation recommended"
            else:
                findings["description"] = "Mild Anemia - Monitor and consider dietary changes"
    
    return findings

def detect_iron_deficiency(results): #  Detect iron deficiency anemia based on MCV, MCH, MCHC Microcytic hypochromic anemia
    
 
    findings = {
        "pattern": None,
        "confidence": 0,
        "indicators": [],
        "description": ""
    }
    
    mcv_data = results.get("MCV")
    mch_data = results.get("MCH")
    mchc_data = results.get("MCHC")
    
    mcv = mcv_data. get("value") if mcv_data else None
    mch = mch_data.get("value") if mch_data else None
    mchc = mchc_data.get("value") if mchc_data else None
    
    low_count = 0
    
    if mcv is not None and mcv < 80.0:
        low_count += 1
        findings["indicators"]. append(f"Low MCV:  {mcv} fl (Microcytic)")
    
    if mch is not None and mch < 27.0:
        low_count += 1
        findings["indicators"].append(f"Low MCH: {mch} pg (Hypochromic)")
    
    if mchc is not None and mchc < 32.0:
        low_count += 1
        findings["indicators"].append(f"Low MCHC: {mchc} g/dl")
    
    if low_count >= 2:
        findings["pattern"] = "Iron Deficiency Anemia Indicators"
        findings["confidence"] = round(low_count / 3 * 100, 1)
        findings["description"] = "Microcytic hypochromic pattern - Consider iron studies"
    
    return findings



def detect_kidney_disease_risk(results):  #detect kidney isease based on Creatine, Urea, Uric Acid
    findings = {
        "pattern" : None,
        "confidence" : 0,
        "indicators" : [],
        "risk_level" : "Low",
        "description" : ""
    }
    creat_data = results.get("Creatinine")
    urea_data = results.get("Urea")
    uric_data = results.get("Uric Acid")

    creat = creat_data.get("value") if creat_data else None
    urea = urea_data.get("value") if urea_data else None
    uric = uric_data.get("value") if uric_data else None

    high_count = 0

    if creat is not None and creat > 1.3:
        high_count += 1
        findings["indicators"].append(f"High Creatinine:  {creat} mg/dl")
    
    if urea is not None and urea > 43.0:
        high_count += 1
        findings["indicators"].append(f"High Urea: {urea} mg/dl")
    
    if uric is not None and uric > 7.2:
        high_count += 1
        findings["indicators"].append(f"High Uric Acid: {uric} mg/dl")

    if high_count >= 1:
            findings["pattern"] = "Kidney Function Concern"
            findings["confidence"] = round(high_count/3*100,1)

            if high_count >= 2:
                findings["risk_level"] = "High"
                findings["description"] = "Multiple kidney markers elevated - Medical consultation strongly recommended"
            else:
                findings["risk_level"] = "Moderate"
                findings["description"] = "Single kidney marker elevated - Monitor and retest recommended"
    
    return findings

def detect_infection_indicators(results): # Detect possible infection based on WBC count
    
    findings = {
        "pattern":  None,
        "confidence": 0,
        "indicators": [],
        "description": ""
    }
    
    wbc_data = results.get("WBC")
    wbc = wbc_data.get("value") if wbc_data else None
    
    if wbc is not None: 
        if wbc > 11.0:
            findings["pattern"] = "Possible Infection/Inflammation"
            findings["confidence"] = min(round((wbc - 11.0) / 5 * 100, 1), 100)
            findings["indicators"].append(f"Elevated WBC: {wbc} 10^3/uL")
            findings["description"] = "High WBC may indicate infection or inflammation"
        elif wbc < 4.0:
            findings["pattern"] = "Low WBC (Leukopenia)"
            findings["confidence"] = 80
            findings["indicators"].append(f"Low WBC: {wbc} 10^3/uL")
            findings["description"] = "Low WBC may indicate immune system issues"
    
    return findings

def detect_all_patterns(results): # Run all pattern detection and return combined findings

    all_patterns = []
    
    # Run all detectors
    anemia = detect_anemia(results)
    if anemia["pattern"]:
        all_patterns.append(anemia)
    
    iron_def = detect_iron_deficiency(results)
    if iron_def["pattern"]: 
        all_patterns.append(iron_def)
    
    kidney = detect_kidney_disease_risk(results)
    if kidney["pattern"]: 
        all_patterns.append(kidney)
    
    infection = detect_infection_indicators(results)
    if infection["pattern"]: 
        all_patterns.append(infection)
    
    return all_patterns