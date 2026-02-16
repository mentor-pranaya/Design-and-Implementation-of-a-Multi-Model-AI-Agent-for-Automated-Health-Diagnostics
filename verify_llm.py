import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.getcwd())

async def verify_llm():
    print("--- Verifying LLM Service ---")
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    else:
        print(f"[OK] GEMINI_API_KEY found: {api_key[:5]}...")

    try:
        from src.llm import get_multi_llm_service
        service = get_multi_llm_service()
        
        info = service.get_provider_info()
        print(f"Provider Info: {info}")
        
        if not service.is_any_available():
            print("[FAIL] No LLM providers available.")
            return

        print("Testing generation...")
        try:
            # Test a simple generation
            test_params = {"Hemoglobin": {"value": 13.5, "unit": "g/dL"}}
            recommendations = service.generate_medical_recommendations(
                interpretations=["Hemoglobin is normal"],
                risks=[],
                parameters=test_params
            )
            print(f"[OK] Recommendations generated: {len(recommendations)}")
            for r in recommendations[:2]:
                print(f"  - {r}")
        except Exception as e:
             print(f"[FAIL] Generation failed: {e}")
             import traceback
             traceback.print_exc()

    except Exception as e:
        print(f"[FAIL] Import or Initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_llm())
