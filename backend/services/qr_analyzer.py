"""
============================================================
SERVICE: QR Code Security Analyzer
============================================================

Decodes QR codes from uploaded images and analyzes the
embedded URL/content for security risks using Gemini AI.
Supports base64-encoded image input.
============================================================
"""

import json
import base64
import io
import re

from backend.services.gemini_service import get_gemini_client, get_model_id


SYSTEM_PROMPT = (
    "You are a cybersecurity expert specializing in QR code security (Quishing). "
    "You have been given a QR code image. First, decode the content of the QR code. "
    "Then analyze the decoded content (usually a URL) for security risks including: "
    "phishing links, malicious redirects, credential harvesting, malware distribution, "
    "and social engineering tactics. "
    "Return ONLY valid raw JSON (no markdown, no explanation) in this format:\n"
    '{ "decoded_content": "the decoded QR text/URL", '
    '"classification": "SAFE | SUSPICIOUS | DANGEROUS", '
    '"risk_score": number, "reasons": string[], "recommendation": "string" }'
)


def analyze_qr_code(image_base64: str) -> dict:
    """
    Analyzes a QR code image for security risks using Gemini AI vision.

    Args:
        image_base64: Base64-encoded image string (may include data:image/... prefix).

    Returns:
        Dictionary with decoded_content, classification, risk_score, reasons, recommendation.
    """
    client = get_gemini_client()

    # Strip dataURL prefix if present (e.g. "data:image/png;base64,...")
    if "," in image_base64:
        image_base64 = image_base64.split(",", 1)[1]

    # Decode base64 to bytes
    image_bytes = base64.b64decode(image_base64)

    from google.genai import types

    response = client.models.generate_content(
        model=get_model_id(),
        contents=[
            types.Content(
                parts=[
                    types.Part.from_text(text="Analyze this QR code image for security risks. Decode the QR code content and assess if it is safe."),
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                ]
            )
        ],
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
