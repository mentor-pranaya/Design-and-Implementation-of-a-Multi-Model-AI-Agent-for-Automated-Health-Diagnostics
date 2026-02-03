import os
from groq import Groq

client = Groq(api_key=" API KEY ")

def recommendation_engine(analysis_summary, user_context):
    """
    Translates AI analysis into a personalized health plan.
    """
    prompt = f"""
    SYSTEM ROLE: You are a Personalized Health Coach & Medical Liaison.
    TASK: Generate actionable health recommendations based on AI diagnostics.

    AI ANALYSIS SUMMARY:
    {analysis_summary}

    USER GOALS: {user_context['goal']}
    USER HISTORY: {user_context['history']}

    OUTPUT STRUCTURE:
    1. Nutritional Focus (What to eat/avoid based on findings)
    2. Lifestyle/Activity (Exercises or habits related to markers)
    3. Medical Next Steps (Specific specialists to see if needed)
    4. Guardrail Disclaimer.

    STYLE: Encouraging, professional, and clear. Avoid definitive diagnostic language.
    """

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.4
    )
    return response.choices[0].message.content
