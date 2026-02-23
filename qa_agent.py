import os
import google.generativeai as genai
import json


def ask_question_about_report(model1_data, model2_data, final_report, user_profile, question):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "❌ GEMINI_API_KEY not found in Hugging Face secrets."

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    prompt = f"""
You are a healthcare assistant AI.

You are given:
1. Blood report analysis (Model 1)
2. Risk score analysis (Model 2)
3. Final synthesized report (Model 3)
4. User profile (age, gender, lifestyle, symptoms)

Your task:
Answer the user's question based on these inputs.

Important Rules:
- Provide personalized explanation based on age and gender.
- Do not claim final diagnosis.
- Be supportive and clear.
- Provide actionable advice.
- Mention when to consult a doctor if risk is high.
- Avoid scary language.

User Profile:
{json.dumps(user_profile, indent=2)}

Blood Report Data (Model 1):
{json.dumps(model1_data, indent=2)}

Risk Assessment (Model 2):
{json.dumps(model2_data, indent=2)}

Final Health Report (Model 3):
{final_report}

User Question:
{question}

Answer in a friendly and helpful tone.
"""

    response = model.generate_content(prompt)

    return response.text.strip()
