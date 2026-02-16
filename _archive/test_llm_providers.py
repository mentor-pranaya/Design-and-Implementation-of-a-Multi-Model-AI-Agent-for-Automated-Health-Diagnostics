#!/usr/bin/env python3
"""
Test script to check LLM provider availability and basic functionality.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm.multi_llm_service import get_multi_llm_service

def test_llm_providers():
    """Test LLM providers."""
    print("=" * 60)
    print("Testing LLM Providers...")
    print("=" * 60)

    # Get the multi-LLM service
    service = get_multi_llm_service()

    # Check provider info
    info = service.get_provider_info()
    print(f"Primary Provider: {info['primary']}")
    print(f"Available Providers: {info['available']}")
    print(f"Total Available: {info['total_available']}")
    print(f"All Configured: {info['all_configured']}")
    print("-" * 60)

    # Test basic text generation
    if service.is_any_available():
        print("Testing basic text generation...")
        test_prompt = "Hello, can you respond with a simple greeting?"
        try:
            response = service.generate_text(test_prompt, max_tokens=100)
            if response:
                print(f"✓ Response received ({len(response)} chars)")
                print(f"  Preview: {response[:100]}...")
            else:
                print("✗ No response from any provider")
        except Exception as e:
            print(f"✗ Error during text generation: {e}")
    else:
        print("✗ No LLM providers available")

    print("-" * 60)
    print("Test completed.")
    print("=" * 60)

if __name__ == "__main__":
    test_llm_providers()
