import httpx
from typing import List, Dict, Optional, Any
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.exceptions import ExternalServiceException
from app.core.cache import cached
from app.schemas.chat import HealthcareProvider, Location

logger = structlog.get_logger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
    reraise=True,
)
@cached(ttl=300, key_prefix="healthcare")
async def find_healthcare_providers(
    intent: str, 
    entities: Dict[str, Any], 
    location: Optional[Location] = None,
    user_id: Optional[str] = None
) -> List[HealthcareProvider]:
    """Find healthcare providers based on intent and entities"""
    
    if intent == "find_doctor":
        return await find_doctors(entities, location, user_id)
    elif intent == "find_hospital":
        return await find_hospitals(entities, location, user_id)
    elif intent == "find_lab":
        return await find_labs(entities, location, user_id)
    elif intent == "find_pharmacy":
        return await find_pharmacies(entities, location, user_id)
    elif intent == "find_ayush":
        return await find_ayush_practitioners(entities, location, user_id)
    
    return []

async def find_doctors(
    entities: Dict[str, Any], 
    location: Optional[Location], 
    user_id: Optional[str]
) -> List[HealthcareProvider]:
    """Find doctors based on specialty and location"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {
                "specialty": entities.get("specialty", ""),
                "limit": 5
            }
            
            if location:
                params["latitude"] = location.latitude
                params["longitude"] = location.longitude
                
            if "city" in entities:
                params["city"] = entities["city"]
                
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/api/v1/doctors/search",
                params=params
            )
            
            if response.status_code != 200:
                logger.error(
                    "doctor_search_error",
                    status_code=response.status_code,
                    response=response.text,
                )
                return []
                
            doctors_data = response.json()
            
            return [
                HealthcareProvider(
                    id=doctor["id"],
                    name=doctor["name"],
                    type="doctor",
                    specialty=doctor.get("specialty"),
                    address=doctor.get("address"),
                    city=doctor.get("city"),
                    state=doctor.get("state"),
                    rating=doctor.get("rating"),
                    distance=doctor.get("distance"),
                    available_slots=doctor.get("available_slots")
                )
                for doctor in doctors_data
            ]
    except httpx.RequestError as e:
        logger.error("doctor_search_request_error", error=str(e))
        return []
    except Exception as e:
        logger.error("doctor_search_unexpected_error", error=str(e))
        return []

async def find_hospitals(
    entities: Dict[str, Any], 
    location: Optional[Location], 
    user_id: Optional[str]
) -> List[HealthcareProvider]:
    """Find hospitals based on specialty and location"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {
                "specialty": entities.get("specialty", ""),
                "limit": 5
            }
            
            if location:
                params["latitude"] = location.latitude
                params["longitude"] = location.longitude
                
            if "city" in entities:
                params["city"] = entities["city"]
                
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/api/v1/hospitals/search",
                params=params
            )
            
            if response.status_code != 200:
                logger.error(
                    "hospital_search_error",
                    status_code=response.status_code,
                    response=response.text,
                )
                return []
                
            hospitals_data = response.json()
            
            return [
                HealthcareProvider(
                    id=hospital["id"],
                    name=hospital["name"],
                    type="hospital",
                    specialty=hospital.get("specialty"),
                    address=hospital.get("address"),
                    city=hospital.get("city"),
                    state=hospital.get("state"),
                    rating=hospital.get("rating"),
                    distance=hospital.get("distance")
                )
                for hospital in hospitals_data
            ]
    except httpx.RequestError as e:
        logger.error("hospital_search_request_error", error=str(e))
        return []
    except Exception as e:
        logger.error("hospital_search_unexpected_error", error=str(e))
        return []

async def find_labs(
    entities: Dict[str, Any], 
    location: Optional[Location], 
    user_id: Optional[str]
) -> List[HealthcareProvider]:
    """Find labs based on test type and location"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {
                "test_type": entities.get("test_type", ""),
                "limit": 5
            }
            
            if location:
                params["latitude"] = location.latitude
                params["longitude"] = location.longitude
                
            if "city" in entities:
                params["city"] = entities["city"]
                
            response = await client.get(
                f"{settings.LAB_SERVICE_URL}/api/v1/labs/search",
                params=params
            )
            
            if response.status_code != 200:
                logger.error(
                    "lab_search_error",
                    status_code=response.status_code,
                    response=response.text,
                )
                return []
                
            labs_data = response.json()
            
            return [
                HealthcareProvider(
                    id=lab["id"],
                    name=lab["name"],
                    type="lab",
                    address=lab.get("address"),
                    city=lab.get("city"),
                    state=lab.get("state"),
                    rating=lab.get("rating"),
                    distance=lab.get("distance")
                )
                for lab in labs_data
            ]
    except httpx.RequestError as e:
        logger.error("lab_search_request_error", error=str(e))
        return []
    except Exception as e:
        logger.error("lab_search_unexpected_error", error=str(e))
        return []

async def find_pharmacies(
    entities: Dict[str, Any], 
    location: Optional[Location], 
    user_id: Optional[str]
) -> List[HealthcareProvider]:
    """Find pharmacies based on medicine and location"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {
                "medicine": entities.get("medicine", ""),
                "limit": 5
            }
            
            if location:
                params["latitude"] = location.latitude
                params["longitude"] = location.longitude
                
            if "city" in entities:
                params["city"] = entities["city"]
                
            response = await client.get(
                f"{settings.PHARMA_SERVICE_URL}/api/v1/pharmacies/search",
                params=params
            )
            
            if response.status_code != 200:
                logger.error(
                    "pharmacy_search_error",
                    status_code=response.status_code,
                    response=response.text,
                )
                return []
                
            pharmacies_data = response.json()
            
            return [
                HealthcareProvider(
                    id=pharmacy["id"],
                    name=pharmacy["name"],
                    type="pharmacy",
                    address=pharmacy.get("address"),
                    city=pharmacy.get("city"),
                    state=pharmacy.get("state"),
                    rating=pharmacy.get("rating"),
                    distance=pharmacy.get("distance")
                )
                for pharmacy in pharmacies_data
            ]
    except httpx.RequestError as e:
        logger.error("pharmacy_search_request_error", error=str(e))
        return []
    except Exception as e:
        logger.error("pharmacy_search_unexpected_error", error=str(e))
        return []

async def find_ayush_practitioners(
    entities: Dict[str, Any], 
    location: Optional[Location], 
    user_id: Optional[str]
) -> List[HealthcareProvider]:
    """Find AYUSH practitioners based on type and location"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {
                "type": entities.get("type", ""),
                "limit": 5
            }
            
            if location:
                params["latitude"] = location.latitude
                params["longitude"] = location.longitude
                
            if "city" in entities:
                params["city"] = entities["city"]
                
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/api/v1/ayush/search",
                params=params
            )
            
            if response.status_code != 200:
                logger.error(
                    "ayush_search_error",
                    status_code=response.status_code,
                    response=response.text,
                )
                return []
                
            practitioners_data = response.json()
            
            return [
                HealthcareProvider(
                    id=practitioner["id"],
                    name=practitioner["name"],
                    type="ayush",
                    specialty=practitioner.get("type"),
                    address=practitioner.get("address"),
                    city=practitioner.get("city"),
                    state=practitioner.get("state"),
                    rating=practitioner.get("rating"),
                    distance=practitioner.get("distance")
                )
                for practitioner in practitioners_data
            ]
    except httpx.RequestError as e:
        logger.error("ayush_search_request_error", error=str(e))
        return []
    except Exception as e:
        logger.error("ayush_search_unexpected_error", error=str(e))
        return []