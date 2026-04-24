"""
============================================================
SERVICE: URL Security Analyzer
OWNER:   Person A
============================================================

Analyzes URLs for phishing, scams, and security risks
using the Gemini AI model. Returns classification,
risk score, reasons, and recommendations.
============================================================
"""

import json
from backend.services.gemini_service import get_gemini_client, get_model_id


SYSTEM_PROMPT = (
    "You are a cybersecurity expert. "
    "Analyze the given URL or text for security risks. "
    "Return ONLY valid raw JSON (no markdown, no explanation) in this format:\n"
    '{ "classification": "SAFE | SUSPICIOUS | DANGEROUS", '
    '"risk_score": number, "reasons": string[], "recommendation": "string" }'
)


def analyze_url(message: str) -> dict:
    """
    Sends a URL or text to Gemini AI for security analysis.

    Args:
        message: The URL or text to analyze.

    Returns:
        Dictionary with classification, risk_score, reasons, recommendation.
    """
    client = get_gemini_client()

    from google.genai import types

    response = client.models.generate_content(
        model=get_model_id(),
        contents=message,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=SYSTEM_PROMPT,
        ),
    )

    # Parse the JSON response from Gemini
    response_text = response.text
    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    result = json.loads(cleaned)

    return result
