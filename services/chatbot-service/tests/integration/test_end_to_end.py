import pytest
from unittest.mock import patch, MagicMock
import uuid

from app.db.models.conversation import Conversation, Message

@pytest.mark.asyncio
async def test_end_to_end_chat_flow(client, db_session, mock_llm_response, mock_healthcare_providers):
    """
    End-to-end test of the chat flow.
    
    This test simulates a complete conversation with the chatbot,
    including multiple messages and context preservation.
    """
    user_id = "test_user"
    
    # Mock the LLM service
    with patch("app.services.llm_service.process_message", return_value=("find_doctor", {"specialty": "cardiologist"})):
        # Mock the healthcare service
        with patch("app.services.healthcare_service.find_healthcare_providers", return_value=mock_healthcare_providers):
            # First message
            response1 = await client.post(
                "/api/v1/chat",
                json={
                    "user_id": user_id,
                    "message": "I need a cardiologist"
                }
            )
            
            # Check the response
            assert response1.status_code == 200
            data1 = response1.json()
            conversation_id = data1["conversation_id"]
            
            # Second message in the same conversation
            response2 = await client.post(
                "/api/v1/chat",
                json={
                    "user_id": user_id,
                    "message": "Show me the nearest one",
                    "conversation_id": conversation_id,
                    "location": {
                        "latitude": 19.0760,
                        "longitude": 72.8777,
                        "city": "Mumbai"
                    }
                }
            )
            
            # Check the response
            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["conversation_id"] == conversation_id
            
            # Verify that messages were saved to the database
            result = await db_session.execute(
                select(Message).where(Message.conversation_id == uuid.UUID(conversation_id))
            )
            messages = result.scalars().all()
            
            assert len(messages) == 4  # 2 user messages + 2 bot responses
            assert messages[0].role == "user"
            assert messages[0].content == "I need a cardiologist"
            assert messages[1].role == "assistant"
            assert messages[2].role == "user"
            assert messages[2].content == "Show me the nearest one"
            assert messages[3].role == "assistant"

@pytest.mark.asyncio
async def test_conversation_context_preservation(client, db_session):
    """Test that conversation context is preserved between messages."""
    user_id = "test_user"
    
    # First message - looking for a doctor
    with patch("app.services.llm_service.process_message", return_value=("find_doctor", {"specialty": "cardiologist"})):
        with patch("app.services.healthcare_service.find_healthcare_providers", return_value=[]):
            response1 = await client.post(
                "/api/v1/chat",
                json={
                    "user_id": user_id,
                    "message": "I need a cardiologist"
                }
            )
            
            data1 = response1.json()
            conversation_id = data1["conversation_id"]
    
    # Check that context was saved
    result = await db_session.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conversation = result.scalar_one()
    assert conversation.context["intent"] == "find_doctor"
    assert conversation.context["entities"]["specialty"] == "cardiologist"
    
    # Second message - should use the context from the first message
    with patch("app.services.llm_service.process_message") as mock_process:
        mock_process.return_value = ("find_doctor", {"specialty": "cardiologist", "location": "Mumbai"})
        
        with patch("app.services.healthcare_service.find_healthcare_providers", return_value=[]):
            response2 = await client.post(
                "/api/v1/chat",
                json={
                    "user_id": user_id,
                    "message": "in Mumbai",
                    "conversation_id": conversation_id
                }
            )
            
            # Verify that the context was passed to the LLM service
            context_arg = mock_process.call_args[0][1]
            assert context_arg["intent"] == "find_doctor"
            assert context_arg["entities"]["specialty"] == "cardiologist"

@pytest.mark.asyncio
async def test_health_check(client):
    """Test the health check endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data