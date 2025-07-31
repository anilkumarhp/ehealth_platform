import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "eHealth Chatbot Service"
    PROJECT_DESCRIPTION: str = "AI-powered healthcare assistant for the eHealth platform"
    VERSION: str = "0.1.0"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://chatbotuser:chatbotpassword@localhost:5435/chatbot_service"
    )
    
    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6381/0")
    
    # External service URLs
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
    PHARMA_SERVICE_URL: str = os.getenv("PHARMA_SERVICE_URL", "http://localhost:8001")
    LAB_SERVICE_URL: str = os.getenv("LAB_SERVICE_URL", "http://localhost:8003")
    LLM_SERVICE_URL: str = os.getenv("LLM_SERVICE_URL", "http://localhost:8008")
    
    # CORS settings
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Monitoring settings
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    # LLM settings
    LLM_TIMEOUT: int = 10  # seconds
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour

settings = Settings()