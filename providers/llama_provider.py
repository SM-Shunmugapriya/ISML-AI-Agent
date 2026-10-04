import os

from openai import OpenAI

from providers.llm_provider import LLMProvider


class LlamaProvider(LLMProvider):
    """Llama implementation using an OpenAI-compatible API."""

    name = "llama"
    model = os.getenv("LLAMA_MODEL", "meta-llama/llama-3.1-8b-instruct")

    def __init__(self):
        api_key = os.getenv("LLAMA_API_KEY")

        if not api_key:
            raise ValueError("LLAMA_API_KEY is not configured")

        self.client = OpenAI(
            api_key=api_key,
            base_url=os.getenv(
                "LLAMA_BASE_URL",
                "https://api.groq.com/openai/v1",
            ),
        )

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