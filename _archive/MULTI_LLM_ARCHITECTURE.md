"""
Multi-LLM System Architecture - Quick Reference

Usage:
------
from src.llm.multi_llm_service import get_multi_llm_service

# Get the multi-LLM service
llm_service = get_multi_llm_service()

# Check available providers
print(f"Available: {llm_service.get_available_providers()}")
print(f"Primary: {llm_service.get_provider_info()['primary']}")

# Generate recommendations with automatic fallback
recommendations = llm_service.generate_medical_recommendations(
    interpretations=["Low hemoglobin"],
    risks=["Possible anemia"],
    parameters={"hemoglobin": 9.5},
    patient_context=None,
    preferred_provider=None  # Auto-select primary, fallback if fails
)

# Generate custom text with automatic fallback
response = llm_service.generate_text(
    prompt="Please summarize the blood test issues...",
    preferred_provider="openai"  # Try OpenAI first
)

Fallback Chain:
---------------
Preferred Provider (if specified)
    ↓
Primary Provider (from LLM_PROVIDER env)
    ↓
Available Fallback 1
    ↓
Available Fallback 2
    ↓
Available Fallback 3
    ↓
Empty List / Hardcoded Fallback

Configuration:
---------------
.env file:
    LLM_PROVIDER=gemini              # Primary
    GEMINI_API_KEY=...               # Gemini provider
    OPENAI_API_KEY=...               # OpenAI provider (fallback)
    ANTHROPIC_API_KEY=...            # Claude provider (fallback)

Files:
------
src/llm/
    ├── llm_provider.py              # Abstract base class
    ├── gemini_provider.py           # Google Gemini implementation
    ├── openai_provider.py           # OpenAI GPT implementation
    ├── claude_provider.py           # Anthropic Claude implementation
    ├── multi_llm_service.py         # Multi-provider orchestrator
    └── __init__.py                  # Module exports

Integration Points:
-------------------
Agent Orchestrator
    └── LLMRecommendationAgent
        └── MultiLLMService
            └── [Gemini | OpenAI | Claude]

JSON Response Includes:
-----------------------
{
  "agent_execution": {
    "agents": [
      {
        "name": "LLM Recommendation Agent",
        "status": "success",  # Or "failed"
        "execution_time": 2.34
      }
    ]
  }
}

Environment Variables:
----------------------
Primary Provider Selection:
    LLM_PROVIDER=gemini  # gemini, openai, or claude

API Keys (add as needed):
    GEMINI_API_KEY=...
    OPENAI_API_KEY=...
    ANTHROPIC_API_KEY=...

Error Handling:
---------------
✓ If primary provider fails → automatically tries fallbacks
✓ If all providers fail → returns empty list (triggers hardcoded fallback)
✓ All errors are logged with provider names
✓ No exceptions thrown - graceful degradation

Performance:
------------
Gemini: ~1-2s per request
OpenAI: ~2-3s per request  
Claude: ~1-2s per request
Fallback: ~0.1s (hardcoded)

Testing:
--------
# Test if providers are available:
python -c "from src.llm import get_multi_llm_service; s = get_multi_llm_service(); print(s.get_provider_info())"

# Output:
# {'primary': 'Google Gemini', 'available': ['Google Gemini'], 'total_available': 1, 'fallback_enabled': True}
"""
