from src.llm.llm_service import LLMService

def generate_recommendations(interpretation: list, risks: list):
    """
    Generate lifestyle recommendations and medical advice based on findings and risks using LLM.
    """
    llm_service = LLMService()
    parameters = {}  # No parameters provided in current function signature
    patient_context = None

    # Try to get recommendations from LLM
    llm_recommendations = llm_service.generate_medical_recommendations(
        interpretations=interpretation,
        risks=risks,
        parameters=parameters,
        patient_context=patient_context
    )

    if llm_recommendations:
        return llm_recommendations

    # Fallback to hardcoded recommendations if LLM fails
    recommendations = []

    # Convert to lowercase for easier matching
    all_findings = [f.lower() for f in interpretation + risks]

    # Anemia recommendations
    if any("anemia" in finding or "low hemoglobin" in finding for finding in all_findings):
        recommendations.extend([
            "Increase iron-rich foods: spinach, lentils, red meat",
            "Consider vitamin C rich foods to enhance iron absorption",
            "Consult doctor for iron supplements if needed",
            "Regular blood tests to monitor hemoglobin levels"
        ])

    # Diabetes recommendations
    if any("diabetes" in finding or "glucose" in finding or "hba1c" in finding for finding in all_findings):
        recommendations.extend([
            "Follow low glycemic index diet",
            "Regular physical exercise (30 minutes daily)",
            "Monitor blood sugar levels regularly",
            "Consult endocrinologist for diabetes management",
            "Weight management if BMI > 25"
        ])

    # Liver issues
    if any("liver" in finding or "alt" in finding or "ast" in finding or "bilirubin" in finding for finding in all_findings):
        recommendations.extend([
            "Avoid alcohol consumption",
            "Follow liver-friendly diet: avoid fried foods, processed meats",
            "Stay hydrated and maintain healthy weight",
            "Consult hepatologist for liver function evaluation"
        ])

    # Kidney issues
    if any("kidney" in finding or "creatinine" in finding or "urea" in finding for finding in all_findings):
        recommendations.extend([
            "Reduce salt intake (<2g sodium daily)",
            "Stay well hydrated (2-3 liters water daily)",
            "Limit protein intake if advised by doctor",
            "Regular monitoring of kidney function",
            "Consult nephrologist for kidney health"
        ])

    # Cardiovascular risk
    if any("cholesterol" in finding or "cardiovascular" in finding or "ldl" in finding for finding in all_findings):
        recommendations.extend([
            "Heart-healthy diet: Mediterranean diet recommended",
            "Reduce saturated fats and trans fats",
            "Increase omega-3 rich foods: fish, nuts, seeds",
            "Regular cardiovascular exercise",
            "Quit smoking if applicable",
            "Consult cardiologist for heart health assessment"
        ])

    # Thyroid issues
    if any("thyroid" in finding or "tsh" in finding for finding in all_findings):
        recommendations.extend([
            "Iodine-rich diet for thyroid health",
            "Regular thyroid function monitoring",
            "Consult endocrinologist for thyroid management",
            "Medication adherence if prescribed"
        ])

    # Electrolyte imbalances
    if any("sodium" in finding or "potassium" in finding or "electrolyte" in finding for finding in all_findings):
        recommendations.extend([
            "Balanced diet with adequate fruits and vegetables",
            "Monitor salt intake carefully",
            "Stay hydrated appropriately",
            "Consult doctor before making dietary changes"
        ])

    # Vitamin deficiencies
    if any("vitamin" in finding or "iron" in finding for finding in all_findings):
        recommendations.extend([
            "Include variety of colorful vegetables and fruits",
            "Consider multivitamin supplements after medical consultation",
            "Regular nutrient level monitoring"
        ])

    # Infection/Inflammation
    if any("infection" in finding or "wbc" in finding for finding in all_findings):
        recommendations.extend([
            "Maintain good hygiene practices",
            "Adequate rest and sleep",
            "Balanced nutrition to support immune system",
            "Seek medical attention if symptoms worsen"
        ])

    # General recommendations
    recommendations.extend([
        "Schedule regular health check-ups",
        "Maintain healthy lifestyle: balanced diet, exercise, stress management",
        "Keep medical records organized",
        "Inform healthcare providers about all medications and supplements"
    ])

    return list(set(recommendations))  # Remove duplicates

def generate_prescriptions(interpretation: list, risks: list, parameters: dict):
    """
    Generate natural remedy suggestions based on findings.
    IMPORTANT: These are natural remedy suggestions only - always consult healthcare professionals.
    """
    prescriptions = []

    all_findings = [f.lower() for f in interpretation + risks]

    # Anemia natural remedies
    if any("anemia" in finding or "low hemoglobin" in finding for finding in all_findings):
        prescriptions.extend([
            "🍎 Iron-rich foods: Spinach, lentils, red meat, pumpkin seeds",
            "🍊 Vitamin C foods: Citrus fruits, bell peppers to enhance iron absorption",
            "🥬 Leafy greens: Kale, Swiss chard, beet greens for natural iron",
            "🌰 Nuts and seeds: Almonds, sesame seeds, sunflower seeds",
            "🍇 Dried fruits: Raisins, apricots, prunes for natural iron boost"
        ])

    # Diabetes natural remedies (Based on recent clinical studies)
    if any("diabetes" in finding or "glucose" in finding or "hba1c" in finding for finding in all_findings):
        prescriptions.extend([
            "🌿 Ceylon cinnamon: 1/2 teaspoon daily (2023 studies show 10-15% glucose reduction)",
            "🥬 Bitter melon: 50-100g daily (clinical trials show HbA1c reduction)",
            "🫘 Fenugreek seeds: 5-10g soaked overnight (meta-analysis shows blood sugar benefits)",
            "🍃 Gymnema sylvestre: 300-400mg daily (traditional + modern research validated)",
            "🫚 Ginger tea: 2g daily (recent studies show improved insulin sensitivity)",
            "🧄 Garlic: 600-1200mg daily (research shows blood sugar regulation benefits)"
        ])

    # Liver issues natural remedies
    if any("liver" in finding or "alt" in finding or "ast" in finding or "bilirubin" in finding for finding in all_findings):
        prescriptions.extend([
            "🫒 Olive oil: Cold-pressed for liver health",
            "🌱 Milk thistle: Traditional liver support herb",
            "🍋 Lemon water: Natural detoxifier for liver",
            "🫚 Turmeric: Anti-inflammatory for liver health",
            "🥕 Beetroot juice: Natural liver cleanser"
        ])

    # Kidney issues natural remedies (Based on nephrology research)
    if any("kidney" in finding or "creatinine" in finding or "urea" in finding for finding in all_findings):
        prescriptions.extend([
            "🥒 Cucumber: 1-2 daily (natural diuretic, supports kidney filtration)",
            "🍇 Unsweetened cranberry juice: 200ml daily (proanthocyanidins prevent UTIs)",
            "🌿 Dandelion root tea: 1 cup daily (natural diuretic, consult doctor first)",
            "🍍 Pineapple: 100g daily (bromelain reduces inflammation)",
            "🥕 Carrot juice: 200ml daily (beta-carotene supports kidney antioxidant defense)",
            "🫐 Blueberries: 1 cup daily (anthocyanins protect kidney cells)"
        ])

    # Cardiovascular risk natural remedies (Based on recent clinical research)
    if any("cholesterol" in finding.lower() or "cardiovascular" in finding.lower() or "ldl" in finding.lower() or "hdl" in finding.lower() for finding in all_findings):
        prescriptions.extend([
            "🫒 Mediterranean diet: 2024 studies show 30% reduced heart disease risk",
            "🧄 Aged garlic extract: 600-1200mg daily (meta-analysis shows LDL reduction)",
            "🫚 Ginger: 2g daily (research shows improved circulation and blood pressure)",
            "🌰 Almonds: 30g daily (clinical trials show LDL cholesterol reduction)",
            "🍎 Apples: 1-2 daily (pectin fiber reduces cholesterol absorption)",
            "🫐 Berries: Rich in anthocyanins for heart protection (blueberries, strawberries)"
        ])

    # Thyroid issues natural remedies (Based on endocrinology research)
    if any("thyroid" in finding or "tsh" in finding for finding in all_findings):
        prescriptions.extend([
            "🌰 Brazil nuts: 1-2 daily (selenium supports thyroid hormone conversion)",
            "🫚 Ginger tea: 2 cups daily (research shows anti-inflammatory thyroid benefits)",
            "🥑 Avocados: 1/2 daily (healthy fats support thyroid hormone production)",
            "🥕 Sweet potatoes: Rich in beta-carotene (supports thyroid hormone synthesis)",
            "🌿 Ashwagandha: 600mg daily (2023 studies show TSH normalization in hypothyroidism)",
            "🧄 Garlic: 600mg daily (contains allicin for thyroid support)"
        ])

    # Electrolyte imbalances natural remedies
    if any("sodium" in finding or "potassium" in finding or "electrolyte" in finding for finding in all_findings):
        prescriptions.extend([
            "🍌 Bananas: Rich in potassium for electrolyte balance",
            "🥥 Coconut water: Natural electrolyte replenisher",
            "🍊 Oranges: Potassium and magnesium source",
            "🥬 Leafy greens: Magnesium and potassium rich",
            "🥜 Nuts: Magnesium and potassium sources"
        ])

    # Vitamin deficiencies natural remedies
    if any("vitamin" in finding or "iron" in finding for finding in all_findings):
        prescriptions.extend([
            "🍊 Citrus fruits: Vitamin C for iron absorption",
            "🥕 Carrots: Beta-carotene (vitamin A precursor)",
            "🍅 Tomatoes: Lycopene and vitamin C",
            "🥬 Dark leafy greens: Multiple vitamins and minerals",
            "🌰 Sunflower seeds: Vitamin E and minerals"
        ])

    # Infection/Inflammation natural remedies
    if any("infection" in finding or "wbc" in finding for finding in all_findings):
        prescriptions.extend([
            "🫚 Ginger tea: Natural anti-inflammatory",
            "🧄 Raw garlic: Natural antibiotic properties",
            "🍯 Manuka honey: Natural antibacterial",
            "🫚 Turmeric: Powerful anti-inflammatory",
            "🍋 Lemon water: Immune system booster"
        ])

    # General natural remedies
    prescriptions.extend([
        "🫚 Warm lemon water: Morning detox drink",
        "🌱 Green tea: Antioxidant-rich daily drink",
        "🍯 Honey and cinnamon: Natural health tonic",
        "🥥 Virgin coconut oil: Healthy fat source",
        "🫒 Extra virgin olive oil: Anti-inflammatory oil"
    ])

    # Add prescription suggestions based on common medical practices
    prescription_suggestions = []

    # Anemia prescription suggestions
    if any("anemia" in finding or "low hemoglobin" in finding for finding in all_findings):
        prescription_suggestions.extend([
            "💊 Ferrous sulfate 325mg daily (standard iron supplement for iron deficiency anemia)",
            "💊 Ferrous gluconate 300mg twice daily (gentler on stomach than ferrous sulfate)",
            "💊 Vitamin B12 injections if pernicious anemia suspected (1000mcg monthly)",
            "💊 Folic acid 1mg daily if folate deficiency confirmed"
        ])

    # Diabetes prescription suggestions
    if any("diabetes" in finding or "glucose" in finding or "hba1c" in finding for finding in all_findings):
        prescription_suggestions.extend([
            "💊 Metformin 500mg twice daily (first-line treatment for type 2 diabetes)",
            "💊 Glipizide 5mg daily (sulfonylurea for blood sugar control)",
            "💊 Sitagliptin 100mg daily (DPP-4 inhibitor for glycemic control)",
            "💊 Insulin glargine (long-acting insulin for type 1 or advanced type 2 diabetes)"
        ])

    # Cardiovascular prescription suggestions
    if any("cholesterol" in finding or "cardiovascular" in finding or "ldl" in finding or "hdl" in finding for finding in all_findings):
        prescription_suggestions.extend([
            "💊 Atorvastatin 20mg daily (statin for LDL cholesterol reduction)",
            "💊 Rosuvastatin 10mg daily (potent statin for high cholesterol)",
            "💊 Ezetimibe 10mg daily (cholesterol absorption inhibitor)",
            "💊 Aspirin 81mg daily (antiplatelet therapy for cardiovascular protection)"
        ])

    # Thyroid prescription suggestions
    if any("thyroid" in finding or "tsh" in finding for finding in all_findings):
        prescription_suggestions.extend([
            "💊 Levothyroxine 25-100mcg daily (thyroid hormone replacement for hypothyroidism)",
            "💊 Liothyronine 5mcg daily (T3 thyroid hormone if needed)",
            "💊 Methimazole 5-10mg daily (for hyperthyroidism treatment)",
            "💊 Propranolol 10mg as needed (for thyroid-related rapid heartbeat)"
        ])

    # Liver issues prescription suggestions
    if any("liver" in finding or "alt" in finding or "ast" in finding or "bilirubin" in finding for finding in all_findings):
        prescription_suggestions.extend([
            "💊 Ursodeoxycholic acid 300mg twice daily (for cholestasis and liver protection)",
            "💊 Silymarin 150mg twice daily (milk thistle extract for liver support)",
            "💊 Vitamin E 400 IU daily (antioxidant for liver protection)",
            "💊 N-acetylcysteine 600mg twice daily (for acetaminophen overdose or liver support)"
        ])

    # Kidney issues prescription suggestions
    if any("kidney" in finding or "creatinine" in finding or "urea" in finding for finding in all_findings):
        prescription_suggestions.extend([
            "💊 Losartan 25mg daily (ACE inhibitor for kidney protection)",
            "💊 Amlodipine 5mg daily (calcium channel blocker for blood pressure control)",
            "💊 Furosemide 20mg daily (diuretic for fluid retention)",
            "💊 Calcium acetate 667mg with meals (phosphate binder for kidney disease)"
        ])

    # Add prescription section if there are suggestions
    if prescription_suggestions:
        prescriptions.append("")
        prescriptions.append("💊 PRESCRIPTION SUGGESTIONS (For Healthcare Professional Review Only):")
        prescriptions.extend(prescription_suggestions)

    # Disclaimer
    prescriptions.insert(0, "🌿 Natural Remedies by INBLOODO AGENT: These are AI-suggested natural remedies. Always consult with a qualified healthcare professional before starting any treatment.")
    prescriptions.insert(1, "⚠️ IMPORTANT: The prescription suggestions below are for informational purposes only and must be prescribed by a licensed healthcare professional after proper diagnosis.")

    return prescriptions
