import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.services.healthcare_service import find_healthcare_providers
from app.schemas.chat import Location, HealthcareProvider

@pytest.mark.asyncio
async def test_healthcare_service_integration():
    """
    Integration test for healthcare service.
    
    This test mocks the HTTP calls but tests the full flow of the find_healthcare_providers function,
    including error handling and response parsing.
    """
    # Mock the httpx client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": "123",
            "name": "Dr. John Doe",
            "specialty": "cardiologist",
            "address": "123 Main St",
            "city": "Mumbai",
            "state": "Maharashtra",
            "rating": 4.5,
            "distance": 2.5
        },
        {
            "id": "456",
            "name": "Dr. Jane Smith",
            "specialty": "cardiologist",
            "address": "456 Oak St",
            "city": "Mumbai",
            "state": "Maharashtra",
            "rating": 4.8,
            "distance": 3.2
        }
    ]
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        # Call the function
        intent = "find_doctor"
        entities = {"specialty": "cardiologist"}
        location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
        
        providers = await find_healthcare_providers(intent, entities, location, "user123")
        
        # Check the results
        assert len(providers) == 2
        assert providers[0].name == "Dr. John Doe"
        assert providers[0].specialty == "cardiologist"
        assert providers[0].city == "Mumbai"
        assert providers[1].name == "Dr. Jane Smith"

@pytest.mark.asyncio
async def test_healthcare_service_with_different_intents():
    """Test the healthcare service with different intents."""
    # Mock responses for different services
    mock_responses = {
        "find_doctor": [{"id": "123", "name": "Dr. John Doe", "specialty": "cardiologist"}],
        "find_hospital": [{"id": "456", "name": "City Hospital", "type": "hospital"}],
        "find_lab": [{"id": "789", "name": "City Lab", "type": "lab"}],
        "find_pharmacy": [{"id": "012", "name": "City Pharmacy", "type": "pharmacy"}],
        "find_ayush": [{"id": "345", "name": "Ayurveda Center", "type": "ayush"}]
    }
    
    # Test each intent
    for intent, mock_data in mock_responses.items():
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            # Call the function
            entities = {}
            location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
            
            providers = await find_healthcare_providers(intent, entities, location, "user123")
            
            # Check the results
            assert len(providers) == 1
            assert providers[0].name == mock_data[0]["name"]
            assert providers[0].type == mock_data[0].get("type", "doctor")

@pytest.mark.asyncio
async def test_healthcare_service_error_handling():
    """Test error handling in the healthcare service."""
    # Mock the httpx client to raise an exception
    with patch("httpx.AsyncClient.get", side_effect=httpx.RequestError("Connection error")):
        # Call the function
        intent = "find_doctor"
        entities = {"specialty": "cardiologist"}
        location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
        
        providers = await find_healthcare_providers(intent, entities, location, "user123")
        
        # Should return empty list on error
        assert providers == []

@pytest.mark.asyncio
async def test_healthcare_service_bad_response():
    """Test handling of bad response from healthcare service."""
    # Mock the httpx client
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        # Call the function
        intent = "find_doctor"
        entities = {"specialty": "cardiologist"}
        location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
        
        providers = await find_healthcare_providers(intent, entities, location, "user123")
        
        # Should return empty list on error
        assert providers == []