import pytest
import httpx
from unittest.mock import patch, MagicMock

from app.services.healthcare_service import (
    find_healthcare_providers,
    find_doctors,
    find_hospitals,
    find_labs,
    find_pharmacies,
    find_ayush_practitioners
)
from app.schemas.chat import Location

@pytest.mark.asyncio
async def test_find_healthcare_providers_doctor():
    """Test finding healthcare providers for doctors."""
    intent = "find_doctor"
    entities = {"specialty": "cardiologist"}
    location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
    
    # Mock the find_doctors function
    with patch("app.services.healthcare_service.find_doctors") as mock_find:
        mock_find.return_value = [
            {
                "id": "123",
                "name": "Dr. John Doe",
                "type": "doctor",
                "specialty": "cardiologist"
            }
        ]
        
        result = await find_healthcare_providers(intent, entities, location, "user123")
        
        mock_find.assert_called_once_with(entities, location, "user123")
        assert len(result) == 1
        assert result[0]["name"] == "Dr. John Doe"

@pytest.mark.asyncio
async def test_find_healthcare_providers_hospital():
    """Test finding healthcare providers for hospitals."""
    intent = "find_hospital"
    entities = {}
    location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
    
    # Mock the find_hospitals function
    with patch("app.services.healthcare_service.find_hospitals") as mock_find:
        mock_find.return_value = [
            {
                "id": "456",
                "name": "City Hospital",
                "type": "hospital"
            }
        ]
        
        result = await find_healthcare_providers(intent, entities, location, "user123")
        
        mock_find.assert_called_once_with(entities, location, "user123")
        assert len(result) == 1
        assert result[0]["name"] == "City Hospital"

@pytest.mark.asyncio
async def test_find_doctors():
    """Test finding doctors."""
    entities = {"specialty": "cardiologist"}
    location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
    
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
            "rating": 4.5,
            "distance": 2.5
        }
    ]
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await find_doctors(entities, location, "user123")
        
        assert len(result) == 1
        assert result[0].name == "Dr. John Doe"
        assert result[0].specialty == "cardiologist"

@pytest.mark.asyncio
async def test_find_doctors_error():
    """Test error handling when finding doctors."""
    entities = {"specialty": "cardiologist"}
    location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
    
    # Mock the httpx client to raise an exception
    with patch("httpx.AsyncClient.get", side_effect=httpx.RequestError("Connection error")):
        result = await find_doctors(entities, location, "user123")
        
        # Should return empty list on error
        assert result == []

@pytest.mark.asyncio
async def test_find_doctors_bad_response():
    """Test handling of bad response when finding doctors."""
    entities = {"specialty": "cardiologist"}
    location = Location(latitude=19.0760, longitude=72.8777, city="Mumbai")
    
    # Mock the httpx client
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await find_doctors(entities, location, "user123")
        
        # Should return empty list on error
        assert result == []