"""
API Router: AI Chatbot
Handles conversational messages with chat history.
Owned by Person C.
"""

from fastapi import APIRouter, HTTPException
from backend.models.chat import ChatRequest, ChatResponse
from backend.services.chatbot_service import get_chat_response

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Sends a message to the Aegis AI chatbot and returns a response.
    This is the same endpoint the React frontend calls.

    Request body: { "message": "user text", "history": [...] }
    Response: { "reply": "AI response text" }
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Convert Pydantic models to dicts for the service
        history = []
        if request.history:
            history = [item.model_dump() for item in request.history]

        reply = get_chat_response(request.message, history)
        return ChatResponse(reply=reply)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"reply": "Backend failed: " + str(e)}
        )
