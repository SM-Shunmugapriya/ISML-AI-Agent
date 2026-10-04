import os

from openai import OpenAI

from providers.llm_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of the LLM provider interface."""

    name = "openai"
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    def get_usage(self) -> dict[str, int]:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
        }