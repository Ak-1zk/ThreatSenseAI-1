"""
============================================================
SERVICE: QR Code Security Analyzer
============================================================

Decodes QR codes from uploaded images and analyzes the
embedded URL/content for security risks by piping the decoded
results into our custom-trained local URL ML classifier.
============================================================
"""

import re
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
    Analyzes a QR code image for security risks using OpenCV for fast programmatic decoding,
    with Gemini AI vision as a fallback. Pipes the result into our trained local ML models.
    
    Args:
        image_base64: Base64-encoded image string.
        
    Returns:
        Dictionary with decoded_content, classification, risk_score, reasons, recommendation.
    """
    # Strip dataURL prefix if present
    if "," in image_base64:
        image_base64 = image_base64.split(",", 1)[1]

    # Decode base64 to bytes
    image_bytes = base64.b64decode(image_base64)

    # 1. Try decoding using OpenCV first
    decoded_text = None
    try:
        import cv2
        import numpy as np
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            detector = cv2.QRCodeDetector()
            val, _, _ = detector.detectAndDecode(img)
            if val:
                raw_val = val.strip()
                # QR codes generated from pandas DataFrames may encode the full
                # Series string repr: e.g. "0  https://example.com\nName: url, dtype: object"
                # Extract just the URL if present, otherwise use the raw value.
                url_match = re.search(r'https?://[^\s]+', raw_val)
                if url_match:
                    decoded_text = url_match.group(0).rstrip('.')
                    if raw_val != decoded_text:
                        print(f"[INFO] Extracted URL from pandas-style QR content: '{decoded_text}'")
                else:
                    decoded_text = raw_val
                print(f"[INFO] Programmatic QR code decode successful using OpenCV: '{decoded_text}'")
    except Exception as e:
        print(f"[WARNING] OpenCV QR decoding failed: {e}")

    # 2. If OpenCV successfully decoded the content, analyze it
    if decoded_text:
        if decoded_text.startswith(("http://", "https://")) or ("." in decoded_text and " " not in decoded_text):
            from backend.services.url_analyzer import analyze_url
            try:
                print(f"[INFO] QR content looks like a URL. Piping into URL ML Analyzer...")
                result = analyze_url(decoded_text)
                result["decoded_content"] = decoded_text
                return result
            except Exception as e:
                print(f"[WARNING] Local QR URL assessment failed: {e}")
        else:
            from backend.services.threat_detector import analyze_message
            try:
                print(f"[INFO] QR content looks like text/message. Piping into Message ML Analyzer...")
                result = analyze_message(decoded_text)
                result["decoded_content"] = decoded_text
                return result
            except Exception as e:
                print(f"[WARNING] Local QR Message assessment failed: {e}")

    # 3. Fallback to Gemini vision decoding if OpenCV failed
    print("[INFO] OpenCV decoding failed or returned empty. Falling back to Gemini vision decoding...")
    client = get_gemini_client()
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
    response_text = response.text or ""
    if not response_text and response.candidates:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                response_text = part.text
                break
    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    result = json.loads(cleaned)

    # Pipe decoded URL into our high-accuracy URL ML analyzer
    decoded_url = result.get("decoded_content", "").strip()
    if decoded_url and ("." in decoded_url or "/" in decoded_url):
        from backend.services.url_analyzer import analyze_url
        try:
            print(f"[INFO] QR code decoded via Gemini: '{decoded_url}'. Piping into URL ML Analyzer...")
            url_result = analyze_url(decoded_url)
            
            # Update result with the highly accurate local ML prediction and Gemini reasons
            result["classification"] = url_result["classification"]
            result["risk_score"] = url_result["risk_score"]
            result["reasons"] = url_result["reasons"]
            result["recommendation"] = url_result["recommendation"]
        except Exception as e:
            print(f"[WARNING] Local QR URL assessment failed: {e}")

    return result

