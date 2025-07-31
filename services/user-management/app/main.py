from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
import logging

from app.core.config import settings
from app.core.exceptions import DetailException, NotFoundException
from app.db.init_db import create_database_if_not_exists
from app.core.startup import ensure_s3_bucket_exists

# --- Main App Instance ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Centralized Exception Handlers ---

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handles DB integrity errors (e.g., unique constraint violations)."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Database integrity error. A record with a conflicting value may already exist."},
    )

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """Handles all custom "Not Found" exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )

@app.exception_handler(DetailException)
async def detail_exception_handler(request: Request, exc: DetailException):
    """Handles all other custom exceptions that provide a detail message."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail},
    )

# --- API Routers ---
from app.api.v1.routers import (
    auth, users, organization, consent, connections, rbac, documents, registration, webhooks, notifications, health, files, profile
)

app.include_router(health.router, prefix=settings.API_V1_STR)  # Health check endpoint
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["Users"])
app.include_router(profile.router, prefix=settings.API_V1_STR, tags=["User Profile"])
app.include_router(organization.router, prefix=settings.API_V1_STR, tags=["Organization"])
app.include_router(consent.router, prefix=settings.API_V1_STR, tags=["Consent"])
app.include_router(connections.router, prefix=settings.API_V1_STR, tags=["Connections"])
app.include_router(rbac.router, prefix=settings.API_V1_STR, tags=["RBAC"])
app.include_router(documents.router, prefix=settings.API_V1_STR, tags=["Documents"])
app.include_router(registration.router, prefix=settings.API_V1_STR, tags=["New Registration"])
app.include_router(webhooks.router, prefix=settings.API_V1_STR, tags=["Stripe"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["Notifications"])
app.include_router(files.router, prefix=f"{settings.API_V1_STR}/files", tags=["Files"])
app.include_router(files.router, prefix="/v1/files", tags=["Files"])  # Additional route for frontend compatibility

# --- Startup Events ---
@app.on_event("startup")
def startup_event():
    """Run startup tasks"""
    try:
        # Initialize database and create required tables
        create_database_if_not_exists()
        logging.info("Database initialization completed")
        
        # Ensure S3 bucket exists
        ensure_s3_bucket_exists()
        logging.info("S3 bucket initialization completed")
    except Exception as e:
        logging.error(f"Error during startup: {str(e)}")
        # Don't fail startup if this fails, just log the error