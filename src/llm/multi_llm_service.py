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
