"""
Pydantic models for security analysis (URL, Email, Message).
Used by Person A (URL) and Person B (Email/Message).
"""

from pydantic import BaseModel
from enum import Enum
from typing import List, Optional


class Classification(str, Enum):
    GENUINE = "GENUINE"
    SUSPICIOUS = "SUSPICIOUS"
    SCAM = "SCAM"
    DANGEROUS = "DANGEROUS"
    SAFE = "SAFE"
    ERROR = "ERROR"


class AnalysisRequest(BaseModel):
    """Request body for the /api/analyze endpoint."""
    message: str


class AnalysisResponse(BaseModel):
    """Response from AI analysis — same JSON shape the frontend expects."""
    classification: str
    risk_score: int
    reasons: List[str]
    recommendation: str
