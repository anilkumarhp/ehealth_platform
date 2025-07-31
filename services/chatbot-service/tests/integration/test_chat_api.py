import pytest
import uuid
from unittest.mock import patch

from app.db.models.conversation import Conversation, Message
from app.services.llm_service import process_message
from app.services.healthcare_service import find_healthcare_providers

@pytest.mark.asyncio
async def test_chat_endpoint(client, mock_llm_response, mock_healthcare_providers):
    """Test the chat endpoint."""
    # Mock the LLM service
    with patch("app.api.v1.routers.chat.process_message", return_value=("find_doctor", {"specialty": "cardiologist"})):
        # Mock the healthcare service
        with patch("app.api.v1.routers.chat.find_healthcare_providers", return_value=mock_healthcare_providers):
            # Send a chat message
            response = await client.post(
                "/api/v1/chat",
                json={
                    "user_id": "test_user",
                    "message": "I need a cardiologist",
                    "location": {
                        "latitude": 19.0760,
                        "longitude": 72.8777,
                        "city": "Mumbai"
                    }
                }
            )
            
            # Check the response
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "suggestions" in data
            assert "healthcare_providers" in data
            assert "conversation_id" in data
            
            # Check the healthcare providers
            assert len(data["healthcare_providers"]) == 2
            assert data["healthcare_providers"][0]["name"] == "Dr. John Doe"
            assert data["healthcare_providers"][0]["specialty"] == "cardiologist"

@pytest.mark.asyncio
async def test_chat_endpoint_with_existing_conversation(client, mock_llm_response):
    """Test the chat endpoint with an existing conversation."""
    # Create a conversation
    conversation_id = str(uuid.uuid4())
    
    # Mock the LLM service
    with patch("app.api.v1.routers.chat.process_message", return_value=("find_doctor", {"specialty": "cardiologist"})):
        # Mock the healthcare service
        with patch("app.api.v1.routers.chat.find_healthcare_providers", return_value=[]):
            # Mock the get_or_create_conversation function
            with patch("app.api.v1.routers.chat.get_or_create_conversation") as mock_get_conversation:
                # Setup mock conversation
                mock_conversation = Conversation(id=uuid.UUID(conversation_id), user_id="test_user", context={})
                mock_get_conversation.return_value = mock_conversation
                
                # Send a chat message
                response = await client.post(
                    "/api/v1/chat",
                    json={
                        "user_id": "test_user",
                        "message": "I need a cardiologist",
                        "conversation_id": conversation_id
                    }
                )
                
                # Check the response
                assert response.status_code == 200
                data = response.json()
                assert data["conversation_id"] == conversation_id

@pytest.mark.asyncio
async def test_chat_endpoint_error_handling(client):
    """Test error handling in the chat endpoint."""
    # Mock the LLM service to raise an exception
    with patch("app.api.v1.routers.chat.process_message", side_effect=Exception("Test error")):
        # Send a chat message
        response = await client.post(
            "/api/v1/chat",
            json={
                "user_id": "test_user",
                "message": "I need a cardiologist"
            }
        )
        
        # Check the response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

@pytest.mark.asyncio
async def test_chat_endpoint_invalid_conversation_id(client):
    """Test the chat endpoint with an invalid conversation ID."""
    # Send a chat message with an invalid conversation ID
    response = await client.post(
        "/api/v1/chat",
        json={
            "user_id": "test_user",
            "message": "I need a cardiologist",
            "conversation_id": "invalid-uuid"
        }
    )
    
    # Check the response - should create a new conversation
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["conversation_id"] != "invalid-uuid"