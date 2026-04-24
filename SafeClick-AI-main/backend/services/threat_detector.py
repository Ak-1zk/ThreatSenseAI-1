"""
============================================================
SERVICE: Email & Message Threat Detector
OWNER:   Person B
============================================================

Detects phishing emails and SMS scam messages ("smishing")
using the Gemini AI model. Supports two threat types:
  - Email phishing detection
  - SMS/chat message scam detection
============================================================
"""

import json
from backend.services.gemini_service import get_gemini_client, get_model_id


# Different system prompts for each threat type
SYSTEM_PROMPTS = {
    "email": (
        "You are a cybersecurity expert specializing in phishing email detection. "
        "Analyze the given email content for phishing indicators: urgent language, "
        "credential requests, suspicious links, generic greetings, grammar errors. "
        "Return ONLY valid raw JSON in this format:\n"
        '{ "classification": "SAFE | SUSPICIOUS | DANGEROUS", '
        '"risk_score": number, "reasons": string[], "recommendation": "string" }'
    ),
    "message": (
        "You are a cybersecurity expert specializing in smishing (SMS phishing) detection. "
        "Analyze the given message for scam indicators: fake delivery alerts, "
        "urgent calls to action, shortened links, requests for personal info. "
        "Return ONLY valid raw JSON in this format:\n"
        '{ "classification": "SAFE | SUSPICIOUS | DANGEROUS", '
        '"risk_score": number, "reasons": string[], "recommendation": "string" }'
    ),
}


def analyze_email(content: str) -> dict:
    """
    Analyzes email content for phishing indicators.

    Args:
        content: The full email text to analyze.

    Returns:
        Dictionary with classification, risk_score, reasons, recommendation.
    """
    return _analyze(content, "email")


def analyze_message(content: str) -> dict:
    """
    Analyzes SMS/chat messages for smishing indicators.

    Args:
        content: The message text to analyze.

    Returns:
        Dictionary with classification, risk_score, reasons, recommendation.
    """
    return _analyze(content, "message")


def _analyze(content: str, threat_type: str) -> dict:
    """Shared analysis logic for both email and message threats."""
    client = get_gemini_client()

    prompt = SYSTEM_PROMPTS.get(threat_type, SYSTEM_PROMPTS["email"])

    response = client.models.generate_content(
        model=get_model_id(),
        contents=content,
        config={
            "response_mime_type": "application/json",
            "system_instruction": prompt,
        },
    )

    response_text = response.text
    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    result = json.loads(cleaned)

    return result
