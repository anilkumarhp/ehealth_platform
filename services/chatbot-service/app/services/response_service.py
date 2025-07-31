from typing import Dict, List, Tuple, Any
import structlog

logger = structlog.get_logger(__name__)

def generate_response(intent: str, entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate response based on intent and entities"""
    if intent == "find_doctor":
        return generate_doctor_response(entities)
    elif intent == "find_hospital":
        return generate_hospital_response(entities)
    elif intent == "find_lab":
        return generate_lab_response(entities)
    elif intent == "find_pharmacy":
        return generate_pharmacy_response(entities)
    elif intent == "find_ayush":
        return generate_ayush_response(entities)
    elif intent == "emergency_advice":
        return generate_emergency_response(entities)
    else:
        return generate_general_response(entities)

def generate_doctor_response(entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate response for finding doctors"""
    specialty = entities.get("specialty", "")
    location = entities.get("location", "")
    
    if specialty:
        response = f"I'll help you find a {specialty} doctor"
        if location:
            response += f" in {location}"
        response += ". Here are some options:"
    else:
        response = "I'll help you find a doctor. What type of specialist are you looking for?"
    
    suggestions = [
        "Find a cardiologist",
        "Find a pediatrician",
        "Find a dermatologist",
        "Find a gynecologist",
        "Find a general physician near me"
    ]
    
    return response, suggestions

def generate_hospital_response(entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate response for finding hospitals"""
    specialty = entities.get("specialty", "")
    location = entities.get("location", "")
    
    if specialty:
        response = f"I'll help you find a hospital with {specialty} department"
        if location:
            response += f" in {location}"
        response += ". Here are some options:"
    else:
        response = "I'll help you find a hospital. What type of hospital are you looking for?"
    
    suggestions = [
        "Find a multi-specialty hospital",
        "Find a cardiac hospital",
        "Find a children's hospital",
        "Find a government hospital",
        "Find a hospital near me"
    ]
    
    return response, suggestions

def generate_lab_response(entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate response for finding labs"""
    test_type = entities.get("test_type", "")
    location = entities.get("location", "")
    
    if test_type:
        response = f"I'll help you find a lab for {test_type} test"
        if location:
            response += f" in {location}"
        response += ". Here are some options:"
    else:
        response = "I'll help you find a diagnostic lab. What type of test are you looking for?"
    
    suggestions = [
        "Find a lab for blood tests",
        "Find a lab for MRI scan",
        "Find a lab for COVID test",
        "Find a lab for full body checkup",
        "Find a lab near me"
    ]
    
    return response, suggestions

def generate_pharmacy_response(entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate response for finding pharmacies"""
    medicine = entities.get("medicine", "")
    location = entities.get("location", "")
    
    if medicine:
        response = f"I'll help you find a pharmacy that has {medicine}"
        if location:
            response += f" in {location}"
        response += ". Here are some options:"
    else:
        response = "I'll help you find a pharmacy. Are you looking for any specific medicine?"
    
    suggestions = [
        "Find a 24-hour pharmacy",
        "Find a Jan Aushadhi pharmacy",
        "Find a pharmacy with home delivery",
        "Find a pharmacy near me"
    ]
    
    return response, suggestions

def generate_ayush_response(entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate response for finding AYUSH practitioners"""
    ayush_type = entities.get("type", "")
    location = entities.get("location", "")
    
    if ayush_type:
        response = f"I'll help you find an {ayush_type} practitioner"
        if location:
            response += f" in {location}"
        response += ". Here are some options:"
    else:
        response = "I'll help you find an AYUSH practitioner. What type of AYUSH system are you interested in?"
    
    suggestions = [
        "Find an Ayurveda doctor",
        "Find a Yoga therapist",
        "Find a Unani practitioner",
        "Find a Siddha doctor",
        "Find a Homeopathy doctor near me"
    ]
    
    return response, suggestions

def generate_emergency_response(entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate response for emergency advice"""
    symptoms = entities.get("symptoms", [])
    
    response = "For medical emergencies, please call 102 for an ambulance or visit the nearest emergency room immediately. "
    response += "I'm an AI assistant and not a medical professional, but I can help you find the nearest hospital."
    
    suggestions = [
        "Find nearest emergency room",
        "Find nearest hospital",
        "Call ambulance",
        "First aid for common emergencies",
        "Contact a doctor now"
    ]
    
    return response, suggestions

def generate_general_response(entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Generate general response"""
    response = "I'm your healthcare assistant. I can help you find doctors, hospitals, labs, or pharmacies. What are you looking for today?"
    
    suggestions = [
        "Find a doctor",
        "Find a hospital",
        "Find a diagnostic lab",
        "Find a pharmacy",
        "I need medical advice"
    ]
    
    return response, suggestions