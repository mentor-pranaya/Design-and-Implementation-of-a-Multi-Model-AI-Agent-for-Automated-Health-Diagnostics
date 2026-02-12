"""
Abstract base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the LLM provider with API key and configuration."""
        raise NotImplementedError
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is properly configured and available."""
        raise NotImplementedError
    
    @abstractmethod
    def generate_recommendations(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate medical recommendations using the LLM."""
        raise NotImplementedError
    
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate text response from a prompt."""
        raise NotImplementedError
