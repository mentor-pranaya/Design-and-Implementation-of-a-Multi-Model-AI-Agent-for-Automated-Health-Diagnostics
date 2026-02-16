"""
Multi-LLM Service - Manages multiple LLM providers with fallback mechanism.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from src.llm.gemini_provider import GeminiLLMProvider
from src.llm.openai_provider import OpenAILLMProvider
from src.llm.claude_provider import ClaudeLLMProvider

logger = logging.getLogger(__name__)


class MultiLLMService:
    """
    Service that manages multiple LLM providers with intelligent fallback.
    
    Priority order (configurable):
    1. Primary LLM (from environment variable LLM_PROVIDER)
    2. Secondary LLMs in fallback order
    3. Hardcoded recommendations if all LLMs fail
    """
    
    def __init__(self):
        self.providers = {}
        self.available_providers = []
        self.primary_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available LLM providers."""
        logger.info("Initializing Multi-LLM Service...")

        # Initialize all providers
        providers_to_init = [
            ("gemini", GeminiLLMProvider()),
            ("openai", OpenAILLMProvider()),
            ("claude", ClaudeLLMProvider()),
        ]

        for provider_name, provider in providers_to_init:
            self.providers[provider_name] = provider
            if provider.is_available():
                self.available_providers.append((provider_name, provider))
                logger.info(f"✓ {provider.name} is available")
            else:
                logger.warning(f"✗ {provider.name} is not available")

        # Log summary
        if self.available_providers:
            logger.info(f"Multi-LLM Service initialized with {len(self.available_providers)} providers")
        else:
            logger.warning("No LLM providers available - recommendations will use fallback logic")
        
        # Set primary provider from environment
        primary = os.getenv("LLM_PROVIDER", "gemini").lower()
        if primary in self.providers and self.providers[primary].is_available():
            self.primary_provider = (primary, self.providers[primary])
            logger.info(f"Primary LLM Provider: {self.providers[primary].name}")
        elif self.available_providers:
            self.primary_provider = self.available_providers[0]
            logger.info(f"Primary LLM Provider: {self.primary_provider[1].name} (auto-selected)")
        else:
            logger.warning("No LLM providers available! Using fallback recommendations only.")
    
    def is_any_available(self) -> bool:
        """Check if any LLM provider is available."""
        return len(self.available_providers) > 0
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [name for name, _ in self.available_providers]
    
    def generate_medical_recommendations(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None,
        preferred_provider: Optional[str] = None
    ) -> List[str]:
        """
        Generate medical recommendations with intelligent fallback.
        
        Args:
            interpretations: List of parameter interpretations
            risks: List of identified health risks
            parameters: Dictionary of medical parameters
            patient_context: Optional patient information
            preferred_provider: Optional provider name to use (if available)
        
        Returns:
            List of recommendations from the first available LLM
        """
        
        # Try preferred provider if specified
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if provider.is_available():
                logger.info(f"Using preferred LLM provider: {provider.name}")
                return provider.generate_recommendations(
                    interpretations, risks, parameters, patient_context
                )
        
        # Try primary provider
        if self.primary_provider:
            name, provider = self.primary_provider
            logger.info(f"Using primary LLM provider: {provider.name}")
            recommendations = provider.generate_recommendations(
                interpretations, risks, parameters, patient_context
            )
            if recommendations:
                return recommendations
        
        # Try fallback providers
        for provider_name, provider in self.available_providers:
            if self.primary_provider and provider_name == self.primary_provider[0]:
                continue  # Skip if already tried
            
            logger.info(f"Trying fallback LLM provider: {provider.name}")
            recommendations = provider.generate_recommendations(
                interpretations, risks, parameters, patient_context
            )
            if recommendations:
                return recommendations
        
        # All LLMs failed or unavailable
        logger.warning("All LLM providers failed or unavailable, using hardcoded fallback")
        return self._generate_fallback_recommendations(interpretations, risks, parameters)

    def _generate_fallback_recommendations(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any]
    ) -> List[str]:
        """Generate fallback recommendations when LLMs are unavailable."""
        recommendations = []

        # Basic recommendations based on common parameters
        if any("high" in interp.lower() or "elevated" in interp.lower() for interp in interpretations):
            recommendations.extend([
                "1. 🩺 Consult with a healthcare professional for detailed evaluation",
                "2. 📊 Monitor your health parameters regularly",
                "3. 🥗 Consider dietary modifications based on your specific condition"
            ])

        if any("low" in interp.lower() or "decreased" in interp.lower() for interp in interpretations):
            recommendations.extend([
                "1. 🩺 Seek medical advice for low parameter values",
                "2. 📊 Regular monitoring is essential",
                "3. 💊 Discuss supplementation needs with your doctor"
            ])

        # Risk-based recommendations
        if risks:
            recommendations.append("4. ⚠️ Address identified health risks promptly")

        # General recommendations
        recommendations.extend([
            "5. 🏃‍♂️ Maintain regular physical activity",
            "6. 🥦 Focus on balanced nutrition",
            "7. 💧 Stay hydrated",
            "8. 😴 Ensure adequate sleep and stress management"
        ])

        return recommendations[:8]  # Limit to 8 recommendations

    def generate_intent_analysis(
        self,
        user_input: str,
        context_summary: str,
        preferred_provider: Optional[str] = None
    ) -> str:
        """
        Generate intent analysis using LLM with specialized prompt.

        Args:
            user_input: The user's natural language input
            context_summary: Summary of conversation context
            preferred_provider: Optional provider name to use

        Returns:
            JSON response with intent analysis
        """
        prompt = f"""
You are an expert intent inference agent for a health diagnostics AI system. Your task is to analyze the user's input and determine their true intent, even if the request is vague, implicit, or incomplete.

CONTEXT INFORMATION:
{context_summary}

USER INPUT: "{user_input}"

INTENT CATEGORIES (choose the most appropriate):
- analyze_blood_report: User wants to analyze/upload blood test results
- ask_health_question: General health-related question
- request_recommendations: Seeking health advice or recommendations
- follow_up_previous_analysis: Referring to previous blood report analysis
- clarify_previous_response: Needs clarification on previous AI response
- general_health_inquiry: Broad health information request
- emergency_concern: Urgent health concern that needs immediate attention
- lifestyle_advice: Questions about diet, exercise, lifestyle changes

ANALYSIS REQUIREMENTS:
1. Infer the most likely intent from the categories above
2. Provide a confidence score (0.0-1.0) for your inference
3. Determine if clarification is needed (yes/no)
4. If clarification needed, list 1-3 specific questions to ask
5. List any reasonable assumptions you're making
6. Provide a brief summary of the context you considered

RESPONSE FORMAT (JSON):
{{
    "inferred_intent": "category_name",
    "confidence_score": 0.85,
    "requires_clarification": false,
    "clarifying_questions": [],
    "assumptions_made": ["Assumption 1", "Assumption 2"],
    "context_summary": "Brief summary of context analysis"
}}

Be thorough but concise. If the intent is unclear, prefer to ask for clarification rather than guessing.
"""

        return self.generate_text(prompt, max_tokens=1024, preferred_provider=preferred_provider)

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2048,
        preferred_provider: Optional[str] = None
    ) -> str:
        """
        Generate text response with intelligent fallback.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in response
            preferred_provider: Optional provider name to use
        
        Returns:
            Generated text response
        """
        
        # Try preferred provider
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if provider.is_available():
                logger.info(f"Using preferred LLM provider: {provider.name}")
                return provider.generate_text(prompt, max_tokens)
        
        # Try primary provider
        if self.primary_provider:
            name, provider = self.primary_provider
            logger.info(f"Using primary LLM provider: {provider.name}")
            text = provider.generate_text(prompt, max_tokens)
            if text:
                return text
        
        # Try fallback providers
        for provider_name, provider in self.available_providers:
            if self.primary_provider and provider_name == self.primary_provider[0]:
                continue  # Skip if already tried
            
            logger.info(f"Trying fallback LLM provider: {provider.name}")
            text = provider.generate_text(prompt, max_tokens)
            if text:
                return text
        
        logger.warning("All LLM providers failed")
        return ""
    
    def extract_parameters_from_llm(self, text: str) -> Dict[str, Any]:
        """
        Extract parameters using LLM when regex fails.
        """
        # Try primary provider
        if self.primary_provider:
            _, provider = self.primary_provider
            if hasattr(provider, 'extract_parameters'):
                logger.info(f"Using {provider.name} for parameter extraction")
                return provider.extract_parameters(text)
        
        # Try fallback providers
        for _, provider in self.available_providers:
            if hasattr(provider, 'extract_parameters'):
                logger.info(f"Using {provider.name} for parameter extraction (fallback)")
                return provider.extract_parameters(text)
                
        return {}

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about configured LLM providers."""
        return {
            "primary": self.primary_provider[1].name if self.primary_provider else None,
            "available": [p.name for _, p in self.available_providers],
            "total_available": len(self.available_providers),
            "all_configured": list(self.providers.keys()),
            "fallback_enabled": True
        }


# Singleton instance
_multi_llm_service = None


def get_multi_llm_service() -> MultiLLMService:
    """Get or create the Multi-LLM service singleton."""
    global _multi_llm_service
    if _multi_llm_service is None:
        _multi_llm_service = MultiLLMService()
    return _multi_llm_service
