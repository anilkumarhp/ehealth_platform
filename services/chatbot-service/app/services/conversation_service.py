from typing import Dict, List, Optional, Any
from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.models.conversation import Conversation, Message
from app.core.exceptions import ConversationNotFoundException

logger = structlog.get_logger(__name__)

async def get_or_create_conversation(
    db: AsyncSession, 
    user_id: str, 
    conversation_id: Optional[str] = None
) -> Conversation:
    """Get or create a conversation"""
    if conversation_id:
        try:
            # Try to get existing conversation
            stmt = select(Conversation).where(
                Conversation.id == UUID(conversation_id),
                Conversation.user_id == user_id
            )
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                raise ConversationNotFoundException(conversation_id)
                
            return conversation
        except ValueError:
            # Invalid UUID
            logger.warning("invalid_conversation_id", conversation_id=conversation_id)
            # Fall through to create new conversation
    
    # Create new conversation
    conversation = Conversation(user_id=user_id, context={})
    db.add(conversation)
    await db.flush()
    
    return conversation

async def get_conversation_messages(
    db: AsyncSession, 
    conversation_id: UUID, 
    limit: int = 10
) -> List[Message]:
    """Get messages for a conversation"""
    stmt = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(desc(Message.created_at)).limit(limit)
    
    result = await db.execute(stmt)
    return list(reversed(result.scalars().all()))

async def get_conversation_context(
    db: AsyncSession, 
    conversation_id: UUID
) -> Dict[str, Any]:
    """Get conversation context"""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        return {}
        
    return conversation.context or {}

async def update_conversation_context(
    db: AsyncSession, 
    conversation_id: UUID, 
    intent: str, 
    entities: Dict[str, Any]
) -> None:
    """Update conversation context"""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise ConversationNotFoundException(str(conversation_id))
        
    # Update context
    context = conversation.context or {}
    context.update({
        "intent": intent,
        "entities": entities,
        "last_updated": str(conversation.updated_at)
    })
    
    conversation.context = context
    db.add(conversation)
    await db.flush()

async def get_user_conversations(
    db: AsyncSession, 
    user_id: str, 
    limit: int = 10
) -> List[Conversation]:
    """Get conversations for a user"""
    stmt = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(desc(Conversation.updated_at)).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_conversation_summary(
    db: AsyncSession, 
    conversation_id: UUID
) -> str:
    """Get a summary of the conversation"""
    # Get the first and last message
    first_msg_stmt = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).limit(1)
    
    last_msg_stmt = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(desc(Message.created_at)).limit(1)
    
    first_result = await db.execute(first_msg_stmt)
    last_result = await db.execute(last_msg_stmt)
    
    first_message = first_result.scalar_one_or_none()
    last_message = last_result.scalar_one_or_none()
    
    if not first_message:
        return "Empty conversation"
        
    # Count messages
    count_stmt = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    count_result = await db.execute(count_stmt)
    message_count = count_result.scalar_one()
    
    # Create summary
    if first_message == last_message:
        return f"Conversation with {message_count} message"
    
    return f"Conversation with {message_count} messages, starting with '{first_message.content[:30]}...'"