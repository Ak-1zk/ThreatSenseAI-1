"""
ThreatSense AI — Python Backend (FastAPI)

This is the main entry point for the Python backend.
It creates the FastAPI app, adds CORS middleware (so the
React frontend can call it), and registers all API routes.

To run:
    cd ThreatSense-AI
    uvicorn backend.main:app --reload --port 8000
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from backend.routers import analyze, chat, daily_briefing, qr_scan

# Create the FastAPI app
app = FastAPI(
    title="ThreatSense AI Backend",
    description="Python backend for cybersecurity analysis powered by Gemini AI",
    version="1.0.0",
)

# Allow cross-origin requests (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes — all prefixed with /api
app.include_router(analyze.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(daily_briefing.router, prefix="/api")
app.include_router(qr_scan.router, prefix="/api")


@app.get("/")
async def root():
    """Redirect root to the frontend login page."""
    return RedirectResponse(url="/index.html")


# Serve the frontend static files (must be last, after API routes)
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
