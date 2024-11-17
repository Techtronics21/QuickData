from typing import Any, Dict
import groq
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMService:
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.model = model
        self.client = groq.Groq(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def extract_information(
        self, search_results: list, prompt_template: str
    ) -> Dict[str, Any]:
        try:
            formatted_results = "\n".join(
                [f"URL: {r['url']}\nContent: {r['snippet']}" for r in search_results]
            )

            system_prompt = """Extract the requested information from the search results. 
            If the information is not found, return "Not found". Be precise and concise."""

            prompt = f"{system_prompt}\n\nSearch results:\n{formatted_results}\n\nExtract: {prompt_template}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            return {"result": response.choices[0].message.content, "status": "success"}
        except Exception as e:
            return {"result": str(e), "status": "error"}

    def extract_multiple_information(
        self, search_results: list, prompt_templates: list
    ) -> Dict[str, Any]:
        try:
            formatted_results = "\n".join(
                [f"URL: {r['url']}\nContent: {r['snippet']}" for r in search_results]
            )

            system_prompt = """Extract multiple pieces of information from the search results. 
            For each prompt, provide a separate answer. If information is not found, return "Not found"."""

            prompts_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(prompt_templates)])
            prompt = f"{system_prompt}\n\nSearch results:\n{formatted_results}\n\nExtract:\n{prompts_text}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            return {"result": response.choices[0].message.content, "status": "success"}
        except Exception as e:
            return {"result": str(e), "status": "error", "error_type": type(e).__name__}
