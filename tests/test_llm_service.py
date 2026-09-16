import pytest
from unittest.mock import patch

from services.llm_service import ask_llm


def test_llm_retries_up_to_three_attempts():
    with patch(
        "services.llm_service.get_cached",
        return_value=None,
    ), patch(
        "services.llm_service.ask_gemini",
        side_effect=[
            ValueError("Invalid LLM output"),
            ValueError("Invalid LLM output"),
            {
                "topic": "Python",
                "recommendedResources": [],
                "learningSequence": [],
            },
        ],
    ) as mock_llm:

        result = ask_llm("Test prompt", provider="gemini")

        assert result["topic"] == "Python"
        assert mock_llm.call_count == 3


def test_llm_fails_after_three_attempts():
    with patch(
        "services.llm_service.get_cached",
        return_value=None,
    ), patch(
        "services.llm_service.ask_gemini",
        side_effect=ValueError("Invalid LLM output"),
    ) as mock_llm:

        with pytest.raises(ValueError, match="Invalid LLM output"):
            ask_llm("Test prompt", provider="gemini")

        assert mock_llm.call_count == 3
