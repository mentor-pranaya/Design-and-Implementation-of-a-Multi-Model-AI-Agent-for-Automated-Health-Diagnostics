"""
Anthropic Claude LLM Provider.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from src.llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class ClaudeLLMProvider(LLMProvider):
    """Anthropic Claude LLM provider for medical recommendations."""
    
    def __init__(self):
        self.name = "Anthropic Claude"
        self.client = None
        self.available = False
        self.model_name = "claude-3-opus-20240229"
        self.initialize()
    
    def initialize(self) -> bool:
        """Initialize Claude client."""
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not found in environment variables")
                return False
            
            # Use compatibility wrapper
            from src.llm.sdk_compat import anthropic_completion
            self.client = True
            self._api_key = api_key
            self._anthropic_completion = anthropic_completion
            self.available = True
            logger.info(f"{self.name} LLM provider initialized successfully")
            return True
        except ImportError:
            logger.warning("Anthropic library not installed. Install with: pip install anthropic")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {str(e)}")
            self.available = False
            return False
    
    def is_available(self) -> bool:
        """Check if Claude is available."""
        return self.available and self.client is not None
    
    def generate_recommendations(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate recommendations using Claude."""
        if not self.is_available():
            return []
        
        try:
            prompt = self._build_recommendation_prompt(
                interpretations, risks, parameters, patient_context
            )
            
            # Use compatibility helper for Anthropic
            text = self._anthropic_completion(api_key=self._api_key, model=self.model_name, prompt=prompt, max_tokens=2048)
            if text:
                recommendations = self._parse_llm_response(text)
                logger.info(f"Generated {len(recommendations)} recommendations from {self.name}")
                return recommendations
            
            logger.warning(f"Empty response from {self.name}")
            return []
        
        except Exception as e:
            logger.error(f"Error generating recommendations from {self.name}: {str(e)}")
            return []
    
    def generate_text(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate text response from Claude."""
        if not self.is_available():
            return ""
        
        try:
            text = self._anthropic_completion(api_key=self._api_key, model=self.model_name, prompt=prompt, max_tokens=max_tokens)
            return text or ""
        except Exception as e:
            logger.error(f"Error generating text from {self.name}: {str(e)}")
            return ""
    
    def _build_recommendation_prompt(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build comprehensive prompt for recommendations."""
        
        param_str = "\n".join([f"- {k}: {v}" for k, v in parameters.items()])
        
        prompt = f"""You are an expert medical AI assistant specializing in blood report analysis and personalized health recommendations.

Based on the following blood test results and analysis, provide 8-12 specific, actionable, and personalized health recommendations. Focus on lifestyle changes, dietary advice, and preventive measures.

BLOOD TEST PARAMETERS:
{param_str}

MEDICAL INTERPRETATIONS:
{chr(10).join(f"- {interp}" for interp in interpretations)}

IDENTIFIED HEALTH RISKS:
{chr(10).join(f"- {risk}" for risk in risks)}

INSTRUCTIONS:
1. Provide recommendations that directly address the specific findings and risks identified
2. Include both immediate actions and long-term lifestyle changes
3. Focus on evidence-based, practical advice
4. Prioritize recommendations based on severity of findings
5. Include dietary suggestions with specific foods
6. Suggest appropriate exercise or physical activity
7. Mention when to seek professional medical consultation
8. Keep recommendations concise but informative
9. Use bullet points for clarity
10. Include monitoring and follow-up suggestions

Format your response as a numbered list of recommendations, each starting with an emoji relevant to the recommendation type.

IMPORTANT: These recommendations are supplementary to professional medical advice. Always emphasize consulting healthcare providers for serious conditions."""
        
        if patient_context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in patient_context.items()])
            prompt += f"\n\nPATIENT CONTEXT:\n{context_str}"
        
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> List[str]:
        """Parse LLM response into clean list of recommendations."""
        try:
            lines = response_text.strip().split('\n')
            recommendations = []
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                    recommendations.append(line)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error parsing {self.name} response: {str(e)}")
            return []
