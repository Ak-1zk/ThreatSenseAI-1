"""
API Router: Daily Threat Briefing
Generates a daily cybersecurity briefing.
Owned by Person D.
"""

from fastapi import APIRouter
from backend.services.briefing_service import generate_daily_briefing

router = APIRouter()


@router.get("/daily-briefing")
async def daily_briefing():
    """
    Generates a daily cybersecurity threat briefing.

    Response: { "briefing": "Markdown text..." }
    """
    try:
        briefing = generate_daily_briefing()
        return {"briefing": briefing}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error generating briefing: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"briefing": "Backend failed: " + str(e)}
        )
