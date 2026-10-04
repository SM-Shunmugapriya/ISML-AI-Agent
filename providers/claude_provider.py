import os

from providers.llm_provider import LLMProvider


class ClaudeProvider(LLMProvider):
    """Claude implementation of the LLM provider interface."""

    name = "claude"
    model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required for ClaudeProvider"
            ) from exc

        self.client = Anthropic(api_key=api_key)

    def generate(self, prompt: str):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.content[0].text

    def get_usage(self) -> dict[str, int]:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
        }