#!/usr/bin/env python3
"""
Test script to check LLM provider availability and basic functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm.multi_llm_service import get_multi_llm_service

def test_llm_providers():
    """Test LLM providers."""
    print("Testing LLM Providers...")
    print("=" * 50)

    # Get the multi-LLM service
    service = get_multi_llm_service()

    # Check provider info
    info = service.get_provider_info()
    print(f"Primary Provider: {info['primary']}")
    print(f"Available Providers: {info['available']}")
    print(f"Total Available: {info['total_available']}")
    print(f"All Configured: {info['all_configured']}")
    print()

    # Test basic text generation
    if service.is_any_available():
        print("Testing basic text generation...")
        test_prompt = "Hello, can you respond with a simple greeting?"
        response = service.generate_text(test_prompt, max_tokens=100)
        if response:
            print(f"✓ Response: {response[:100]}...")
        else:
            print("✗ No response from any provider")
    else:
        print("✗ No LLM providers available")

    print("\nTest completed.")

if __name__ == "__main__":
    test_llm_providers()
