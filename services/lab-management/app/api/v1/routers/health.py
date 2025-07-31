from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis
import time
from datetime import datetime
from typing import Dict, Any

from app.db.session import get_db_session
from app.core.config import settings
from app.core.cache import cache_client, get_cache_stats

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "lab-management",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Detailed health check with dependency status."""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "lab-management",
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        start_time = time.time()
        result = await db.execute(text("SELECT 1"))
        db_response_time = (time.time() - start_time) * 1000
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_response_time, 2),
            "details": "PostgreSQL connection successful"
        }
    except Exception as e:
        overall_healthy = False
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "PostgreSQL connection failed"
        }
    
    # Redis health check
    try:
        start_time = time.time()
        cache_client.ping()
        redis_response_time = (time.time() - start_time) * 1000
        
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "response_time_ms": round(redis_response_time, 2),
            "details": "Redis connection successful"
        }
    except Exception as e:
        overall_healthy = False
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Redis connection failed"
        }
    
    # File system health check
    try:
        import os
        from pathlib import Path
        
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Test write/read/delete
        test_file = upload_dir / "health_check.tmp"
        test_file.write_text("health check")
        content = test_file.read_text()
        test_file.unlink()
        
        health_status["checks"]["filesystem"] = {
            "status": "healthy",
            "details": "File system read/write operations successful"
        }
    except Exception as e:
        overall_healthy = False
        health_status["checks"]["filesystem"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "File system operations failed"
        }
    
    # Memory usage check
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        memory_status = "healthy"
        if memory.percent > 90:
            memory_status = "critical"
            overall_healthy = False
        elif memory.percent > 80:
            memory_status = "warning"
        
        health_status["checks"]["memory"] = {
            "status": memory_status,
            "usage_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "details": f"Memory usage at {memory.percent}%"
        }
    except ImportError:
        health_status["checks"]["memory"] = {
            "status": "unknown",
            "details": "psutil not available for memory monitoring"
        }
    except Exception as e:
        health_status["checks"]["memory"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Set overall status
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    
    # Return appropriate HTTP status
    if not overall_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status

@router.get("/readiness")
async def readiness_check(
    db: AsyncSession = Depends(get_db_session)
):
    """Readiness probe for Kubernetes."""
    
    try:
        # Check database connectivity
        await db.execute(text("SELECT 1"))
        
        # Check Redis connectivity
        cache_client.ping()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/liveness")
async def liveness_check():
    """Liveness probe for Kubernetes."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - getattr(get_metrics, 'start_time', time.time()),
        "cache_stats": await get_cache_stats()
    }
    
    # Add database connection pool stats if available
    try:
        from app.db.session import engine
        pool = engine.pool
        metrics["database_pool"] = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    except Exception:
        metrics["database_pool"] = "unavailable"
    
    return metrics

# Initialize start time for uptime calculation
get_metrics.start_time = time.time()

@router.get("/dependencies")
async def check_dependencies():
    """Check status of external dependencies."""
    
    dependencies = {
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {}
    }
    
    # Check notification service (when implemented)
    dependencies["dependencies"]["notification_service"] = {
        "status": "not_implemented",
        "details": "Notification service integration pending"
    }
    
    # Check payment service (when implemented)
    dependencies["dependencies"]["payment_service"] = {
        "status": "not_implemented", 
        "details": "Payment service integration pending"
    }
    
    # Check user management service
    dependencies["dependencies"]["user_service"] = {
        "status": "assumed_healthy",
        "details": "User service health check not implemented"
    }
    
    return dependencies