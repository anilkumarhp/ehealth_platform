# src/lab_management/api/middleware/exception_middleware.py

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import (
    BaseLabException, create_error_response, handle_database_error
)

# Get a logger instance for this module
logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """
    Enhanced global exception handler with proper error categorization.
    """
    
    # Handle custom lab exceptions
    if isinstance(exc, BaseLabException):
        error_response = create_error_response(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )
    
    # Handle FastAPI HTTP exceptions
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    # Handle database exceptions
    if isinstance(exc, SQLAlchemyError):
        lab_exception = handle_database_error(exc)
        error_response = create_error_response(lab_exception)
        return JSONResponse(
            status_code=lab_exception.status_code,
            content=error_response
        )
    
    # Log unhandled exceptions
    logger.error(
        f"Unhandled exception for request {request.method} {request.url}",
        exc_info=exc,
        extra={
            "request_details": {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else "N/A",
            }
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )