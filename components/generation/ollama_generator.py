import requests
from typing import List, Dict, Optional

from components.interfaces import IGenerator


class OllamaGenerator(IGenerator):
    """
    Fallback LLM provider, using Ollama server.
    """

    def __init__(self,
                 model: str = "llama3.1:8b",
                 host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Ollama trả nội dung trong data["message"]["content"]
            return data.get("message", {}).get("content", "")

        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
