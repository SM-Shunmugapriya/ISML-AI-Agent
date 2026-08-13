from services.deepseek_service import ask_deepseek
from services.gemini_service import ask_gemini


def ask_llm(prompt: str, provider: str = "gemini") -> dict:
    if provider == "deepseek":
        return ask_deepseek(prompt)

    if provider == "gemini":
        return ask_gemini(prompt)

    raise ValueError(f"Unsupported LLM provider: {provider}")