#!/usr/bin/env python3
"""
Test script for Intent Inference Agent functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.intent_inference_agent import IntentInferenceAgent, ConversationContext

async def test_intent_inference():
    """Test the intent inference agent with various inputs."""
    print("🧪 Testing Intent Inference Agent")
    print("=" * 50)

    agent = IntentInferenceAgent()

    # Test cases
    test_cases = [
        "I want to analyze my blood report",
        "What's normal cholesterol level?",
        "I'm feeling tired all the time, what could be wrong?",
        "Can you help me understand my lab results?",
        "I have high blood pressure, what should I do?",
        "Tell me about diabetes symptoms",
        "Upload my test results please",
        "I'm worried about my health",
        "Give me some health advice",
        "What does this blood test mean?"
    ]

    conversation_context = ConversationContext()

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: '{user_input}'")
        print("-" * 40)

        try:
            intent_result = await agent.analyze_intent(user_input, conversation_context)

            print(f"🎯 Inferred Intent: {intent_result.inferred_intent}")
            print(f"📊 Confidence Score: {intent_result.confidence_score:.2f}")
            print(f"❓ Requires Clarification: {intent_result.requires_clarification}")

            if intent_result.clarifying_questions:
                print("❓ Clarifying Questions:")
                for q in intent_result.clarifying_questions:
                    print(f"   • {q}")

            if intent_result.assumptions_made:
                print("🤔 Assumptions Made:")
                for assumption in intent_result.assumptions_made:
                    print(f"   • {assumption}")

            # Update context for next interaction
            conversation_context = agent.update_conversation_context(
                conversation_context, user_input, intent_result
            )

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 50)
    print("✅ Intent Inference Testing Complete")

if __name__ == "__main__":
    asyncio.run(test_intent_inference())
