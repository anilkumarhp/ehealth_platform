"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis
import time
import logging

from app.db.session import get_async_session
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "pharma-management",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_async_session)):
    """Detailed health check including database and Redis."""
    health_status = {
        "status": "healthy",
        "service": "pharma-management",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Database check
    try:
        result = await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": 0  # Could measure actual time
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # External services check (optional)
    health_status["checks"]["external_services"] = {
        "twilio": "not_configured" if not settings.TWILIO_ACCOUNT_SID else "configured",
        "sendgrid": "not_configured" if not settings.SENDGRID_API_KEY else "configured",
        "aws_s3": "not_configured" if not settings.S3_BUCKET_NAME else "configured"
    }
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_async_session)):
    """Kubernetes readiness probe."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail={"status": "not_ready", "error": str(e)})


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}