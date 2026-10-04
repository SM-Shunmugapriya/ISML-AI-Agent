from providers.llm_provider import LLMProvider
from services.gemini_service import ask_gemini, get_last_usage


class GeminiProvider(LLMProvider):
    """Gemini implementation of the LLM provider interface."""

    name = "gemini"
    model = "gemini-3.6-flash"

    def generate(self, prompt: str):
        return ask_gemini(prompt)

    def get_usage(self) -> dict[str, int]:
        return get_last_usage()