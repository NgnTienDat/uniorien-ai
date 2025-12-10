import os
import openai
from typing import List, Dict, Optional

from components.interfaces import IGenerator


class OpenAIGenerator(IGenerator):
    """
    Primary LLM Provider: OpenAI (gpt-4o-mini / gpt-4o)
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing.")

        openai.api_key = api_key
        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate response từ OpenAI Chat Completion.
        """

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": user_prompt})

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message["content"]

        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {str(e)}")
