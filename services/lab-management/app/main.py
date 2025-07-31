import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
try:
    from starlette_prometheus import metrics, PrometheusMiddleware
except ImportError:
    # For testing environments where prometheus is not available
    metrics = None
    PrometheusMiddleware = None

from app.core.config import settings
from app.api.v1.api_router import api_router
from app.core.logging_config import setup_logging
from app.api.middleware.exception_middleware import global_exception_handler
from app.core.docs import OPENAPI_CONFIG, API_TAGS
from app.core.rate_limiter import RateLimitMiddleware

""" Application Setup """
# Logging setup
setup_logging()
logger = logging.getLogger(__name__)

# Create the FastAPI app instance
app = FastAPI(
    **OPENAPI_CONFIG,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    openapi_tags=API_TAGS
)

""" Middleware Configuration """
# Global Exception handler Middleware
app.add_exception_handler(Exception, global_exception_handler)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, default_limit=1000, window=3600)  # 1000 requests per hour

# 4. Add Prometheus middleware to expose /metrics endpoint (if available)
if PrometheusMiddleware:
    app.add_middleware(PrometheusMiddleware)

# 5. Set up CORS (Cross-Origin Resource Sharing) middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

""" Router Setup """
# setup prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add the /metrics endpoint for Prometheus (if available)
if metrics:
    app.add_route("/metrics", metrics)


# Root Endpoint
@app.get("/", tags=["Health Check"])
async def read_root():
    """
    A simple root endpoint to confirm that the application is running.
    """
    logger.info("Health check endpoint was called.")
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}