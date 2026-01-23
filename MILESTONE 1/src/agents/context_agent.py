import os
from groq import Groq

client = Groq(api_key="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")

def contextual_analysis_agent(interpreted_data, patterns, user_context):
    """
    Synthesizes blood data with user history and goals.
    """
    prompt = f"""
    SYSTEM ROLE: You are a Senior Clinical Health Analyst. 
    TASK: Provide a contextual interpretation of blood results.
    
    USER PROFILE:
    - Age: {user_context['age']}
    - Gender: {user_context['gender']}
    - Primary Health Goal: {user_context['goal']}
    - Relevant History: {user_context['history']}
    
    DATA FINDINGS:
    {interpreted_data}
    
    DETECTED PATTERNS:
    {patterns}
    
    INSTRUCTIONS:
    1. Focus on the user's primary goal.
    2. Explain how the abnormal values impact a person of their specific age/gender.
    3. Do NOT provide a generic summary; be specific to their context.
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="llama-3.3-70b-versatile", # Updated to a current high-performance model
        temperature=0.2 
    )
    return response.choices[0].message.content
