import unittest
from unittest.mock import MagicMock, patch

from src.services.llm_service import LLMService


class TestLLMService(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.model = "gemini-1.5-flash"
        self.service = LLMService(api_key=self.api_key, model=self.model)
        self.search_results = [
            {"url": "http://example.com", "snippet": "Example snippet content"}
        ]
        self.prompt_template = "Extract the main topic."

    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_extract_information_success(self, mock_generate_content):
        mock_response = MagicMock()
        mock_response.text = "Main topic: Example"
        mock_generate_content.return_value = mock_response

        result = self.service.extract_information(
            self.search_results, self.prompt_template
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "Main topic: Example")

    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_extract_information_failure(self, mock_generate_content):
        mock_generate_content.side_effect = Exception("API error")

        result = self.service.extract_information(
            self.search_results, self.prompt_template
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("API error", result["result"])


if __name__ == "__main__":
    unittest.main()
