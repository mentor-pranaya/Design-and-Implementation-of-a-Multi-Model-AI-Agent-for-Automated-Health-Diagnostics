def apply_medical_guardrails(recommendation_text):
    # 1. Verification of Disclaimer
    disclaimer = "\n\n**IMPORTANT:** This is an AI-generated health summary for educational purposes. " \
                 "It is NOT a replacement for professional medical advice, diagnosis, or treatment."
    
    if "disclaimer" not in recommendation_text.lower():
        recommendation_text += disclaimer

    # 2. Confidence Check
    # Replaces "You have [Disease]" with "Results may indicate [Condition]"
    safe_text = recommendation_text.replace("You have", "Your results are consistent with")
    safe_text = safe_text.replace("You must take", "Consider discussing with your doctor regarding")
    
    return safe_text
