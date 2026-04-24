"""
API Router: Security Analysis
Handles URL, Email, and Message analysis.
Owned by Person A (URL) and Person B (Email/Message).
"""

from fastapi import APIRouter, HTTPException
from backend.models.analysis import AnalysisRequest, AnalysisResponse
from backend.services.url_analyzer import analyze_url

router = APIRouter()


@router.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Analyzes a URL, email, or message for security risks.
    This is the same endpoint the React frontend calls.

    Request body: { "message": "text to analyze" }
    Response: { "classification", "risk_score", "reasons", "recommendation" }
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")

        result = analyze_url(request.message)
        return result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "classification": "ERROR",
                "risk_score": 100,
                "reasons": ["Backend failed: " + str(e)],
                "recommendation": "Please try again later."
            }
        )
