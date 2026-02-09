def apply_contextual_adjustment(patterns, age=None, gender=None):
    """
    Model-3: Contextual Analysis
    Adjusts risk interpretation based on age and gender
    """

    def escalate_risk(current):
        if current == "Low":
            return "Moderate"
        if current == "Moderate":
            return "High"
        return "High"

    adjusted_patterns = []

    for p in patterns:
        updated_pattern = p.copy()
        original_risk = updated_pattern["risk_level"]

        # -------- AGE-BASED ADJUSTMENT --------
        if age is not None:
            if age >= 60:
                updated_pattern["risk_level"] = escalate_risk(
                    escalate_risk(updated_pattern["risk_level"])
                )
                updated_pattern["reason"] += " Risk elevated due to advanced age."
            elif age >= 45:
                updated_pattern["risk_level"] = escalate_risk(
                    updated_pattern["risk_level"]
                )
                updated_pattern["reason"] += " Risk slightly elevated due to age."

        # -------- GENDER-BASED ADJUSTMENT --------
        if gender is not None:
            gender = gender.lower()

            # Anemia more concerning in females
            if gender == "female" and "Anemia" in p["pattern"]:
                updated_pattern["risk_level"] = escalate_risk(
                    updated_pattern["risk_level"]
                )
                updated_pattern["reason"] += " Higher concern due to female gender."

            # High hemoglobin in males → dehydration / smoking risk
            if gender == "male" and "High Hemoglobin" in p["pattern"]:
                updated_pattern["reason"] += (
                    " Consider dehydration or lifestyle factors."
                )

        adjusted_patterns.append(updated_pattern)

    return adjusted_patterns
