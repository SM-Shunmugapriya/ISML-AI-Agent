import os

from dotenv import load_dotenv
from google import genai

from services.resilience_service import (
    retry_with_backoff,
    CircuitBreaker,
)


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={
        "timeout": 30000
    }
)


EMBEDDING_CIRCUIT_BREAKER = CircuitBreaker(
    failure_threshold=5
)


def generate_embedding(text: str) -> list[float]:
    """
    Generate a vector embedding for the given text.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    def embedding_request():
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )

        return response.embeddings[0].values

    resilient_request = retry_with_backoff(
        max_retries=3,
        backoff_factor=1,
        timeout=30,
        circuit_breaker=EMBEDDING_CIRCUIT_BREAKER,
    )(embedding_request)

    return resilient_request()