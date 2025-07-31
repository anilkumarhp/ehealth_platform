from fastapi import APIRouter, Depends
from app.services.llm_service import llm_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    Health check endpoint that also checks the LLM service status.
    """
    # Check LLM service status
    llm_status = await llm_service.check_model_status()
    
    return {
        "status": "ok",
        "llm_service": llm_status
    }