"""
============================================================
API ROUTER: Security Analysis
OWNER:      Person A & Person B
============================================================

Handles URL, Email, and Message analysis requests.
Dynamically routes requests to their corresponding custom-trained
ML analyzers based on prompt structure or text content heuristics.
============================================================
"""

import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.models.analysis import AnalysisRequest
from backend.services.url_analyzer import analyze_url
from backend.services.threat_detector import analyze_email, analyze_message

router = APIRouter()

@router.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Analyzes a URL, email, or message for security risks.
    Smart-routes the request to the specialized local ML + Gemini hybrid analyzer.
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message/Content is required")

        text = request.message.strip()
        print(f"[INFO] [Router] Incoming analysis request: '{text[:60]}...'")

        # Dynamic routing based on frontend prompt envelopes
        if text.lower().startswith("analyze this url"):
            print("  --> Routed to: URL Analyzer")
            result = analyze_url(text)
            
        elif text.lower().startswith("analyze this email"):
            print("  --> Routed to: Email Threat Detector")
            result = analyze_email(text)
            
        elif text.lower().startswith("analyze this message"):
            print("  --> Routed to: Message/SMS Threat Detector")
            result = analyze_message(text)
            
        else:
            # Heuristic routing based on raw content shape
            # Check if it looks like a URL (starts with http/https or contains common TLDs)
            url_pattern = r"(https?://[^\s]+)|(^[a-zA-Z0-9][-a-zA-Z0-9.]*\.(com|net|org|edu|gov|mil|biz|info|io|co|me|xyz|info|us|tv|cc|ws|mobi|app|dev|sh|kr|in|br)(/[^\s]*)?$)"
            if re.search(url_pattern, text, re.IGNORECASE):
                print("  --> Heuristically Routed to: URL Analyzer")
                result = analyze_url(text)
            else:
                # If it's a block of text, check size; large blocks default to Email, short blocks to Message/SMS
                if len(text) > 200:
                    print("  --> Heuristically Routed to: Email Threat Detector")
                    result = analyze_email(text)
                else:
                    print("  --> Heuristically Routed to: Message/SMS Threat Detector")
                    result = analyze_message(text)

        return result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "classification": "ERROR",
                "risk_score": 100,
                "reasons": [f"Backend routing/analysis failure: {str(e)}"],
                "recommendation": "System experienced an error. Please try again."
            }
        )
