def pattern_recognition_agent(interpreted_data):
    insights = []
    # Convert list to a searchable dictionary for easy access
    d = {item['parameter'].lower(): item for item in interpreted_data}
    
    # --- PATTERN 1: ANEMIA TYPING ---
    hb = d.get('hemoglobin')
    mcv = d.get('mcv')
    if hb and mcv:
        if hb['status'] == "Low" and mcv['value'] < 80:
            insights.append({
                "pattern": "Microcytic Anemia",
                "finding": "Low Hemoglobin combined with low MCV strongly suggests Iron Deficiency.",
                "severity": "High"
            })
        elif hb['status'] == "Low" and mcv['value'] > 100:
            insights.append({
                "pattern": "Macrocytic Anemia",
                "finding": "Low Hemoglobin with high MCV suggests Vitamin B12 or Folate deficiency.",
                "severity": "High"
            })

    # --- PATTERN 2: LIVER HEALTH (De Ritis Ratio) ---
    ast = d.get('ast')
    alt = d.get('alt')
    if ast and alt:
        ratio = ast['value'] / alt['value']
        if ratio > 2.0 and ast['status'] == "High":
            insights.append({
                "pattern": "Liver Stress Pattern",
                "finding": f"AST/ALT Ratio is {ratio:.2f}. Values > 2.0 may indicate specific liver stress.",
                "severity": "Critical"
            })

    # --- PATTERN 3: KIDNEY & HYDRATION ---
    bun = d.get('bun')
    creatinine = d.get('creatinine')
    albumin = d.get('albumin')
    if bun and creatinine and albumin:
        ratio = bun['value'] / creatinine['value']
        if ratio > 20 and albumin['status'] == "High":
            insights.append({
                "pattern": "Dehydration Marker",
                "finding": "Elevated BUN/Creatinine ratio and High Albumin suggest significant dehydration.",
                "severity": "Moderate"
            })

    # --- PATTERN 4: LIPID RATIO (Cardio Risk) ---
    tg = d.get('triglycerides')
    hdl = d.get('hdl cholesterol')
    if tg and hdl:
        risk_ratio = tg['value'] / hdl['value']
        if risk_ratio > 3.0:
            insights.append({
                "pattern": "Atherogenic Index",
                "finding": f"TG/HDL ratio is {risk_ratio:.2f}. High ratios correlate with small dense LDL particles.",
                "severity": "High"
            })

    return insights
