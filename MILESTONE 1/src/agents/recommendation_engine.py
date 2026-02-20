from groq import Groq
import streamlit as st

api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)
def recommendation_engine(analysis_summary, user_context=None):
    """
    Generates personalized health recommendations from AI analysis.
    """

    if not api_key:
        return "⚠️ Groq API Key missing. Set GROQ_API_KEY in environment variables."

    user_context = user_context or {}

    goal = user_context.get("goal", "General Wellness")
    history = user_context.get("history", "None reported")

    # ---- System Instructions ----
    system_prompt = (
        "You are a clinical health recommendation assistant. "
        "Provide actionable lifestyle and nutrition guidance. "
        "Avoid diagnosis. Include safety disclaimer."
    )

    # ---- User Prompt ----
    user_prompt = f"""
AI ANALYSIS SUMMARY:
{analysis_summary}

USER GOAL: {goal}
USER HISTORY: {history}

Generate structured recommendations:

1. Nutritional Focus (diet suggestions)
2. Lifestyle & Activity (exercise, habits)
3. Medical Next Steps (which specialist to consult)
4. Safety Disclaimer (non-diagnostic)
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=600
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Recommendation AI Error: {str(e)}"
