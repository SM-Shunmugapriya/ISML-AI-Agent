from providers.llm_provider import LLMProvider
from services.deepseek_service import ask_deepseek, get_last_usage


class DeepSeekProvider(LLMProvider):
    """DeepSeek implementation of the LLM provider interface."""

    name = "deepseek"
    model = "deepseek-chat"

    def generate(self, prompt: str):
        return ask_deepseek(prompt)

    def get_usage(self) -> dict[str, int]:
        return get_last_usage()