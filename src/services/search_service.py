from typing import Dict, List

import requests

from utils.rate_limiter import RateLimiter


class SearchService:
    def __init__(self, api_key: str, rate_limit: int = 5):
        self.api_key = api_key
        if not self.api_key or self.api_key.startswith("${"):
            raise ValueError(
                "Invalid SERPAPI_API_KEY. Please check your environment variables."
            )
        self.rate_limiter = RateLimiter(rate_limit)

    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        self.rate_limiter.wait()
        try:
            params = {"api_key": self.api_key, "q": query, "num": max_results}

            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()

            data = response.json()
            organic_results = data.get("organic_results", [])

            return [
                {"url": r.get("link"), "snippet": r.get("snippet", "")}
                for r in organic_results[:max_results]
            ]

        except requests.exceptions.RequestException as e:
            raise Exception(f"Search error: {str(e)}")
