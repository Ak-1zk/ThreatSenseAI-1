"""
Shared Gemini AI client.
Provides a single reusable client instance for all services.
"""

from google import genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL


def get_gemini_client() -> genai.Client:
    """Creates and returns a Gemini AI client."""
    return genai.Client(api_key=GEMINI_API_KEY)


def get_model_id() -> str:
    """Returns the configured Gemini model ID."""
    return GEMINI_MODEL
