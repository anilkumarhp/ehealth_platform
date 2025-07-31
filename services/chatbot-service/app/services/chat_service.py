import logging
from typing import Dict, Any, List, Optional
from app.services.llm_service import llm_service
from app.services.external_service import external_service
import re

logger = logging.getLogger(__name__)

class ChatService:
    async def process_message(self, message: str, conversation_history: List[Dict[str, str]], token: Optional[str] = None) -> Dict[str, Any]:
        """Process a chat message and generate a response."""
        try:
            # Check if user is logged in
            user_data = None
            if token:
                user_data = await external_service.check_user_logged_in(token)
            
            # Detect intent from the message
            intent = self._detect_intent(message)
            
            if intent == "appointment":
                # Handle appointment scheduling
                return await self._handle_appointment(message, conversation_history, user_data, token)
            elif intent == "medical_question":
                # Handle general medical questions with LLM
                return await self._handle_medical_question(message, conversation_history)
            else:
                # Default to general LLM response
                response = await llm_service.generate_completion(message)
                return {"response": response, "intent": "general"}
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {"response": "I'm sorry, I encountered an error while processing your request. Please try again later.", "intent": "error"}
    
    def _detect_intent(self, message: str) -> str:
        """Detect the intent of the message."""
        message = message.lower()
        
        # Appointment related keywords
        appointment_keywords = ["appointment", "schedule", "book", "visit", "see a doctor", "consult", "consultation"]
        
        for keyword in appointment_keywords:
            if keyword in message:
                return "appointment"
        
        # Medical question keywords
        medical_keywords = ["symptom", "treatment", "medicine", "disease", "condition", "pain", "diagnosis", "prescription"]
        
        for keyword in medical_keywords:
            if keyword in message:
                return "medical_question"
        
        return "general"
    
    async def _handle_appointment(self, message: str, conversation_history: List[Dict[str, str]], user_data: Optional[Dict[str, Any]], token: Optional[str]) -> Dict[str, Any]:
        """Handle appointment scheduling."""
        # Extract entities from the message
        hospital_name = self._extract_entity(message, "hospital")
        doctor_name = self._extract_entity(message, "doctor")
        date = self._extract_entity(message, "date")
        
        # If user is not logged in, ask them to log in
        if not user_data:
            return {
                "response": "To schedule an appointment, you need to be logged in. Please log in to your account first.",
                "intent": "appointment",
                "requires_auth": True
            }
        
        # If hospital is not specified, get hospitals and ask user to choose
        if not hospital_name:
            hospitals = await external_service.get_hospitals()
            if not hospitals:
                return {
                    "response": "I couldn't find any hospitals in our system. Please try again later.",
                    "intent": "appointment"
                }
            
            hospital_list = ", ".join([h["name"] for h in hospitals[:5]])
            return {
                "response": f"Which hospital would you like to schedule an appointment at? We have: {hospital_list}",
                "intent": "appointment",
                "hospitals": hospitals[:5]
            }
        
        # If hospital is specified but doctor is not, get doctors for that hospital
        if hospital_name and not doctor_name:
            hospitals = await external_service.get_hospitals(hospital_name)
            if not hospitals:
                return {
                    "response": f"I couldn't find a hospital named '{hospital_name}'. Could you please specify a different hospital?",
                    "intent": "appointment"
                }
            
            hospital_id = hospitals[0]["id"]
            doctors = await external_service.get_doctors(hospital_id=hospital_id)
            
            if not doctors:
                return {
                    "response": f"I couldn't find any doctors at {hospitals[0]['name']}. Please try a different hospital.",
                    "intent": "appointment"
                }
            
            doctor_list = ", ".join([f"Dr. {d['name']} ({d['specialty']})" for d in doctors[:5]])
            return {
                "response": f"Which doctor would you like to see at {hospitals[0]['name']}? We have: {doctor_list}",
                "intent": "appointment",
                "doctors": doctors[:5]
            }
        
        # If both hospital and doctor are specified but date is not, ask for date
        if hospital_name and doctor_name and not date:
            hospitals = await external_service.get_hospitals(hospital_name)
            if not hospitals:
                return {
                    "response": f"I couldn't find a hospital named '{hospital_name}'. Could you please specify a different hospital?",
                    "intent": "appointment"
                }
            
            hospital_id = hospitals[0]["id"]
            doctors = await external_service.get_doctors(hospital_id=hospital_id)
            
            matching_doctors = [d for d in doctors if doctor_name.lower() in d["name"].lower()]
            if not matching_doctors:
                return {
                    "response": f"I couldn't find Dr. {doctor_name} at {hospitals[0]['name']}. Please specify a different doctor.",
                    "intent": "appointment"
                }
            
            return {
                "response": f"When would you like to schedule your appointment with Dr. {matching_doctors[0]['name']} at {hospitals[0]['name']}? Please specify a date.",
                "intent": "appointment",
                "doctor": matching_doctors[0]
            }
        
        # If all information is provided, check available slots
        if hospital_name and doctor_name and date:
            hospitals = await external_service.get_hospitals(hospital_name)
            if not hospitals:
                return {
                    "response": f"I couldn't find a hospital named '{hospital_name}'. Could you please specify a different hospital?",
                    "intent": "appointment"
                }
            
            hospital_id = hospitals[0]["id"]
            doctors = await external_service.get_doctors(hospital_id=hospital_id)
            
            matching_doctors = [d for d in doctors if doctor_name.lower() in d["name"].lower()]
            if not matching_doctors:
                return {
                    "response": f"I couldn't find Dr. {doctor_name} at {hospitals[0]['name']}. Please specify a different doctor.",
                    "intent": "appointment"
                }
            
            doctor_id = matching_doctors[0]["id"]
            slots = await external_service.get_available_slots(doctor_id=doctor_id, date=date)
            
            if not slots:
                return {
                    "response": f"I couldn't find any available slots for Dr. {matching_doctors[0]['name']} on {date}. Would you like to try a different date?",
                    "intent": "appointment"
                }
            
            slot_list = ", ".join([s["time"] for s in slots[:5]])
            return {
                "response": f"The following slots are available for Dr. {matching_doctors[0]['name']} on {date}: {slot_list}. Which time would you prefer?",
                "intent": "appointment",
                "slots": slots[:5]
            }
        
        # Default response if we can't determine the next step
        return {
            "response": "I need more information to schedule your appointment. Could you please provide details about which hospital and doctor you'd like to see?",
            "intent": "appointment"
        }
    
    async def _handle_medical_question(self, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Handle general medical questions using the LLM."""
        system_prompt = """
        You are a healthcare assistant for an eHealth platform. Provide helpful, accurate information about general health topics.
        
        Important guidelines:
        1. DO NOT provide specific medical advice or diagnosis.
        2. Always recommend consulting with a healthcare professional for specific medical concerns.
        3. Provide general information about common health conditions, treatments, and preventive measures.
        4. Be empathetic and supportive in your responses.
        5. If you're unsure about something, acknowledge your limitations.
        """
        
        response = await llm_service.generate_completion(message, system_prompt)
        return {"response": response, "intent": "medical_question"}
    
    def _extract_entity(self, message: str, entity_type: str) -> Optional[str]:
        """Extract entities from the message."""
        message = message.lower()
        
        if entity_type == "hospital":
            # Look for hospital names
            hospital_pattern = r"(?:at|in|to) (?:the )?([a-z ]+) hospital"
            match = re.search(hospital_pattern, message)
            if match:
                return match.group(1).strip()
            
            # Look for "hospital" followed by a name
            hospital_pattern = r"hospital (?:called|named) ([a-z ]+?)(?:\.|\?|$| for| to| on)"
            match = re.search(hospital_pattern, message)
            if match:
                return match.group(1).strip()
        
        elif entity_type == "doctor":
            # Look for doctor names
            doctor_pattern = r"(?:with|see) (?:dr\.?|doctor) ([a-z ]+?)(?:\.|\?|$| at| on| for)"
            match = re.search(doctor_pattern, message)
            if match:
                return match.group(1).strip()
        
        elif entity_type == "date":
            # Look for dates
            date_patterns = [
                r"(?:on|for) ([a-z]+ \d{1,2}(?:st|nd|rd|th)?)",  # "on January 15th"
                r"(?:on|for) (\d{1,2}(?:st|nd|rd|th)? (?:of )?[a-z]+)",  # "on 15th of January"
                r"(?:on|for) (\d{1,2}/\d{1,2}(?:/\d{2,4})?)",  # "on 01/15" or "on 01/15/2023"
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, message)
                if match:
                    return match.group(1).strip()
        
        return None

# Singleton instance
chat_service = ChatService()