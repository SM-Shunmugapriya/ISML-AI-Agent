import os

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    timeout=30.0
)

# ENH-007: Stores usage from the latest DeepSeek request.
_last_usage = {
    "input_tokens": 0,
    "output_tokens": 0,
}


def get_last_usage() -> dict:
    return _last_usage.copy()


def ask_deepseek(prompt: str) -> str:
    global _last_usage

    # Reset usage before every request to avoid stale values.
    _last_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
    }

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    usage = getattr(response, "usage", None)

    if usage is not None:
        _last_usage = {
            "input_tokens": int(
                getattr(usage, "prompt_tokens", 0) or 0
            ),
            "output_tokens": int(
                getattr(usage, "completion_tokens", 0) or 0
            ),
        }

    return response.choices[0].message.content
