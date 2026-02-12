import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.llm.llm_service import LLMService


class TestLLMService:
    """Test cases for LLMService class."""

    def test_init_with_api_key(self):
        """Test initialization with valid API key."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            with patch('google.generativeai.configure') as mock_configure:
                with patch('google.generativeai.GenerativeModel') as mock_model:
                    service = LLMService()
                    mock_configure.assert_called_once_with(api_key='test_key')
                    mock_model.assert_called_once_with('gemini-1.5-flash')
                    assert service.client is True

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.llm.llm_service.logger') as mock_logger:
                service = LLMService()
                mock_logger.warning.assert_called_once()
                assert service.client is None

    @patch('src.llm.llm_service.genai')
    def test_generate_recommendations_success(self, mock_genai):
        """Test successful recommendation generation."""
        # Setup mocks
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "1. 🥗 Eat more vegetables\n2. 🏃‍♂️ Exercise regularly"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            service = LLMService()

            interpretations = ["Hemoglobin is low"]
            risks = ["Anemia risk"]
            parameters = {"hemoglobin": 10.5}

            recommendations = service.generate_medical_recommendations(
                interpretations, risks, parameters
            )

            assert len(recommendations) == 2
            assert "Eat more vegetables" in recommendations[0]
            assert "Exercise regularly" in recommendations[1]

    @patch('src.llm.llm_service.genai')
    def test_generate_recommendations_no_client(self, mock_genai):
        """Test recommendation generation when client is not available."""
        with patch.dict(os.environ, {}, clear=True):
            service = LLMService()

            recommendations = service.generate_medical_recommendations([], [], {})

            assert recommendations == []

    @patch('src.llm.llm_service.genai')
    def test_generate_recommendations_empty_response(self, mock_genai):
        """Test handling of empty response from LLM."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            with patch('src.llm.llm_service.logger') as mock_logger:
                service = LLMService()

                recommendations = service.generate_medical_recommendations([], [], {})

                mock_logger.warning.assert_called_once()
                assert recommendations == []

    @patch('src.llm.llm_service.genai')
    def test_generate_recommendations_exception(self, mock_genai):
        """Test handling of exceptions during LLM call."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            with patch('src.llm.llm_service.logger') as mock_logger:
                service = LLMService()

                recommendations = service.generate_medical_recommendations([], [], {})

                mock_logger.error.assert_called_once()
                assert recommendations == []

    def test_build_recommendation_prompt(self):
        """Test prompt building functionality."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            service = LLMService()

            interpretations = ["High glucose levels"]
            risks = ["Diabetes risk"]
            parameters = {"glucose": 150}
            patient_context = {"age": 45, "gender": "male"}

            prompt = service._build_recommendation_prompt(
                interpretations, risks, parameters, patient_context
            )

            assert "glucose: 150" in prompt
            assert "High glucose levels" in prompt
            assert "Diabetes risk" in prompt
            assert "age: 45" in prompt
            assert "gender: male" in prompt

    def test_parse_llm_response(self):
        """Test parsing of LLM response."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            service = LLMService()

            response_text = "1. 🥗 Eat healthy foods\n2. 🏃‍♂️ Stay active\n• Some bullet point"

            recommendations = service._parse_llm_response(response_text)

            assert len(recommendations) == 3
            assert "Eat healthy foods" in recommendations[0]
            assert "Stay active" in recommendations[1]
            assert "Some bullet point" in recommendations[2]


if __name__ == "__main__":
    pytest.main([__file__])
