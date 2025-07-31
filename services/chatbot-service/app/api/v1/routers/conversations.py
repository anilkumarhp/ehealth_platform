from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import structlog

from app.db.base import get_db
from app.schemas.chat import ConversationResponse, ConversationSummary, MessageResponse
from app.services.conversation_service import (
    get_user_conversations,
    get_conversation_messages,
    get_conversation_summary
)
from app.core.exceptions import ConversationNotFoundException

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/user/{user_id}", response_model=List[ConversationSummary])
async def get_conversations_for_user(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get conversations for a user"""
    try:
        conversations = await get_user_conversations(db, user_id, limit)
        
        return [
            ConversationSummary(
                id=str(conv.id),
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                summary=await get_conversation_summary(db, conv.id)
            )
            for conv in conversations
        ]
    except Exception as e:
        logger.error("get_conversations_error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a conversation by ID"""
    try:
        # Get conversation
        stmt = select(Conversation).where(Conversation.id == UUID(conversation_id))
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ConversationNotFoundException(conversation_id)
        
        # Get messages
        messages = await get_conversation_messages(db, conversation.id)
        
        return ConversationResponse(
            id=str(conversation.id),
            user_id=conversation.user_id,
            context=conversation.context,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                MessageResponse(
                    id=str(msg.id),
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at
                )
                for msg in messages
            ]
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    except ConversationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("get_conversation_error", conversation_id=conversation_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")