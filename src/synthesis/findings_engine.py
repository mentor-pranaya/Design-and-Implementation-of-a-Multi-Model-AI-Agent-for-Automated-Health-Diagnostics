from src.config.reference_loader import get_age_group


def categorize_findings(results, patterns, risk_assessment, contextual_analysis):
    
    findings = {
        "critical": [],      
        "abnormal": [],      
        "borderline": [],    
        "normal": [],        
        "not_found": []      
    }
    
    for param_name, param_data in results.items():
        if param_name in ["Age", "Gender"]:
            continue
        
        if param_data is None:
            findings["not_found"].append(param_name)
            continue
        
        value = param_data.get("value")
        status = param_data.get("status", "UNKNOWN")
        contextual_range = param_data.get("contextual_range", "N/A")
        value_range = param_data.get("value_range")
        
        finding = {
            "parameter": param_name,
            "value": value,
            "unit": param_data.get("unit", ""),
            "status": status,
            "range": contextual_range
        }
        
        if status in ["LOW", "HIGH"]:
            # Check if critical (far from normal)
            if value_range:
                min_val, max_val = value_range
                if status == "LOW" and value < (min_val * 0.7):  # 30% below min
                    finding["severity"] = "critical"
                    findings["critical"].append(finding)
                elif status == "HIGH" and value > (max_val * 1.5):  # 50% above max
                    finding["severity"] = "critical"
                    findings["critical"].append(finding)
                else:
                    finding["severity"] = "abnormal"
                    findings["abnormal"].append(finding)
            else:
                finding["severity"] = "abnormal"
                findings["abnormal"].append(finding)
        
        elif status == "NORMAL":
            # Check if borderline
            if value_range:
                min_val, max_val = value_range
                # Within 5% of boundaries
                if value <= min_val * 1.05 or value >= max_val * 0.95:
                    finding["severity"] = "borderline"
                    findings["borderline"].append(finding)
                else:
                    finding["severity"] = "normal"
                    findings["normal"].append(finding)
            else:
                finding["severity"] = "normal"
                findings["normal"].append(finding)
        else:
            finding["severity"] = "unknown"
            findings["normal"].append(finding)
    
    return findings


def identify_conditions(patterns, categorized_findings, risk_assessment):
    
    conditions = []
    
    # Add conditions from detected patterns
    for pattern in patterns:
        condition = {
            "name": pattern["pattern"],
            "confidence": pattern["confidence"],
            "indicators": pattern["indicators"],
            "description": pattern["description"],
            "severity": pattern.get("severity", "mild"),
            "source": "pattern_detection"
        }
        
        # Determine severity from description
        desc_lower = pattern["description"].lower()
        if "severe" in desc_lower or "urgent" in desc_lower:
            condition["severity"] = "severe"
        elif "moderate" in desc_lower:
            condition["severity"] = "moderate"
        else:
            condition["severity"] = "mild"
        
        conditions.append(condition)
    
    # Check for isolated abnormalities not captured by patterns
    abnormal = categorized_findings.get("abnormal", [])
    critical = categorized_findings.get("critical", [])
    
    # Check for isolated low RBC (not part of anemia pattern)
    rbc_finding = next((f for f in abnormal + critical if f["parameter"] == "RBC"), None)
    anemia_pattern_exists = any("anemia" in c["name"].lower() for c in conditions)
    
    if rbc_finding and not anemia_pattern_exists:
        conditions.append({
            "name": "Low RBC Count",
            "confidence": 70,
            "indicators": [f"Low RBC: {rbc_finding['value']} ({rbc_finding['range']})"],
            "description": "Isolated low RBC - monitor for developing anemia",
            "severity": "mild",
            "source": "isolated_finding"
        })
    
    return conditions


def generate_summary_text(conditions, categorized_findings, age, gender, risk_assessment):
    
    age_group = get_age_group(age)
    
    # Count findings
    critical_count = len(categorized_findings.get("critical", []))
    abnormal_count = len(categorized_findings.get("abnormal", []))
    borderline_count = len(categorized_findings.get("borderline", []))
    normal_count = len(categorized_findings.get("normal", []))
    
    # Build summary
    summary_parts = []
    
    # Patient context
    if age and gender:
        summary_parts.append(f"Analysis for {gender} patient, {age} years old ({age_group}).")
    elif age:
        summary_parts.append(f"Analysis for patient, {age} years old ({age_group}).")
    elif gender:
        summary_parts.append(f"Analysis for {gender} patient.")
    
    # Overall status
    if critical_count > 0:
        summary_parts.append(f"ATTENTION: {critical_count} critical finding(s) require immediate attention.")
    
    if abnormal_count > 0:
        summary_parts.append(f"Found {abnormal_count} parameter(s) outside normal range.")
    
    if borderline_count > 0:
        summary_parts.append(f"{borderline_count} parameter(s) at borderline levels.")
    
    if normal_count > 0 and abnormal_count == 0 and critical_count == 0:
        summary_parts.append("All tested parameters are within normal range.")
    
    # Conditions identified
    if conditions:
        condition_names = [c["name"] for c in conditions]
        summary_parts.append(f"Identified conditions: {', '.join(condition_names)}.")
    
    # Risk level
    risk_level = risk_assessment.get("risk_level", "UNKNOWN")
    overall_score = risk_assessment.get("overall_score", 0)
    summary_parts.append(f"Overall risk assessment: {risk_level} ({overall_score}/100).")
    
    return " ".join(summary_parts)


def synthesize_findings(results, patterns, risk_assessment, contextual_analysis, age=None, gender=None):
   
    # Categorize findings
    categorized = categorize_findings(results, patterns, risk_assessment, contextual_analysis)
    
    # Identify conditions
    conditions = identify_conditions(patterns, categorized, risk_assessment)
    
    # Generate summary text
    summary_text = generate_summary_text(conditions, categorized, age, gender, risk_assessment)
    
       # Build key findings list
    key_findings = []
    
    # Add critical findings
    for finding in categorized.get("critical", []):
        key_findings.append({
            "type": "critical",
            "text": f"{finding['parameter']}: {finding['value']} {finding.get('unit', '')} - Critically {finding['status'].lower()}"
        })
    
    # Add abnormal findings
    for finding in categorized.get("abnormal", []):
        key_findings.append({
            "type": "abnormal",
            "text": f"{finding['parameter']}: {finding['value']} {finding.get('unit', '')} - {finding['status']}"
        })
    
    # Add borderline findings
    for finding in categorized.get("borderline", []):
        key_findings.append({
            "type": "borderline",
            "text": f"{finding['parameter']}: {finding['value']} {finding.get('unit', '')} - Borderline"
        })
    
    return {
        "summary_text": summary_text,
        "key_findings": key_findings,
        "conditions": conditions,
        "categorized_findings": categorized,
        "risk_level": risk_assessment.get("risk_level", "UNKNOWN"),
        "overall_risk_score": risk_assessment.get("overall_score", 0),
        "age_group": get_age_group(age),
        "patient_context": {
            "age": age,
            "gender": gender
        }
    }