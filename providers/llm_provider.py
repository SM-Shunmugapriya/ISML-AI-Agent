from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Common interface for all LLM providers."""

    name: str
    model: str

    @abstractmethod
    def generate(self, prompt: str) -> Any:
        """Generate an LLM response for the given prompt."""
        raise NotImplementedError

    def get_usage(self) -> dict[str, int]:
        """Return token usage for the latest request."""
        return {
            "input_tokens": 0,
            "output_tokens": 0,
        }