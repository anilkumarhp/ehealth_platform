import pytest

from app.services.response_service import (
    generate_response,
    generate_doctor_response,
    generate_hospital_response,
    generate_lab_response,
    generate_pharmacy_response,
    generate_ayush_response,
    generate_emergency_response,
    generate_general_response
)

def test_generate_response_doctor():
    """Test generating response for finding doctors."""
    intent = "find_doctor"
    entities = {"specialty": "cardiologist"}
    
    response, suggestions = generate_response(intent, entities)
    
    assert "cardiologist" in response
    assert len(suggestions) > 0
    assert any("cardiologist" in suggestion for suggestion in suggestions)

def test_generate_response_hospital():
    """Test generating response for finding hospitals."""
    intent = "find_hospital"
    entities = {"specialty": "cardiac"}
    
    response, suggestions = generate_response(intent, entities)
    
    assert "cardiac" in response
    assert len(suggestions) > 0
    assert any("hospital" in suggestion.lower() for suggestion in suggestions)

def test_generate_response_lab():
    """Test generating response for finding labs."""
    intent = "find_lab"
    entities = {"test_type": "blood test"}
    
    response, suggestions = generate_response(intent, entities)
    
    assert "blood test" in response
    assert len(suggestions) > 0
    assert any("lab" in suggestion.lower() for suggestion in suggestions)

def test_generate_response_pharmacy():
    """Test generating response for finding pharmacies."""
    intent = "find_pharmacy"
    entities = {"medicine": "paracetamol"}
    
    response, suggestions = generate_response(intent, entities)
    
    assert "paracetamol" in response
    assert len(suggestions) > 0
    assert any("pharmacy" in suggestion.lower() for suggestion in suggestions)

def test_generate_response_ayush():
    """Test generating response for finding AYUSH practitioners."""
    intent = "find_ayush"
    entities = {"type": "ayurveda"}
    
    response, suggestions = generate_response(intent, entities)
    
    assert "ayurveda" in response
    assert len(suggestions) > 0
    assert any("ayurveda" in suggestion.lower() for suggestion in suggestions)

def test_generate_response_emergency():
    """Test generating response for emergency advice."""
    intent = "emergency_advice"
    entities = {"symptoms": ["chest pain"]}
    
    response, suggestions = generate_response(intent, entities)
    
    assert "emergency" in response.lower()
    assert "102" in response  # Emergency number in India
    assert len(suggestions) > 0
    assert any("emergency" in suggestion.lower() for suggestion in suggestions)

def test_generate_response_general():
    """Test generating general response."""
    intent = "general_info"
    entities = {}
    
    response, suggestions = generate_response(intent, entities)
    
    assert "healthcare assistant" in response.lower()
    assert len(suggestions) > 0
    assert any("doctor" in suggestion.lower() for suggestion in suggestions)

def test_doctor_response_with_location():
    """Test doctor response with location."""
    entities = {"specialty": "cardiologist", "location": "Mumbai"}
    
    response, suggestions = generate_doctor_response(entities)
    
    assert "cardiologist" in response
    assert "Mumbai" in response
    assert len(suggestions) > 0

def test_doctor_response_without_specialty():
    """Test doctor response without specialty."""
    entities = {}
    
    response, suggestions = generate_doctor_response(entities)
    
    assert "specialist" in response
    assert len(suggestions) > 0