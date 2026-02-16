import os
import logging
from dotenv import load_dotenv
import google.genai as genai
from typing import List, Dict, Any
import json

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Google's Gemini LLM for medical recommendations."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            self.model = 'gemini-1.5-flash'
            logger.info("Gemini LLM service initialized")

    def generate_medical_recommendations(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any],
        patient_context: Dict[str, Any] = None
    ) -> List[str]:
        """
        Generate personalized medical recommendations using Gemini LLM.

        Args:
            interpretations: List of parameter interpretations
            risks: List of identified health risks
            parameters: Dictionary of medical parameters
            patient_context: Additional patient information (age, gender, etc.)

        Returns:
            List of personalized recommendations
        """
        if not self.client:
            logger.warning("LLM service not available, returning empty recommendations")
            return []

        try:
            # Prepare the prompt for Gemini
            prompt = self._build_recommendation_prompt(
                interpretations, risks, parameters, patient_context
            )

            # Generate response from Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            if response and response.text:
                # Parse the response into a list of recommendations
                recommendations = self._parse_llm_response(response.text)
                logger.info(f"Generated {len(recommendations)} LLM recommendations")
                return recommendations
            else:
                logger.warning("Empty response from Gemini LLM")
                return []

        except Exception as e:
            logger.error(f"Error generating LLM recommendations: {str(e)}")
            return []

    def _build_recommendation_prompt(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any],
        patient_context: Dict[str, Any] = None
    ) -> str:
        """Build a comprehensive prompt for the LLM."""

        # Format parameters for readability
        param_str = "\n".join([f"- {k}: {v}" for k, v in parameters.items()])

        # Build the prompt
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

Format your response as a numbered list of recommendations, each starting with an emoji relevant to the recommendation type (e.g., 🥗 for diet, 🏃‍♂️ for exercise, 👨‍⚕️ for medical consultation).

IMPORTANT: These recommendations are supplementary to professional medical advice. Always emphasize consulting healthcare providers for serious conditions."""

        if patient_context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in patient_context.items()])
            prompt += f"\n\nPATIENT CONTEXT:\n{context_str}"

        return prompt

    def _parse_llm_response(self, response_text: str) -> List[str]:
        """Parse the LLM response into a clean list of recommendations."""
        try:
            # Split by numbered list items and clean up
            lines = response_text.strip().split('\n')
            recommendations = []

            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                    recommendations.append(line)

            return recommendations
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return []
