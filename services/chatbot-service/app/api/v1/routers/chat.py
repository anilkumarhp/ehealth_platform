from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import structlog

from app.db.base import get_db
from app.schemas.chat import ChatMessage, ChatResponse, HealthcareProvider
from app.services.llm_service import process_message
from app.services.healthcare_service import find_healthcare_providers
from app.services.conversation_service import (
    get_or_create_conversation, 
    get_conversation_context,
    update_conversation_context
)
from app.services.response_service import generate_response
from app.core.exceptions import LLMServiceException, ConversationNotFoundException

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(
    message: ChatMessage, 
    db: AsyncSession = Depends(get_db)
):
    """Process chat message and return response"""
    try:
        # Get or create conversation
        conversation = await get_or_create_conversation(
            db, 
            message.user_id, 
            message.conversation_id
        )
        
        # Save user message
        db_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=message.message
        )
        db.add(db_message)
        await db.flush()
        
        # Get conversation context
        context = await get_conversation_context(db, conversation.id)
        
        # Process with LLM
        try:
            intent, entities = await process_message(message.message, context)
        except LLMServiceException:
            # Fallback to rule-based intent detection
            intent, entities = fallback_intent_detection(message.message)
        
        # Generate response based on intent
        response_text, suggestions = generate_response(intent, entities)
        
        # Find healthcare providers if needed
        providers = []
        if intent in ["find_doctor", "find_hospital", "find_lab", "find_pharmacy", "find_ayush"]:
            providers = await find_healthcare_providers(
                intent, 
                entities, 
                message.location,
                message.user_id
            )
        
        # Save bot response
        bot_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text
        )
        db.add(bot_message)
        
        # Update conversation context
        await update_conversation_context(db, conversation.id, intent, entities)
        
        # Commit changes
        await db.commit()
        
        return ChatResponse(
            message=response_text,
            suggestions=suggestions,
            healthcare_providers=providers,
            conversation_id=str(conversation.id)
        )
    except ConversationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("chat_error", error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while processing your message")