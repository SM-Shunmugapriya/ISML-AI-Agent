import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_embedding(text: str) -> list[float]:
    """
    Generate a vector embedding for the given text.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values