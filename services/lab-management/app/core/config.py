# app/core/config.py (Corrected)

import os
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict # Import SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """
    Pydantic settings class to manage application configuration from environment variables.
    """
    # --- All fields remain the same ---
    PROJECT_NAME: str = "Lab Management System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "a_very_secret_key_that_should_be_changed"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/lab_db")
    TEST_DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/lab_test_db")
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost", "http://localhost:3000"]
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "lab-management-reports-bucket"
    STRIPE_API_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    
    # External Services
    NOTIFICATION_SERVICE_URL: str | None = None
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: int = 1000  # requests per hour
    
    # Caching
    CACHE_ENABLED: bool = True
    DEFAULT_CACHE_TTL: int = 300  # 5 minutes

    # --- THIS IS THE FIX ---
    # Replace the inner Config class with model_config
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding='utf-8'
    )
    # --- END OF FIX ---

# Instantiate the settings object
settings = Settings()