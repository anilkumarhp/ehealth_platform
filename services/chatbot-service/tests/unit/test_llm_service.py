import pytest
import httpx
from unittest.mock import patch, MagicMock

from app.services.llm_service import process_message, fallback_intent_detection
from app.core.exceptions import LLMServiceException

@pytest.mark.asyncio
async def test_process_message_success():
    """Test successful processing of a message."""
    # Mock the httpx client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "intent": "find_doctor",
        "entities": {"specialty": "cardiologist"},
        "confidence": 0.9
    }
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        intent, entities = await process_message("I need a cardiologist")
        
        assert intent == "find_doctor"
        assert entities == {"specialty": "cardiologist"}

@pytest.mark.asyncio
async def test_process_message_error():
    """Test error handling in message processing."""
    # Mock the httpx client to raise an exception
    with patch("httpx.AsyncClient.post", side_effect=httpx.RequestError("Connection error")):
        with pytest.raises(LLMServiceException):
            await process_message("I need a doctor")

@pytest.mark.asyncio
async def test_process_message_bad_response():
    """Test handling of bad response from LLM service."""
    # Mock the httpx client
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with pytest.raises(LLMServiceException):
            await process_message("I need a doctor")

def test_fallback_intent_detection():
    """Test the fallback intent detection."""
    # Test doctor intent
    intent, entities = fallback_intent_detection("I need a cardiologist")
    assert intent == "find_doctor"
    assert entities.get("specialty") == "cardiologist"
    
    # Test hospital intent
    intent, entities = fallback_intent_detection("Looking for a hospital")
    assert intent == "find_hospital"
    
    # Test lab intent
    intent, entities = fallback_intent_detection("I need a blood test")
    assert intent == "find_lab"
    
    # Test pharmacy intent
    intent, entities = fallback_intent_detection("Where can I get medicine?")
    assert intent == "find_pharmacy"
    
    # Test emergency intent
    intent, entities = fallback_intent_detection("This is an emergency")
    assert intent == "emergency_advice"
    
    # Test ayush intent
    intent, entities = fallback_intent_detection("I need an ayurveda doctor")
    assert intent == "find_ayush"
    assert entities.get("type") == "ayurveda"
    
    # Test general intent
    intent, entities = fallback_intent_detection("Hello")
    assert intent == "general_info"