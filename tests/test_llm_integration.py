import pytest
import os
from unittest.mock import patch, MagicMock
from src.recommendation.recommendation_generator import generate_recommendations
from src.llm.llm_service import LLMService


class TestLLMIntegration:
    """Integration tests for LLM-based recommendation system."""

    @patch('src.llm.llm_service.genai')
    def test_generate_recommendations_with_llm_success(self, mock_genai):
        """Test successful LLM-based recommendation generation."""
        # Setup LLM mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """1. 🥗 Increase iron-rich foods intake
2. 🏃‍♂️ Maintain regular physical activity
3. 👨‍⚕️ Consult healthcare provider for anemia evaluation
4. 🩸 Schedule follow-up blood tests in 3 months"""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            interpretations = ["Hemoglobin is low (10.5 g/dL)", "MCH is decreased"]
            risks = ["Iron deficiency anemia", "Nutritional deficiency"]

            recommendations = generate_recommendations(interpretations, risks)

            assert len(recommendations) >= 3
            assert any("iron" in rec.lower() for rec in recommendations)
            assert any("consult" in rec.lower() or "provider" in rec.lower() for rec in recommendations)

    @patch('src.llm.llm_service.genai')
    def test_generate_recommendations_llm_fallback(self, mock_genai):
        """Test fallback to rule-based recommendations when LLM fails."""
        # Setup LLM to fail
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            interpretations = ["Hemoglobin is low"]
            risks = ["Anemia risk"]

            recommendations = generate_recommendations(interpretations, risks)

            # Should fall back to hardcoded recommendations
            assert len(recommendations) > 0
            assert any("iron" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_no_llm(self):
        """Test recommendations without LLM (fallback only)."""
        with patch.dict(os.environ, {}, clear=True):
            interpretations = ["Glucose is high", "HbA1c is elevated"]
            risks = ["Diabetes mellitus"]

            recommendations = generate_recommendations(interpretations, risks)

            assert len(recommendations) > 0
            assert any("glucose" in rec.lower() or "diabetes" in rec.lower() for rec in recommendations)

    @patch('src.llm.llm_service.genai')
    def test_diabetes_recommendations(self, mock_genai):
        """Test diabetes-specific recommendations."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """1. 🥗 Follow low glycemic index diet
2. 🏃‍♂️ Regular blood glucose monitoring
3. 💧 Stay hydrated with water
4. 👨‍⚕️ Consult endocrinologist for diabetes management"""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            interpretations = ["Fasting glucose is 140 mg/dL", "HbA1c is 7.2%"]
            risks = ["Type 2 diabetes mellitus"]

            recommendations = generate_recommendations(interpretations, risks)

            assert len(recommendations) >= 3
            assert any("diet" in rec.lower() or "glycemic" in rec.lower() for rec in recommendations)

    @patch('src.llm.llm_service.genai')
    def test_liver_disease_recommendations(self, mock_genai):
        """Test liver disease recommendations."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """1. 🚫 Avoid alcohol consumption completely
2. 🥗 Follow liver-friendly diet
3. 💊 Take prescribed medications regularly
4. 👨‍⚕️ Regular liver function monitoring"""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            interpretations = ["ALT is elevated (80 U/L)", "AST is high (65 U/L)"]
            risks = ["Liver dysfunction", "Hepatitis possible"]

            recommendations = generate_recommendations(interpretations, risks)

            assert len(recommendations) >= 3
            assert any("alcohol" in rec.lower() for rec in recommendations)

    @patch('src.llm.llm_service.genai')
    def test_kidney_disease_recommendations(self, mock_genai):
        """Test kidney disease recommendations."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """1. 🧂 Reduce salt intake to less than 2g daily
2. 💧 Stay adequately hydrated
3. 🥗 Limit potassium-rich foods if advised
4. 👨‍⚕️ Consult nephrologist for kidney evaluation"""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            interpretations = ["Creatinine is 1.8 mg/dL", "eGFR is decreased"]
            risks = ["Chronic kidney disease stage 2"]

            recommendations = generate_recommendations(interpretations, risks)

            assert len(recommendations) >= 3
            assert any("salt" in rec.lower() for rec in recommendations)

    @patch('src.llm.llm_service.genai')
    def test_cardiovascular_risk_recommendations(self, mock_genai):
        """Test cardiovascular risk recommendations."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """1. 🫒 Follow Mediterranean diet
2. 🏃‍♂️ Regular aerobic exercise 150 minutes/week
3. 🩸 Monitor blood pressure regularly
4. 👨‍⚕️ Consult cardiologist for risk assessment"""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            interpretations = ["Total cholesterol is 250 mg/dL", "LDL is high"]
            risks = ["Cardiovascular disease risk"]

            recommendations = generate_recommendations(interpretations, risks)

            assert len(recommendations) >= 3
            assert any("diet" in rec.lower() or "mediterranean" in rec.lower() for rec in recommendations)


if __name__ == "__main__":
    pytest.main([__file__])
