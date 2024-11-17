import unittest
from unittest.mock import MagicMock, patch

import requests

from src.services.search_service import SearchService


class TestSearchService(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.search_service = SearchService(api_key=self.api_key)

    @patch("src.services.search_service.requests.get")
    def test_search_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic_results": [
                {"link": "http://example.com/1", "snippet": "Example snippet 1"},
                {"link": "http://example.com/2", "snippet": "Example snippet 2"},
                {"link": "http://example.com/3", "snippet": "Example snippet 3"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = self.search_service.search("test query", max_results=2)
        expected_results = [
            {"url": "http://example.com/1", "snippet": "Example snippet 1"},
            {"url": "http://example.com/2", "snippet": "Example snippet 2"},
        ]

        self.assertEqual(results, expected_results)
        mock_get.assert_called_once_with(
            "https://serpapi.com/search",
            params={"api_key": self.api_key, "q": "test query", "num": 2},
        )

    @patch("src.services.search_service.requests.get")
    def test_search_no_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"organic_results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = self.search_service.search("test query", max_results=2)
        expected_results = []

        self.assertEqual(results, expected_results)
        mock_get.assert_called_once_with(
            "https://serpapi.com/search",
            params={"api_key": self.api_key, "q": "test query", "num": 2},
        )

    @patch("src.services.search_service.requests.get")
    def test_search_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test exception")

        with self.assertRaises(Exception) as context:
            self.search_service.search("test query", max_results=2)

        self.assertTrue("Search error: Test exception" in str(context.exception))
        mock_get.assert_called_once_with(
            "https://serpapi.com/search",
            params={"api_key": self.api_key, "q": "test query", "num": 2},
        )

    def test_invalid_api_key(self):
        with self.assertRaises(ValueError) as context:
            SearchService(api_key="${INVALID_KEY}")

        self.assertTrue(
            "Invalid SERPAPI_API_KEY. Please check your environment variables."
            in str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
