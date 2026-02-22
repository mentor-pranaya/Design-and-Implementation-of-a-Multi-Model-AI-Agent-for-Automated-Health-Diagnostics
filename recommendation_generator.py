"""
Personalized Recommendation Generator (Milestone 3)
Generates actionable, personalized health recommendations based on synthesized findings
from all models, directly linked to specific identified abnormalities and risk areas.
"""


def generate_recommendations(synthesis_findings, parameters, interpretation, risk_assessment, age=None, gender=None):
    """
    Generate comprehensive, personalized recommendations based on synthesized findings.
    
    Args:
        synthesis_findings: dict - Output from synthesis_engine
        parameters: dict - Raw extracted blood parameters
        interpretation: dict - Model 1 output
        risk_assessment: dict - Model 2 output
        age: int - User age (optional)
        gender: str - User gender (optional)
    
    Returns:
        dict - Personalized recommendations organized by category
    """
    
    recommendations = {
        "dietary_recommendations": [],
        "lifestyle_recommendations": [],
        "medical_follow_up": [],
        "monitoring_schedule": [],
        "supplementation_advice": [],
        "activity_recommendations": [],
        "risk_reduction_strategies": [],
        "disclaimers": []
    }
    
    # ===== DIETARY RECOMMENDATIONS =====
    glucose = parameters.get("Glucose", 0)
    cholesterol = parameters.get("Cholesterol", 0)
    triglycerides = parameters.get("Triglycerides", 0)
    hemoglobin = parameters.get("Hemoglobin", 0)
    
    # High Glucose - Diabetes Risk
    if glucose >= 110:
        recommendations["dietary_recommendations"].append({
            "category": "Glucose Management",
            "finding": f"Elevated glucose level ({glucose} mg/dL)",
            "recommendations": [
                "Reduce refined carbohydrates and sugary foods",
                "Increase fiber intake through whole grains, vegetables, and legumes",
                "Eat regular, balanced meals to maintain steady blood sugar",
                "Limit alcohol consumption, especially sweet drinks",
                "Consider meal planning with complex carbohydrates",
                "Monitor portion sizes and eat smaller, frequent meals"
            ],
            "priority": "HIGH" if glucose >= 126 else "MODERATE",
            "foods_to_avoid": ["White bread", "Sugary drinks", "Pastries", "Candy", "Processed snacks"],
            "foods_to_include": ["Oats", "Brown rice", "Legumes", "Leafy greens", "Berries", "Nuts"]
        })
    
    # High Cholesterol - Cardiovascular Risk
    if cholesterol > 200 or parameters.get("LDL", 0) > 100:
        recommendations["dietary_recommendations"].append({
            "category": "Cholesterol Management",
            "finding": f"Elevated cholesterol level ({cholesterol} mg/dL)" if cholesterol > 200 else f"Elevated LDL ({parameters.get('LDL', 0)} mg/dL)",
            "recommendations": [
                "Reduce saturated fat intake (aim for <7% of daily calories)",
                "Eliminate or limit trans fats (found in processed foods)",
                "Increase fiber intake (soluble fiber helps lower cholesterol)",
                "Include heart-healthy fats (omega-3, olive oil)",
                "Consume lean proteins and plant-based proteins",
                "Reduce sodium intake to <2,300mg per day"
            ],
            "priority": "HIGH" if cholesterol > 240 else "MODERATE",
            "foods_to_avoid": ["Red meat", "Full-fat dairy", "Processed foods", "Fried foods", "Butter", "Coconut oil"],
            "foods_to_include": ["Fatty fish (salmon)", "Oats", "Almonds", "Olive oil", "Avocados", "Berries"]
        })
    
    # High Triglycerides
    if triglycerides > 150:
        recommendations["dietary_recommendations"].append({
            "category": "Triglyceride Management",
            "finding": f"Elevated triglycerides ({triglycerides} mg/dL)",
            "recommendations": [
                "Reduce simple carbohydrates and sugar",
                "Limit alcohol consumption significantly",
                "Increase omega-3 fatty acids (fish, flaxseed)",
                "Maintain healthy weight through balanced diet",
                "Eat whole foods instead of processed foods",
                "Increase physical activity combined with dietary changes"
            ],
            "priority": "MODERATE",
            "foods_to_avoid": ["Sugar", "Alcohol", "Refined grains", "Sugary beverages"],
            "foods_to_include": ["Salmon", "Sardines", "Flaxseeds", "Walnuts", "Vegetables"]
        })
    
    # Low/High Hemoglobin - Anemia/Polycythemia
    if hemoglobin < 12:
        recommendations["dietary_recommendations"].append({
            "category": "Anemia Management",
            "finding": f"Low hemoglobin level ({hemoglobin} g/dL)",
            "recommendations": [
                "Increase iron-rich foods in your diet",
                "Pair iron sources with vitamin C for better absorption",
                "Avoid excessive tea and coffee which inhibit iron absorption",
                "Include lean red meat, poultry, or seafood",
                "Consider plant-based iron sources (legumes, spinach)",
                "Consult doctor about iron supplementation"
            ],
            "priority": "HIGH",
            "foods_to_avoid": ["Excessive tea/coffee", "Whole grains with high phytates (when anemic)"],
            "foods_to_include": ["Red meat", "Chicken", "Fish", "Spinach", "Lentils", "Fortified cereals", "Citrus fruits"]
        })
    
    # ===== LIFESTYLE RECOMMENDATIONS =====
    
    # Cardiovascular risk
    if risk_assessment.get("Cardiovascular Risk") in ["HIGH", "MODERATE"]:
        recommendations["lifestyle_recommendations"].append({
            "category": "Cardiovascular Health",
            "finding": f"Cardiovascular Risk Level: {risk_assessment.get('Cardiovascular Risk')}",
            "recommendations": [
                "Engage in regular aerobic exercise (150 minutes/week moderate intensity)",
                "Include strength training 2-3 times per week",
                "Manage stress through meditation, yoga, or relaxation techniques",
                "Ensure adequate sleep (7-9 hours per night)",
                "Avoid smoking and secondhand smoke exposure",
                "Limit alcohol consumption (≤2 drinks/day for men, ≤1 for women)"
            ],
            "priority": "HIGH" if risk_assessment.get("Cardiovascular Risk") == "HIGH" else "MODERATE",
            "stress_management": ["Daily 10-15 minute meditation", "Regular yoga practice", "Breathing exercises"],
            "activity_types": ["Brisk walking", "Swimming", "Cycling", "Running", "Dancing"]
        })
    
    # Diabetes risk
    if risk_assessment.get("Diabetes Risk") in ["HIGH", "MODERATE"]:
        recommendations["lifestyle_recommendations"].append({
            "category": "Diabetes Prevention",
            "finding": f"Diabetes Risk Level: {risk_assessment.get('Diabetes Risk')}",
            "recommendations": [
                "Maintain healthy weight (BMI 18.5-24.9)",
                "Exercise regularly (at least 150 minutes/week)",
                "Monitor blood sugar levels regularly",
                "Reduce stress and improve sleep quality",
                "Avoid rapid weight gain",
                "Limit sedentary behavior and screen time"
            ],
            "priority": "HIGH" if risk_assessment.get("Diabetes Risk") == "HIGH" else "MODERATE",
            "weight_management": "Aim for 5-10% weight loss if overweight",
            "activity_types": ["Brisk walking", "Swimming", "Cycling", "Strength training"]
        })
    
    # Anemia risk
    if risk_assessment.get("Anemia Risk") in ["HIGH", "MODERATE"]:
        recommendations["lifestyle_recommendations"].append({
            "category": "Anemia Management",
            "finding": f"Anemia Risk Level: {risk_assessment.get('Anemia Risk')}",
            "recommendations": [
                "Avoid strenuous activities until hemoglobin levels improve",
                "Get adequate rest and sleep",
                "Manage stress appropriately",
                "Avoid medications that may worsen anemia (consult doctor)",
                "Stay hydrated",
                "Avoid alcohol which may worsen anemia"
            ],
            "priority": "HIGH",
            "activity_level": "Light to moderate until treatment begins",
            "rest_requirements": "Ensure 8+ hours of sleep nightly"
        })
    
    # ===== MEDICAL FOLLOW-UP =====
    
    # High risk areas requiring urgent follow-up
    urgent_risks = [cat for cat, level in risk_assessment.items() if level == "HIGH"]
    if urgent_risks:
        recommendations["medical_follow_up"].append({
            "urgency": "URGENT",
            "recommendation": f"Schedule appointment with primary care physician within 1 week to discuss: {', '.join(urgent_risks)}",
            "specialists_to_consider": _get_specialist_recommendations(urgent_risks),
            "tests_to_request": _get_recommended_tests(parameters, interpretation, risk_assessment)
        })
    
    # Moderate risk follow-up
    moderate_risks = [cat for cat, level in risk_assessment.items() if level == "MODERATE"]
    if moderate_risks:
        recommendations["medical_follow_up"].append({
            "urgency": "RECOMMENDED",
            "recommendation": f"Schedule appointment with primary care physician within 2-4 weeks to discuss: {', '.join(moderate_risks)}",
            "specialists_to_consider": _get_specialist_recommendations(moderate_risks),
            "tests_to_request": _get_recommended_tests(parameters, interpretation, risk_assessment)
        })
    
    # Routine follow-up
    if not urgent_risks and not moderate_risks:
        recommendations["medical_follow_up"].append({
            "urgency": "ROUTINE",
            "recommendation": "Schedule routine check-up and blood work in 6-12 months",
            "specialists_to_consider": [],
            "tests_to_request": ["Standard annual blood work", "Lipid panel"]
        })
    
    # ===== MONITORING SCHEDULE =====
    
    if urgent_risks:
        recommendations["monitoring_schedule"].append({
            "frequency": "Monthly",
            "focus_areas": urgent_risks,
            "parameters_to_track": _get_parameters_to_track(parameters, interpretation),
            "method": "Regular blood tests as recommended by physician"
        })
    elif moderate_risks:
        recommendations["monitoring_schedule"].append({
            "frequency": "Every 3 months",
            "focus_areas": moderate_risks,
            "parameters_to_track": _get_parameters_to_track(parameters, interpretation),
            "method": "Blood tests and regular check-ups"
        })
    else:
        recommendations["monitoring_schedule"].append({
            "frequency": "Annually",
            "focus_areas": ["General health", "Preventive screening"],
            "parameters_to_track": ["Glucose", "Cholesterol", "Hemoglobin"],
            "method": "Annual physical examination and standard blood work"
        })
    
    # ===== SUPPLEMENTATION ADVICE =====
    
    if hemoglobin < 12:
        recommendations["supplementation_advice"].append({
            "supplement": "Iron",
            "reason": "Low hemoglobin detected",
            "dosage": "Consult with physician for appropriate dosage",
            "note": "Take with vitamin C sources for better absorption. Avoid with calcium/dairy products."
        })
    
    if parameters.get("Glucose", 0) >= 110:
        recommendations["supplementation_advice"].append({
            "supplement": "Chromium & Alpha Lipoic Acid",
            "reason": "May help improve insulin sensitivity and glucose control",
            "dosage": "Consult with physician or registered dietitian",
            "note": "Supplement with medical supervision, especially if on diabetes medications"
        })
    
    if cholesterol > 200:
        recommendations["supplementation_advice"].append({
            "supplement": "Omega-3 Fatty Acids (Fish Oil)",
            "reason": "May help lower triglycerides and support heart health",
            "dosage": "Consult with physician (typically 1-3 grams EPA/DHA per day)",
            "note": "Use pharmaceutical-grade supplements. May interact with blood thinners."
        })
    
    recommendations["supplementation_advice"].append({
        "supplement": "Multivitamin with Minerals",
        "reason": "General nutritional support and deficiency prevention",
        "dosage": "Follow label instructions",
        "note": "Optional but recommended. Choose a high-quality brand."
    })
    
    # ===== ACTIVITY RECOMMENDATIONS =====
    
    activity_plan = _generate_activity_plan(age, gender, risk_assessment)
    recommendations["activity_recommendations"].append(activity_plan)
    
    # ===== RISK REDUCTION STRATEGIES =====
    
    strategies = _generate_risk_reduction_strategies(risk_assessment, age, gender)
    for strategy in strategies:
        recommendations["risk_reduction_strategies"].append(strategy)
    
    # ===== DISCLAIMERS =====
    
    recommendations["disclaimers"].append({
        "disclaimer": "IMPORTANT MEDICAL DISCLAIMER",
        "content": [
            "This AI-generated report is NOT a substitute for professional medical advice, diagnosis, or treatment.",
            "Always consult with a qualified healthcare provider before making any health decisions.",
            "The interpretations and recommendations provided are based on available data and general medical guidelines.",
            "Individual health situations may vary significantly, and only a qualified physician can provide personalized medical advice.",
            "Any abnormal results should be discussed with your healthcare provider before taking action.",
            "This system is designed to provide informational guidance only, not medical diagnosis."
        ]
    })
    
    return recommendations


def _get_specialist_recommendations(risk_categories):
    """Get specialist recommendations based on risk categories."""
    specialist_map = {
        "Cardiovascular Risk": ["Cardiologist"],
        "Diabetes Risk": ["Endocrinologist", "Diabetes Educator"],
        "Anemia Risk": ["Hematologist"],
        "Liver Risk": ["Hepatologist", "Gastroenterologist"],
        "Kidney Risk": ["Nephrologist"]
    }
    
    specialists = []
    for risk in risk_categories:
        specialists.extend(specialist_map.get(risk, []))
    
    return list(set(specialists))  # Remove duplicates


def _get_recommended_tests(parameters, interpretation, risk_assessment):
    """Get recommended follow-up tests based on findings."""
    tests = []
    
    if parameters.get("Glucose", 0) >= 110:
        tests.extend(["Fasting Glucose", "HbA1c (Glycated Hemoglobin)", "Oral Glucose Tolerance Test"])
    
    if parameters.get("Cholesterol", 0) > 200:
        tests.extend(["Lipid Panel (LDL, HDL, Triglycerides)", "Lipoprotein(a)"])
    
    if parameters.get("Hemoglobin", 0) < 12:
        tests.extend(["Iron Panel", "B12 and Folate Levels", "Reticulocyte Count"])
    
    if interpretation.get("ALT") == "HIGH" or interpretation.get("AST") == "HIGH":
        tests.extend(["Hepatitis Panel", "Liver Ultrasound"])
    
    if interpretation.get("Creatinine") == "HIGH" or interpretation.get("BUN") == "HIGH":
        tests.extend(["Kidney Function Panel", "Urinalysis", "Kidney Ultrasound"])
    
    if risk_assessment.get("Cardiovascular Risk") in ["HIGH", "MODERATE"]:
        tests.extend(["ECG", "Stress Test (as appropriate)"])
    
    return list(set(tests))  # Remove duplicates


def _get_parameters_to_track(parameters, interpretation):
    """Get key parameters to track over time."""
    track = []
    
    for param, status in interpretation.items():
        if status != "NORMAL":
            track.append(param)
    
    track.extend(["Glucose", "Cholesterol", "Hemoglobin"])  # Always track these
    
    return list(set(track))


def _generate_activity_plan(age=None, gender=None, risk_assessment=None):
    """Generate personalized activity/exercise plan."""
    
    base_activity = {
        "weekly_goal_minutes": 150,
        "intensity": "Moderate (50-70% max heart rate)",
        "frequency": "5 days per week minimum",
        "activities": [],
        "precautions": [],
        "rest_days": 2
    }
    
    risk_assessment = risk_assessment or {}
    
    # Adjust based on age
    if age and age > 65:
        base_activity["weekly_goal_minutes"] = 150
        base_activity["intensity"] = "Light to Moderate (40-60% max heart rate)"
        base_activity["activities"] = ["Walking", "Swimming", "Water aerobics", "Tai Chi", "Gentle yoga"]
        base_activity["precautions"].append("Start slowly and increase gradually")
        base_activity["precautions"].append("Stay well-hydrated")
        base_activity["precautions"].append("Warm up for 5-10 minutes before exercise")
    else:
        base_activity["activities"] = ["Brisk walking", "Jogging", "Cycling", "Swimming", "Group fitness", "Sports"]
    
    # Adjust based on cardiovascular risk
    if risk_assessment.get("Cardiovascular Risk") == "HIGH":
        base_activity["precautions"].append("Get medical clearance before starting new exercise program")
        base_activity["precautions"].append("Avoid intense exercise until cleared by physician")
        base_activity["weekly_goal_minutes"] = 150
        base_activity["intensity"] = "Light to Moderate (40-60%)"
    
    # Adjust based on diabetes risk
    if risk_assessment.get("Diabetes Risk") in ["HIGH", "MODERATE"]:
        base_activity["weekly_goal_minutes"] = 150
        base_activity["activities"].append("Weight training (2-3 times weekly)")
        base_activity["precautions"].append("Check blood sugar before and after exercise")
    
    # Adjust based on anemia
    if risk_assessment.get("Anemia Risk") == "HIGH":
        base_activity["weekly_goal_minutes"] = 30  # Reduced
        base_activity["intensity"] = "Light (30-40% max heart rate)"
        base_activity["precautions"].append("Avoid strenuous activity")
        base_activity["precautions"].append("Rest when fatigued")
    
    return {
        "category": "Exercise & Physical Activity",
        "plan": base_activity,
        "progression": "Gradually increase intensity and duration over 4-6 weeks"
    }


def _generate_risk_reduction_strategies(risk_assessment, age=None, gender=None):
    """Generate comprehensive risk reduction strategies."""
    strategies = []
    
    # Cardiovascular risk reduction
    if risk_assessment.get("Cardiovascular Risk") in ["HIGH", "MODERATE"]:
        strategies.append({
            "risk_area": "Cardiovascular Health",
            "strategies": [
                "Maintain blood pressure at healthy levels (<120/80 mmHg)",
                "Manage cholesterol levels through diet and medication if needed",
                "Quit smoking completely",
                "Manage stress through relaxation techniques",
                "Limit sodium intake to <2,300mg per day",
                "Maintain healthy weight",
                "Consider aspirin therapy (consult physician)",
                "Get adequate sleep (7-9 hours nightly)"
            ],
            "timeline": "Implement over 4 weeks, reassess in 3 months"
        })
    
    # Diabetes risk reduction
    if risk_assessment.get("Diabetes Risk") in ["HIGH", "MODERATE"]:
        strategies.append({
            "risk_area": "Diabetes Prevention",
            "strategies": [
                "Achieve/maintain healthy weight (lose 5-10% if overweight)",
                "Increase physical activity to 150 minutes/week",
                "Eat regular, balanced meals",
                "Monitor carbohydrate intake and choose complex carbs",
                "Stay hydrated (drink water, avoid sugary drinks)",
                "Manage stress levels",
                "Get quality sleep",
                "Consider diabetes screening every 3-6 months"
            ],
            "timeline": "Implement lifestyle changes over 8-12 weeks, reassess in 3 months"
        })
    
    # Anemia management
    if risk_assessment.get("Anemia Risk") in ["HIGH", "MODERATE"]:
        strategies.append({
            "risk_area": "Anemia Treatment & Prevention",
            "strategies": [
                "Increase iron-rich food intake",
                "Consider iron supplementation (physician-prescribed)",
                "Take iron with vitamin C for better absorption",
                "Avoid excess tea/coffee with meals",
                "Monitor hemoglobin levels monthly",
                "Address any underlying causes with physician",
                "Consider B12 testing if deficient"
            ],
            "timeline": "Begin immediately, reassess in 4-8 weeks"
        })
    
    # General wellness strategies
    strategies.append({
        "risk_area": "General Health & Wellness",
        "strategies": [
            "Stay up-to-date with vaccinations",
            "Schedule regular health check-ups (annually minimum)",
            "Maintain social connections and mental health",
            "Limit alcohol consumption",
            "Avoid smoking and secondhand smoke",
            "Maintain healthy weight",
            "Stay hydrated",
            "Get adequate sleep"
        ],
        "timeline": "Ongoing lifestyle practices"
    })
    
    return strategies
