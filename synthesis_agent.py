import os
import google.generativeai as genai
import json
import re


def generate_final_health_report(model1_output, model2_output):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "❌ GEMINI_API_KEY not found. Please add it in Hugging Face secrets."

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    prompt = f"""
You are an expert AI health assistant.

You are given:
1. Model 1 output: Blood parameter analysis (Normal/High/Low)
2. Model 2 output: Risk scores and possible health conditions

Your task:
Generate a FINAL user-friendly medical report.

The report must contain:

1. Overall Health Summary (2-4 lines)
2. Top 3 Critical Findings (priority order)
3. Risk Score Dashboard (Diabetes, Cardiovascular, Kidney, Liver, Anemia)
4. Possible Conditions (not diagnosis)
5. Personalized Recommendations:
   - Diet recommendations
   - Exercise recommendations
   - Lifestyle improvements
6. Suggested Follow-up Tests (if needed)
7. Doctor Consultation Suggestions
8. Emergency Warning Signs (if any)
9. Final Disclaimer

Important:
- Use simple language.
- Do not scare the user.
- Do not claim final diagnosis.
- Output should be clean and structured.

Return output in plain text format (not JSON).

Model 1 Output:
{json.dumps(model1_output, indent=2)}

Model 2 Output:
{json.dumps(model2_output, indent=2)}
"""

    response = model.generate_content(prompt)

    return response.text.strip()
