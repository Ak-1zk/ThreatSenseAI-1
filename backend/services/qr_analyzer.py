"""
============================================================
SERVICE: QR Code Security Analyzer
============================================================

Decodes QR codes from uploaded images and analyzes the
embedded URL/content for security risks by piping the decoded
results into our custom-trained local URL ML classifier.
============================================================
"""

import json
import base64
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
    Analyzes a QR code image for security risks using Gemini AI vision for decoding,
    and our trained local ML model for URL safety assessment.
    
    Args:
        image_base64: Base64-encoded image string.
        
    Returns:
        Dictionary with decoded_content, classification, risk_score, reasons, recommendation.
    """
    client = get_gemini_client()

    # Strip dataURL prefix if present
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

    # Pipe decoded URL into our high-accuracy URL ML analyzer
    decoded_url = result.get("decoded_content", "").strip()
    if decoded_url and ("." in decoded_url or "/" in decoded_url):
        from backend.services.url_analyzer import analyze_url
        try:
            print(f"[INFO] QR code decoded: '{decoded_url}'. Piping into URL ML Analyzer...")
            url_result = analyze_url(decoded_url)
            
            # Update result with the highly accurate local ML prediction and Gemini reasons
            result["classification"] = url_result["classification"]
            result["risk_score"] = url_result["risk_score"]
            result["reasons"] = url_result["reasons"]
            result["recommendation"] = url_result["recommendation"]
        except Exception as e:
            print(f"[WARNING] Local QR URL assessment failed: {e}")

    return result
