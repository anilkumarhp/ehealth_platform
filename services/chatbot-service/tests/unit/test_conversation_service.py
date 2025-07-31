import pytest
import uuid
from unittest.mock import MagicMock
from sqlalchemy import select

from app.db.models.conversation import Conversation, Message
from app.services.conversation_service import (
    get_or_create_conversation,
    get_conversation_messages,
    get_conversation_context,
    update_conversation_context,
    get_user_conversations
)
from app.core.exceptions import ConversationNotFoundException

@pytest.mark.asyncio
async def test_get_or_create_conversation_new(db_session):
    """Test creating a new conversation."""
    user_id = "test_user"
    
    conversation = await get_or_create_conversation(db_session, user_id)
    
    assert conversation is not None
    assert conversation.user_id == user_id
    assert conversation.context == {}
    
    # Verify it was saved to the database
    result = await db_session.execute(select(Conversation).where(Conversation.user_id == user_id))
    db_conversation = result.scalar_one_or_none()
    assert db_conversation is not None
    assert db_conversation.id == conversation.id

@pytest.mark.asyncio
async def test_get_or_create_conversation_existing(db_session):
    """Test getting an existing conversation."""
    user_id = "test_user"
    conversation_id = uuid.uuid4()
    
    # Create a conversation first
    conversation = Conversation(id=conversation_id, user_id=user_id, context={})
    db_session.add(conversation)
    await db_session.commit()
    
    # Now try to get it
    retrieved_conversation = await get_or_create_conversation(db_session, user_id, str(conversation_id))
    
    assert retrieved_conversation is not None
    assert retrieved_conversation.id == conversation_id
    assert retrieved_conversation.user_id == user_id

@pytest.mark.asyncio
async def test_get_or_create_conversation_not_found(db_session):
    """Test getting a non-existent conversation."""
    user_id = "test_user"
    conversation_id = str(uuid.uuid4())
    
    # Try to get a conversation that doesn't exist
    with pytest.raises(ConversationNotFoundException):
        await get_or_create_conversation(db_session, user_id, conversation_id)

@pytest.mark.asyncio
async def test_get_conversation_messages(db_session):
    """Test getting messages for a conversation."""
    # Create a conversation
    conversation = Conversation(user_id="test_user", context={})
    db_session.add(conversation)
    await db_session.flush()
    
    # Add some messages
    messages = [
        Message(conversation_id=conversation.id, role="user", content="Hello"),
        Message(conversation_id=conversation.id, role="assistant", content="Hi there"),
        Message(conversation_id=conversation.id, role="user", content="How are you?")
    ]
    db_session.add_all(messages)
    await db_session.commit()
    
    # Get the messages
    retrieved_messages = await get_conversation_messages(db_session, conversation.id)
    
    assert len(retrieved_messages) == 3
    assert retrieved_messages[0].content == "Hello"
    assert retrieved_messages[1].content == "Hi there"
    assert retrieved_messages[2].content == "How are you?"

@pytest.mark.asyncio
async def test_get_conversation_context(db_session):
    """Test getting conversation context."""
    # Create a conversation with context
    context = {"intent": "find_doctor", "entities": {"specialty": "cardiologist"}}
    conversation = Conversation(user_id="test_user", context=context)
    db_session.add(conversation)
    await db_session.commit()
    
    # Get the context
    retrieved_context = await get_conversation_context(db_session, conversation.id)
    
    assert retrieved_context == context
    assert retrieved_context["intent"] == "find_doctor"
    assert retrieved_context["entities"]["specialty"] == "cardiologist"

@pytest.mark.asyncio
async def test_update_conversation_context(db_session):
    """Test updating conversation context."""
    # Create a conversation
    conversation = Conversation(user_id="test_user", context={})
    db_session.add(conversation)
    await db_session.commit()
    
    # Update the context
    intent = "find_doctor"
    entities = {"specialty": "cardiologist"}
    await update_conversation_context(db_session, conversation.id, intent, entities)
    
    # Verify the context was updated
    result = await db_session.execute(select(Conversation).where(Conversation.id == conversation.id))
    updated_conversation = result.scalar_one_or_none()
    
    assert updated_conversation.context["intent"] == intent
    assert updated_conversation.context["entities"] == entities

@pytest.mark.asyncio
async def test_get_user_conversations(db_session):
    """Test getting conversations for a user."""
    user_id = "test_user"
    
    # Create some conversations
    conversations = [
        Conversation(user_id=user_id, context={}),
        Conversation(user_id=user_id, context={}),
        Conversation(user_id="other_user", context={})
    ]
    db_session.add_all(conversations)
    await db_session.commit()
    
    # Get the conversations
    user_conversations = await get_user_conversations(db_session, user_id)
    
    assert len(user_conversations) == 2
    assert all(conv.user_id == user_id for conv in user_conversations)