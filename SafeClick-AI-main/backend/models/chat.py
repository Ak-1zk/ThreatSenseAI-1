"""
Pydantic models for the AI chatbot.
Used by Person C (Chatbot).
"""

from pydantic import BaseModel
from typing import List, Optional


class ChatPart(BaseModel):
    text: str


class ChatHistoryItem(BaseModel):
    role: str  # "user" or "model"
    parts: List[ChatPart]


class ChatRequest(BaseModel):
    """Request body for the /api/chat endpoint."""
    message: str
    history: Optional[List[ChatHistoryItem]] = []


class ChatResponse(BaseModel):
    """Response from the chatbot — same JSON shape the frontend expects."""
    reply: str
