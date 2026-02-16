"""
Google Gemini LLM Provider.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import warnings

# Suppress the FutureWarning about deprecated google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

# Try to import google.generativeai (old SDK) first for better compatibility with v1beta models
try:
    import google.generativeai as genai
    GENAI_VERSION = "old"
except ImportError:
    try:
        import google.genai as genai
        GENAI_VERSION = "new"
    except ImportError:
        genai = None
        GENAI_VERSION = None

from src.llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class GeminiLLMProvider(LLMProvider):
    """Google Gemini LLM provider for medical recommendations."""
    
    def __init__(self):
        self.name = "Google Gemini"
        self.model: Optional[str] = None
        self.available = False
        self.initialize()
    
    def initialize(self) -> bool:
        """Initialize Gemini with API key."""
        try:
            if genai is None:
                logger.warning("google.genai or google.generativeai not installed")
                return False
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in environment")
                return False

            self._api_key = api_key
            
            # Use 'gemini-2.0-flash' as the latest model - fall back to older models if needed
            # Try latest models first
            candidate_models = [
                'gemini-flash-latest',
                'gemini-2.0-flash-lite-001',
                'gemini-2.5-flash',
                'gemini-2.0-flash', 
                'gemini-pro-latest',
            ]
            for model_name in candidate_models:
                try:
                    # Test if model is available
                    if GENAI_VERSION == "new":
                        # New google.genai package
                        self.client = genai.Client(api_key=api_key)
                        test_response = self.client.models.generate_content(
                            model=model_name, contents="test"
                        )
                        if test_response:
                            self.model = model_name
                            break
                    else:
                        # Old google.generativeai package - use configure
                        genai.configure(api_key=api_key)
                        test_model = genai.GenerativeModel(model_name)
                        test_response = test_model.generate_content("test")
                        if test_response:
                            self.model = model_name
                            break
                except Exception as e:
                    logger.debug(f"Model {model_name} not available: {e}")
                    continue
            
            if not self.model:
                logger.warning("No available Gemini models found")
                return False
            
            # Set the generation function based on package version
            if GENAI_VERSION == "new":
                self._generate_func = self._generate_new
            else:
                self._generate_func = self._generate_old
            
            self.available = True
            logger.info(f"{self.name} LLM provider initialized successfully with model {self.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {str(e)}")
            self.available = False
            return False
    
    def _generate_new(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate text using new google.genai package."""
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )
            if response and hasattr(response, 'text'):
                return response.text
            return None
        except Exception as e:
            logger.error(f"Error generating text with new API: {e}")
            return None
    
    def _generate_old(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate text using old google.generativeai package."""
        try:
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                return response.text
            return None
        except Exception as e:
            logger.error(f"Error generating text with old API: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.available and self.model is not None
    
    def generate_recommendations(
        self,
        interpretations: List[str],
        risks: List[str],
        parameters: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate recommendations using Gemini."""
        if not self.is_available():
            return []
        
        try:
            prompt = self._build_recommendation_prompt(interpretations, risks, parameters, patient_context)
            # Use a simpler prompt for stability if needed, but current one is fine
            text = self.generate_text(prompt, 1024)
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
        """Generate text response from Gemini."""
        if not self.is_available():
            return ""
        
        try:
            text = self._generate_func(prompt, max_tokens)
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

Format your response as a numbered list of recommendations, each starting with an emoji relevant to the recommendation type (e.g., 🥗 for diet, 🏃‍♂️ for exercise, 👨‍⚕️ for medical consultation).

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
                if line and (line[0].isdigit() or line.startswith(('•', '-', '*', '🥗', '🏃', '👨', '🩺'))):
                    recommendations.append(line)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error parsing {self.name} response: {str(e)}")
            return []
    def extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extract medical parameters from text using Gemini."""
        if not self.is_available():
            return {}
        
        try:
            # Increased limit to 10000 chars for full reports
            prompt = f"""You are an expert medical data extractor. Your task is to extract blood test parameters from the following text and return them in a strict JSON format.

TEXT DATA:
{text[:10000]}

INSTRUCTIONS:
1. Identify all blood test parameters (e.g., Hemoglobin, Glucose, Cholesterol, RBC, WBC, Platelets, etc.).
2. For each parameter, extract the numerical value and the unit.
3. Standardize parameter names to common medical terms (e.g., "Hb" -> "Hemoglobin").
4. Ignore headers, footers, and irrelevant text.
5. Return ONLY a JSON object where keys are standardized parameter names and values are objects containing "value" (number) and "unit" (string).
6. Do not include any markdown formatting or explanations. JSON only.

EXAMPLE FORMAT:
{{
  "Hemoglobin": {{"value": 13.5, "unit": "g/dL"}},
  "Total Cholesterol": {{"value": 180, "unit": "mg/dL"}}
}}

JSON OUTPUT:"""
            
            response_text = self.generate_text(prompt, max_tokens=4096)
            
            # Robust JSON cleaning
            cleaned_json = response_text.strip()
            if "```json" in cleaned_json:
                cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_json:
                cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()
            
            # Remove any leading/trailing chars that aren't brackets
            start_idx = cleaned_json.find('{')
            end_idx = cleaned_json.rfind('}')
            
            pass
            if start_idx != -1 and end_idx != -1:
                cleaned_json = cleaned_json[start_idx:end_idx+1]
            
            import json
            data = json.loads(cleaned_json)
            return data
            
        except Exception as e:
            logger.error(f"Error extracting parameters with Gemini: {str(e)}")
            return {}
