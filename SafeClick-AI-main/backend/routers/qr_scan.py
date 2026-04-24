"""
API Router: QR Code Security Analysis
Handles QR code image uploads and security analysis.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.qr_analyzer import analyze_qr_code

router = APIRouter()


class QRScanRequest(BaseModel):
    """Request body for the /api/qr-scan endpoint."""
    image: str  # base64-encoded image data


@router.post("/qr-scan")
async def qr_scan(request: QRScanRequest):
    """
    Analyzes a QR code image for security risks.

    Request body: { "image": "base64-encoded-image-data" }
    Response: {
        "decoded_content": "...",
        "classification": "SAFE | SUSPICIOUS | DANGEROUS",
        "risk_score": number,
        "reasons": [...],
        "recommendation": "..."
    }
    """
    try:
        if not request.image:
            raise HTTPException(status_code=400, detail="Image data is required")

        result = analyze_qr_code(request.image)
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
                "decoded_content": "Unable to decode",
                "classification": "ERROR",
                "risk_score": 100,
                "reasons": ["Backend failed: " + str(e)],
                "recommendation": "Please try again later."
            }
        )
