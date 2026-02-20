def pattern_recognition_agent(interpreted_data):
    """
    Detects clinical biomarker patterns using robust name matching and safe ratios.
    """

    insights = []

    # ---- Flexible Parameter Alias Mapping ----
    ALIAS = {
        "hemoglobin": ["hemoglobin", "hb", "hgb"],
        "mcv": ["mcv", "mean corpuscular volume"],
        "ast": ["ast", "sgot"],
        "alt": ["alt", "sgpt"],
        "bun": ["bun", "urea"],
        "creatinine": ["creatinine", "creat"],
        "albumin": ["albumin"],
        "triglycerides": ["triglycerides", "tg"],
        "hdl": ["hdl", "hdl cholesterol"],
        "glucose": ["glucose", "fasting glucose", "fbs"]
    }

    # Build lookup dict
    d = {}
    for item in interpreted_data:
        name = item.get("parameter", "").lower()
        for key, aliases in ALIAS.items():
            if any(a in name for a in aliases):
                d[key] = item

    # Safe ratio function
    def get_ratio(a, b):
        if a in d and b in d:
            x = d[a].get("value", 0)
            y = d[b].get("value", 0)
            return x / y if y > 0 else None
        return None

    # ---------- ANEMIA PATTERN ----------
    hb = d.get("hemoglobin")
    mcv = d.get("mcv")

    if hb and mcv and hb.get("status") == "Low":
        mcv_val = mcv.get("value", 0)

        if mcv_val < 80:
            insights.append({
                "pattern": "Microcytic Anemia",
                "finding": "Suggests iron deficiency or chronic blood loss.",
                "severity": "High"
            })
        elif mcv_val > 100:
            insights.append({
                "pattern": "Macrocytic Anemia",
                "finding": "Suggests Vitamin B12 or folate deficiency.",
                "severity": "High"
            })
        else:
            insights.append({
                "pattern": "Normocytic Anemia",
                "finding": "May indicate chronic disease or acute blood loss.",
                "severity": "Moderate"
            })

    # ---------- LIVER STRESS ----------
    ratio = get_ratio("ast", "alt")
    if ratio and ratio > 2 and d["ast"]["status"] == "High" and d["alt"]["status"] == "High":
        insights.append({
            "pattern": "Liver Injury Pattern",
            "finding": f"AST/ALT ratio = {ratio:.2f}, consistent with hepatic injury risk.",
            "severity": "Critical"
        })

    # ---------- KIDNEY / DEHYDRATION ----------
    bun_cre = get_ratio("bun", "creatinine")
    if bun_cre and bun_cre > 20:
        insights.append({
            "pattern": "Dehydration or Renal Stress",
            "finding": f"BUN/Creatinine ratio = {bun_cre:.1f}. May indicate dehydration or renal hypoperfusion.",
            "severity": "Moderate"
        })

    # ---------- CARDIOVASCULAR RISK ----------
    if "triglycerides" in d and "hdl" in d:
        tg = d["triglycerides"]["value"]
        hdl = d["hdl"]["value"]
        if hdl > 0:
            ratio = tg / hdl
            if ratio > 4:
                sev = "High"
            elif ratio > 2:
                sev = "Moderate"
            else:
                sev = "Low"

            insights.append({
                "pattern": "Atherogenic Index (TG/HDL)",
                "finding": f"TG/HDL ratio = {ratio:.2f}",
                "severity": sev
            })

    # ---------- DIABETES RISK ----------
    glu = d.get("glucose")
    if glu:
        g = glu["value"]
        if g >= 126:
            insights.append({
                "pattern": "Diabetes Range Glucose",
                "finding": f"Glucose = {g} mg/dL (diabetic range).",
                "severity": "Critical"
            })
        elif g >= 100:
            insights.append({
                "pattern": "Prediabetes Range Glucose",
                "finding": f"Glucose = {g} mg/dL (impaired fasting glucose).",
                "severity": "Moderate"
            })
    # ✅ If no patterns detected → add disclaimer

    if len(insights) == 0:
        insights.append({
            "pattern": "No Significant Clinical Pattern Detected",
            "finding": "All extracted biomarkers appear within normal reference ranges or insufficient data was available for pattern detection.",
            "severity": "Low"
        })

    return insights
