import streamlit as st
from groq import Groq

# --- SECURITY: Use Streamlit Secrets --
# Never hardcode API keys. In Streamlit, use st.secrets.
api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def contextual_analysis_agent(interpreted_data=None, patterns=None, user_context=None):
    """
    Uses Groq LLM to analyze lab results with user context.
    """

    if not api_key:
        return "⚠️ GROQ API Key missing. Add it to Streamlit secrets or environment variables."

    interpreted_data = interpreted_data or []
    patterns = patterns or []
    user_context = user_context or {}

    # -------- Format Lab Data --------
    data_bullets = "\n".join([
        f"- {i.get('parameter','Unknown')}: {i.get('value','?')} {i.get('unit','')} (Status: {i.get('status','Unknown')})"
        for i in interpreted_data
    ]) or "No lab data extracted."

    # -------- Format Pattern Data --------
    pattern_bullets = "\n".join([
        f"- {p.get('pattern','Unknown')}: {p.get('finding','')} (Severity: {p.get('severity','Normal')})"
        for p in patterns
    ]) or "No clinical patterns detected."

    # -------- System Role --------
    system_role = (
        "You are a clinical decision support assistant. "
        "Provide concise, factual, non-diagnostic medical insights."
    )

    # -------- User Prompt --------
    user_prompt = f"""
USER PROFILE:
Age: {user_context.get('age','Unknown')}
Gender: {user_context.get('gender','Unknown')}
Goal: {user_context.get('goal','General Wellness')}
History: {user_context.get('history','None')}

LAB RESULTS:
{data_bullets}

CLINICAL PATTERNS:
{pattern_bullets}

TASK:
- Explain clinical significance.
- Relate findings to user goal.
- Avoid disclaimers and generic intros.
- Be concise and clinical.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # safer model
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ AI Error: {str(e)}"
