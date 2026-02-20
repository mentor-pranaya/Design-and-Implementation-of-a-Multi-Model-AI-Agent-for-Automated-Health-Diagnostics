import re

def apply_guardrails(ai_response):
    """
    Post-processes AI responses to ensure safety, removes diagnostic language,
    and appends mandatory medical disclaimers.
    """
    # 1. Phrases to soften (Definitive to Suggestive)
    substitutions = {
        r"You have": "Your results suggest",
        r"You are suffering from": "Your markers indicate potential",
        r"We diagnose you with": "These patterns are consistent with",
        r"This is a clear sign of": "This may be an indicator of",
        r"Cure for": "Support for"
    }

    processed_text = ai_response
    for pattern, replacement in substitutions.items():
        processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE)

    # 2. Mandatory Medical Disclaimer
    disclaimer = (
        "\n\n---\n"
        "**⚠️ MEDICAL DISCLAIMER:** This AI-generated analysis is for informational purposes only "
        "and does not constitute medical advice, diagnosis, or treatment. Always seek the advice "
        "of your physician or other qualified health provider with any questions regarding a "
        "medical condition. Never disregard professional medical advice because of something "
        "you have read in this report."
    )

    # 3. Check for high-severity keywords to add an urgent note
    urgent_keywords = ["critical", "emergency", "severe", "immediate"]
    if any(word in processed_text.lower() for word in urgent_keywords):
        processed_text = "🚨 **Note: Some markers require prompt medical review.**\n\n" + processed_text

    return processed_text + disclaimer

def is_medical_query(text):
    """
    Validates if the input text is actually related to blood reports 
    to prevent the LLM from answering off-topic questions.
    """
    medical_terms = ["blood", "glucose", "hemoglobin", "test", "level", "range", "mg/dl", "mmol/l"]
    return any(term in text.lower() for term in medical_terms)
