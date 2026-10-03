import os
import json
import time

from dotenv import load_dotenv
from google import genai

from services.logger import log_info, log_error


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={
        "timeout": 30000
    }
)

# ENH-007: Stores usage from the latest Gemini request.
_last_usage = {
    "input_tokens": 0,
    "output_tokens": 0,
}


def get_last_usage() -> dict:
    return _last_usage.copy()


def ask_gemini(prompt: str) -> dict:
    global _last_usage

    # Reset usage before every request to avoid stale values.
    _last_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
    }

    start_time = time.perf_counter()

    log_info("Gemini API request started")

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            },
        )

        usage = getattr(response, "usage_metadata", None)

        if usage is not None:
            _last_usage = {
                "input_tokens": int(
                    getattr(usage, "prompt_token_count", 0) or 0
                ),
                "output_tokens": int(
                    getattr(usage, "candidates_token_count", 0) or 0
                ),
            }

        result = json.loads(response.text)

        elapsed_time = time.perf_counter() - start_time

        log_info(
            f"Gemini API request completed | "
            f"response_time={elapsed_time:.2f}s | "
            f"input_tokens={_last_usage['input_tokens']} | "
            f"output_tokens={_last_usage['output_tokens']}"
        )

        return result

    except Exception as e:
        elapsed_time = time.perf_counter() - start_time

        log_error(
            f"Gemini API request failed | "
            f"response_time={elapsed_time:.2f}s | error={e}"
        )

        raise
