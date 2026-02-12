
import os
import sys
from dotenv import load_dotenv

# Load env
load_dotenv()

# Add src to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import LLMService...")
    from src.llm.llm_service import LLMService
    print("Import successful.")
    
    print("Instantiating LLMService...")
    service = LLMService()
    print(f"Service instantiated. Client available: {service.client}")
    
    # Test parsing
    print("Testing parse_llm_response...")
    response = """
    Here are the recommendations:
    1. Eat healthy
    • Sleep well
    - Exercise
    * Drink water
    """
    recs = service._parse_llm_response(response)
    print(f"Parsed {len(recs)} recommendations.")
    for r in recs:
        print(f" - {r}")
        
    print("SUCCESS: LLMService seems functional.")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
