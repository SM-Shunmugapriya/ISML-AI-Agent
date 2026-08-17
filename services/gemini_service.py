import os
import json
import time

from dotenv import load_dotenv
from google import genai

from services.logger import log_info, log_error


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(prompt: str) -> dict:
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

        result = json.loads(response.text)

        elapsed_time = time.perf_counter() - start_time

        log_info(
            f"Gemini API request completed | "
            f"response_time={elapsed_time:.2f}s"
        )

        return result

    except Exception as e:
        elapsed_time = time.perf_counter() - start_time

        log_error(
            f"Gemini API request failed | "
            f"response_time={elapsed_time:.2f}s | error={e}"
        )

        raise