def detect_health_patterns(model1_results):
    """
    Model-2: Health Risk Pattern Recognition

    Input:
    model1_results = {
        "hemoglobin": {"value": 9.5, "status": "Low"},
        "mcv": {"value": 75, "status": "Low"},
        "wbc_count": {"value": 3000, "status": "Low"},
        "platelet_count": {"value": 500000, "status": "High"}
    }
    """

    patterns = []

   
    # 1️⃣ Anemia Risk (Microcytic)
    
    if (
        model1_results.get("hemoglobin", {}).get("status") == "Low" and
        (
            model1_results.get("mcv", {}).get("status") == "Low" or
            model1_results.get("rbc_count", {}).get("status") == "Low"
        )
    ):
        patterns.append({
            "pattern": "Anemia Risk",
            "risk_level": "Moderate",
            "reason": "Low hemoglobin with abnormal red blood cell indices"
        })

    # -------------------------------------------------
    # 2️⃣ Infection Risk (Leukocytosis)
    # -------------------------------------------------
    if model1_results.get("wbc_count", {}).get("status") == "High":
        patterns.append({
            "pattern": "Possible Infection Risk",
            "risk_level": "High",
            "reason": "Elevated white blood cell count"
        })

    # -------------------------------------------------
    # 3️⃣ Leukopenia Risk (NEW)
    # -------------------------------------------------
    if model1_results.get("wbc_count", {}).get("status") == "Low":
        patterns.append({
            "pattern": "Leukopenia Risk",
            "risk_level": "Moderate",
            "reason": "Low white blood cell count indicating reduced immune defense"
        })

    # -------------------------------------------------
    # 4️⃣ Thrombocytopenia / Bleeding Risk (LOW PLATELETS)
    # -------------------------------------------------
    if model1_results.get("platelet_count", {}).get("status") == "Low":
        patterns.append({
            "pattern": "Bleeding Risk (Thrombocytopenia)",
            "risk_level": "High",
            "reason": "Low platelet count may increase bleeding tendency"
        })

    # -------------------------------------------------
    # 5️⃣ Thrombocytosis Risk (HIGH PLATELETS) (NEW)
    # -------------------------------------------------
    if model1_results.get("platelet_count", {}).get("status") == "High":
        patterns.append({
            "pattern": "Thrombocytosis Risk",
            "risk_level": "Moderate",
            "reason": "Elevated platelet count may increase clotting risk"
        })

    return patterns
