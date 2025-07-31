import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.services.llm_service import process_message
from app.core.exceptions import LLMServiceException

@pytest.mark.asyncio
async def test_llm_service_integration():
    """
    Integration test for LLM service.
    
    This test mocks the HTTP call but tests the full flow of the process_message function,
    including error handling, retries, and response parsing.
    """
    # Mock the httpx client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "intent": "find_doctor",
        "entities": {"specialty": "cardiologist", "location": "Mumbai"},
        "confidence": 0.9
    }
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        # Call the function with a message and context
        context = {"previous_intent": "greeting"}
        intent, entities = await process_message(
            "I need a cardiologist in Mumbai",
            context
        )
        
        # Check the results
        assert intent == "find_doctor"
        assert entities["specialty"] == "cardiologist"
        assert entities["location"] == "Mumbai"

@pytest.mark.asyncio
async def test_llm_service_retry_mechanism():
    """Test the retry mechanism of the LLM service."""
    # Create a side effect that fails twice then succeeds
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "intent": "find_doctor",
        "entities": {"specialty": "cardiologist"},
        "confidence": 0.9
    }
    
    # First two calls raise an exception, third call succeeds
    side_effects = [
        httpx.RequestError("Connection error"),
        httpx.RequestError("Connection error"),
        mock_response
    ]
    
    with patch("httpx.AsyncClient.post", side_effect=side_effects):
        # Call the function
        intent, entities = await process_message("I need a cardiologist")
        
        # Check the results
        assert intent == "find_doctor"
        assert entities["specialty"] == "cardiologist"

@pytest.mark.asyncio
async def test_llm_service_max_retries_exceeded():
    """Test that the LLM service raises an exception after max retries."""
    # Create a side effect that always fails
    with patch("httpx.AsyncClient.post", side_effect=httpx.RequestError("Connection error")):
        # Call the function
        with pytest.raises(LLMServiceException):
            await process_message("I need a cardiologist")

@pytest.mark.asyncio
async def test_llm_service_invalid_json():
    """Test handling of invalid JSON response from LLM service."""
    # Mock the httpx client to return invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        # Call the function
        with pytest.raises(LLMServiceException):
            await process_message("I need a cardiologist")