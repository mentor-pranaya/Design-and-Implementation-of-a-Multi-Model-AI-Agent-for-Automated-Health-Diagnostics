import os
import google.generativeai as genai
import json
import re


def gemini_risk_analysis(extracted_report):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {"error": "❌ GEMINI_API_KEY not found. Please add it in Hugging Face Secrets."}

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    prompt = f"""
You are an expert medical diagnostic assistant AI.

You are given blood report results with tested values and their reference ranges.

Your tasks:
1. Identify abnormal parameters.
2. Detect patterns suggesting health risks.
3. Generate risk scores (0 to 100) for:
   - Diabetes Risk Score
   - Cardiovascular Risk Score
   - Kidney Risk Score
   - Liver Risk Score
   - Anemia Risk Score

Rules:
- Score must be numeric (0-100).
- Higher score means higher risk.
- Provide short explanation for each score.

Return output strictly in VALID JSON only.
Do not wrap the JSON inside ```json ```.

JSON format must be:

{{
  "abnormal_findings": [
    {{"parameter":"Glucose","status":"High","value":145,"reference":"70-99"}}
  ],
  "risk_scores": {{
    "diabetes": {{"score": 75, "level": "High", "reason": "Glucose is high"}}
  }},
  "recommendations": [
    "Reduce sugar intake"
  ],
  "doctor_suggestion": [
    "General Physician"
  ],
  "disclaimer": "This is AI-based analysis, not a medical diagnosis."
}}

Blood Report Data:
{json.dumps(extracted_report, indent=2)}
"""

    response = model.generate_content(prompt)

    raw_text = response.text.strip()

    # -------- CLEAN JSON WRAPPERS --------
    # Remove ```json and ``` if Gemini adds them
    raw_text = re.sub(r"^```json", "", raw_text, flags=re.IGNORECASE).strip()
    raw_text = re.sub(r"^```", "", raw_text).strip()
    raw_text = re.sub(r"```$", "", raw_text).strip()

    try:
        return json.loads(raw_text)

    except Exception:
        return {
            "error": "Gemini response was not valid JSON",
            "raw_response": response.text
        }
