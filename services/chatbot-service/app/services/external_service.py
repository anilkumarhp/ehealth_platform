import httpx
from fastapi import HTTPException
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ExternalService:
    def __init__(self):
        self.user_service_url = os.getenv("USER_SERVICE_URL", "http://user-management-api:8000")
        self.hospital_service_url = os.getenv("HOSPITAL_SERVICE_URL", "http://hospital-management-api:8005")
        self.pharma_service_url = os.getenv("PHARMA_SERVICE_URL", "http://pharma-management-app:8001")
        self.lab_service_url = os.getenv("LAB_SERVICE_URL", "http://lab-management-api:8003")
        
    async def get_user_data(self, user_id: str, token: str) -> Dict[str, Any]:
        """Get user data from the user service."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"User service error: {response.status_code} - {response.text}")
                    return None
                
                return response.json()
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None
            
    async def check_user_logged_in(self, token: str) -> Optional[Dict[str, Any]]:
        """Check if the user is logged in and return their data."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"User service error: {response.status_code} - {response.text}")
                    return None
                
                return response.json()
        except Exception as e:
            logger.error(f"Error checking user login: {str(e)}")
            return None
            
    async def get_hospitals(self, query: str = None) -> List[Dict[str, Any]]:
        """Get hospitals from the hospital service."""
        try:
            params = {}
            if query:
                params["search"] = query
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.hospital_service_url}/api/v1/hospitals",
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Hospital service error: {response.status_code} - {response.text}")
                    return []
                
                return response.json()
        except Exception as e:
            logger.error(f"Error getting hospitals: {str(e)}")
            return []
            
    async def get_doctors(self, hospital_id: str = None, specialty: str = None) -> List[Dict[str, Any]]:
        """Get doctors from the hospital service."""
        try:
            params = {}
            if hospital_id:
                params["hospital_id"] = hospital_id
            if specialty:
                params["specialty"] = specialty
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.hospital_service_url}/api/v1/doctors",
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Hospital service error: {response.status_code} - {response.text}")
                    return []
                
                return response.json()
        except Exception as e:
            logger.error(f"Error getting doctors: {str(e)}")
            return []
            
    async def get_available_slots(self, doctor_id: str, date: str = None) -> List[Dict[str, Any]]:
        """Get available appointment slots for a doctor."""
        try:
            params = {}
            if date:
                params["date"] = date
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.hospital_service_url}/api/v1/doctors/{doctor_id}/slots",
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Hospital service error: {response.status_code} - {response.text}")
                    return []
                
                return response.json()
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            return []
            
    async def book_appointment(self, user_id: str, doctor_id: str, slot_id: str, token: str) -> Dict[str, Any]:
        """Book an appointment."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.hospital_service_url}/api/v1/appointments",
                    json={
                        "user_id": user_id,
                        "doctor_id": doctor_id,
                        "slot_id": slot_id
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 201:
                    logger.error(f"Hospital service error: {response.status_code} - {response.text}")
                    return None
                
                return response.json()
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            return None

# Singleton instance
external_service = ExternalService()