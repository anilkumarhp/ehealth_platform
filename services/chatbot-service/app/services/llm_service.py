import httpx
from fastapi import HTTPException
import os
import logging
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm_service_url = os.getenv("LLM_SERVICE_URL", "http://llm-service:11434")
        self.model_name = os.getenv("LLM_MODEL_NAME", "llama2")
        logger.info(f"LLM service URL: {self.llm_service_url}, Model: {self.model_name}")
        
    async def generate_completion(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a completion using the LLM service."""
        if not system_prompt:
            system_prompt = "You are a helpful healthcare assistant for an eHealth platform. Provide accurate and helpful information about healthcare topics."
            
        try:
            # Format for Ollama API
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 256
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.llm_service_url}/api/generate",
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"LLM service error: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=500, detail="Error communicating with LLM service")
                
                result = response.json()
                return result["response"]
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")
            
    async def process_appointment_request(self, 
                                         user_query: str, 
                                         user_data: Optional[Dict[str, Any]] = None,
                                         hospital_data: Optional[List[Dict[str, Any]]] = None,
                                         doctor_data: Optional[List[Dict[str, Any]]] = None,
                                         available_slots: Optional[List[Dict[str, Any]]] = None) -> str:
        """Process an appointment request with context from other services."""
        # Create context with all available data
        context = {
            "user_is_logged_in": user_data is not None,
            "user_data": user_data,
            "hospitals": hospital_data,
            "doctors": doctor_data,
            "available_slots": available_slots
        }
        
        # Create system prompt for appointment handling
        system_prompt = """
        You are a healthcare assistant for an eHealth platform. Your task is to help users schedule appointments.
        
        Follow these guidelines:
        1. If the user is not logged in, politely ask them to log in first.
        2. If the user is logged in but hasn't specified a hospital or doctor, ask for this information.
        3. If the user has specified a hospital or doctor, check if they're available in the provided data.
        4. If time slots are available, present them to the user and ask them to choose one.
        5. If no time slots are available, suggest alternative times or doctors.
        
        Always be helpful, concise, and focused on solving the user's appointment scheduling needs.
        """
        
        # Create prompt with user query and context
        prompt = f"""
        User query: {user_query}
        
        Context (JSON): {json.dumps(context, indent=2)}
        
        Based on the user query and the provided context, help the user schedule an appointment.
        """
        
        # Generate response
        return await self.generate_completion(prompt, system_prompt)

# Singleton instance
llm_service = LLMService()