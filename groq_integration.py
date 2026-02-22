import os
import requests
from typing import Dict, Optional


class GroqClient:
    """Minimal Groq API scaffold — replace endpoint and payload as needed.

    Requires environment variable `GROQ_API_KEY` and `GROQ_API_URL`.
    """

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.api_url = api_url or os.environ.get("GROQ_API_URL")
        if not self.api_key or not self.api_url:
            raise EnvironmentError("GROQ_API_KEY and GROQ_API_URL must be set to use Groq integration.")

    def run_model(self, model: str, prompt: str, params: Optional[Dict] = None) -> Dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "prompt": prompt}
        if params:
            payload["params"] = params

        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()


def example_usage():
    gc = GroqClient()
    out = gc.run_model("gpt-4o-mini", "Summarize the lab report findings.")
    return out
