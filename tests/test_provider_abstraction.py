import pytest
from unittest.mock import patch

from providers.llm_provider import LLMProvider
from providers.gemini_provider import GeminiProvider
from providers.deepseek_provider import DeepSeekProvider
from providers.openai_provider import OpenAIProvider
from providers.claude_provider import ClaudeProvider
from providers.kimi_provider import KimiProvider
from providers.llama_provider import LlamaProvider
from providers.provider_factory import PROVIDER_MAP, get_provider


PROVIDERS = [
    GeminiProvider,
    DeepSeekProvider,
    OpenAIProvider,
    ClaudeProvider,
    KimiProvider,
    LlamaProvider,
]


def test_all_providers_implement_llm_provider():
    for provider_class in PROVIDERS:
        assert issubclass(provider_class, LLMProvider)


def test_all_required_providers_are_registered():
    expected = {
        "gemini",
        "deepseek",
        "openai",
        "claude",
        "kimi",
        "llama",
    }

    assert set(PROVIDER_MAP.keys()) == expected


def test_provider_names_are_unique():
    names = [provider_class.name for provider_class in PROVIDERS]

    assert len(names) == len(set(names))


@pytest.mark.parametrize(
    "provider_class",
    PROVIDERS,
)
def test_provider_has_common_interface(provider_class):
    assert hasattr(provider_class, "generate")
    assert hasattr(provider_class, "get_usage")
    assert hasattr(provider_class, "name")
    assert hasattr(provider_class, "model")


def test_provider_switching_by_configuration(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")

    gemini = get_provider()
    assert gemini.name == "gemini"

    monkeypatch.setenv("LLM_PROVIDER", "deepseek")

    deepseek = get_provider()
    assert deepseek.name == "deepseek"


def test_ask_llm_uses_configured_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")

    with patch(
        "services.llm_service.get_cached",
        return_value={"result": "cached"},
    ) as mock_cache:

        from services.llm_service import ask_llm

        result = ask_llm("Test prompt")

        assert result == {"result": "cached"}

        mock_cache.assert_called_once_with(
            prompt="Test prompt",
            provider="deepseek",
        )
