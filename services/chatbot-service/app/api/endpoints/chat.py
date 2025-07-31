from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional
from pydantic import BaseModel
import logging
from app.services.chat_service import chat_service

router = APIRouter()
logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    intent: Optional[str] = None
    requires_auth: Optional[bool] = False
    hospitals: Optional[List[dict]] = None
    doctors: Optional[List[dict]] = None
    slots: Optional[List[dict]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    """
    Process a chat request and generate a response.
    """
    try:
        # Extract token if provided
        token = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
        
        # Convert Pydantic models to dictionaries
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get the latest user message
        latest_user_message = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), "")
        
        # Process the message
        result = await chat_service.process_message(latest_user_message, messages, token)
        
        return ChatResponse(
            response=result["response"],
            conversation_id=request.conversation_id,
            intent=result.get("intent"),
            requires_auth=result.get("requires_auth", False),
            hospitals=result.get("hospitals"),
            doctors=result.get("doctors"),
            slots=result.get("slots")
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}