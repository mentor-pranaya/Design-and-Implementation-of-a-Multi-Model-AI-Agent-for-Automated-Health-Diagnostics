def pattern_recognition_agent(interpreted_data):
    insights = []
    
    # Extract values for calculation
    data_map = {item['parameter']: item['value'] for item in interpreted_data}
    
    # 1. Lipid Panel Pattern: TG/HDL Ratio (Metabolic Risk)
    if 'Triglycerides' in data_map and 'HDL Cholesterol' in data_map:
        tg_hdl_ratio = round(data_map['Triglycerides'] / data_map['HDL Cholesterol'], 2)
        if tg_hdl_ratio > 3.0:
            insights.append({
                "pattern": "Metabolic Syndrome Indicator",
                "finding": f"High TG/HDL ratio ({tg_hdl_ratio}) suggests increased insulin resistance risk.",
                "severity": "High"
            })

    # 2. Kidney Function Pattern: BUN/Creatinine Ratio
    if 'BUN' in data_map and 'Creatinine' in data_map:
        ratio = round(data_map['BUN'] / data_map['Creatinine'], 2)
        if ratio > 20:
            insights.append({
                "pattern": "Prerenal Azotemia Pattern",
                "finding": f"BUN/Creatinine ratio of {ratio} may indicate dehydration or decreased blood flow to kidneys.",
                "severity": "Moderate"
            })

    # 3. Cardiovascular Risk (Simplified ASCVD approach)
    ldl = data_map.get('LDL Cholesterol', 0)
    hdl = data_map.get('HDL Cholesterol', 0)
    if ldl > 160 and hdl < 40:
        insights.append({
            "pattern": "High Cardiovascular Risk",
            "finding": "Combined high LDL and low HDL significantly increases plaque buildup risk.",
            "severity": "Critical"
        })
        
    return insights
