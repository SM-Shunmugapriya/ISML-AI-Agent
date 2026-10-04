import os

from openai import OpenAI

from providers.llm_provider import LLMProvider


class KimiProvider(LLMProvider):
    """Kimi implementation using an OpenAI-compatible API."""

    name = "kimi"
    model = os.getenv("KIMI_MODEL", "moonshot-v1-8k")

    def __init__(self):
        api_key = os.getenv("KIMI_API_KEY")

        if not api_key:
            raise ValueError("KIMI_API_KEY is not configured")

        self.client = OpenAI(
            api_key=api_key,
            base_url=os.getenv(
                "KIMI_BASE_URL",
                "https://api.moonshot.cn/v1",
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