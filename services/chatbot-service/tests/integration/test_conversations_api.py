import pytest
import uuid
from sqlalchemy import select

from app.db.models.conversation import Conversation, Message

@pytest.mark.asyncio
async def test_get_conversations_for_user(client, db_session):
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
    response = await client.get(f"/api/v1/conversations/user/{user_id}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(conv["id"] for conv in data)
    assert all("summary" in conv for conv in data)

@pytest.mark.asyncio
async def test_get_conversation(client, db_session):
    """Test getting a conversation by ID."""
    user_id = "test_user"
    
    # Create a conversation
    conversation = Conversation(user_id=user_id, context={})
    db_session.add(conversation)
    await db_session.flush()
    
    # Add some messages
    messages = [
        Message(conversation_id=conversation.id, role="user", content="Hello"),
        Message(conversation_id=conversation.id, role="assistant", content="Hi there")
    ]
    db_session.add_all(messages)
    await db_session.commit()
    
    # Get the conversation
    response = await client.get(f"/api/v1/conversations/{conversation.id}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(conversation.id)
    assert data["user_id"] == user_id
    assert len(data["messages"]) == 2
    assert data["messages"][0]["content"] == "Hello"
    assert data["messages"][1]["content"] == "Hi there"

@pytest.mark.asyncio
async def test_get_conversation_not_found(client):
    """Test getting a non-existent conversation."""
    conversation_id = str(uuid.uuid4())
    
    # Get the conversation
    response = await client.get(f"/api/v1/conversations/{conversation_id}")
    
    # Check the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_get_conversation_invalid_id(client):
    """Test getting a conversation with an invalid ID."""
    # Get the conversation
    response = await client.get("/api/v1/conversations/invalid-uuid")
    
    # Check the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_get_conversations_empty(client):
    """Test getting conversations for a user with no conversations."""
    user_id = "user_with_no_conversations"
    
    # Get the conversations
    response = await client.get(f"/api/v1/conversations/user/{user_id}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0