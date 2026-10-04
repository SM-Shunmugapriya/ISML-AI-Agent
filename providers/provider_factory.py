import os

from providers.llm_provider import LLMProvider
from providers.gemini_provider import GeminiProvider
from providers.deepseek_provider import DeepSeekProvider
from providers.openai_provider import OpenAIProvider
from providers.claude_provider import ClaudeProvider
from providers.kimi_provider import KimiProvider
from providers.llama_provider import LlamaProvider


PROVIDER_MAP = {
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
    "openai": OpenAIProvider,
    "claude": ClaudeProvider,
    "kimi": KimiProvider,
    "llama": LlamaProvider,
}


def get_provider(provider_name: str | None = None) -> LLMProvider:
    """Create the configured LLM provider."""

    name = (
        provider_name
        or os.getenv("LLM_PROVIDER", "gemini")
    ).lower().strip()

    provider_class = PROVIDER_MAP.get(name)

    if provider_class is None:
        supported = ", ".join(PROVIDER_MAP.keys())
        raise ValueError(
            f"Unsupported LLM provider: {name}. "
            f"Supported providers: {supported}"
        )

    return provider_class()