# app/api/v1/api_router.py (Updated)

from fastapi import APIRouter

# Import the working routers
from .routers.lab_services import router as lab_services_router
from .routers.test_orders import router as test_orders_router
from .routers.appointments import router as appointments_router
from .routers.consent import router as consent_router
from .routers.reports import router as reports_router
from .routers.payments import router as payments_router
from .routers.auth import router as auth_router
from .routers.workflow import router as workflow_router
from .routers.health import router as health_router
from .routers.lab_config import router as lab_config_router
from .routers.files import router as files_router
from .routers.analytics import router as analytics_router
from .routers.search import router as search_router

# Create a master router for all v1 endpoints
api_router = APIRouter()

# Include the working routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(lab_services_router, prefix="/lab-services", tags=["Lab Services"])
api_router.include_router(test_orders_router, prefix="/test-orders", tags=["Test Orders"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(consent_router, prefix="/consent", tags=["Consent Management"])
api_router.include_router(workflow_router, prefix="/workflow", tags=["Workflow Management"])
api_router.include_router(lab_config_router, prefix="/lab-config", tags=["Lab Configuration"])
api_router.include_router(files_router, prefix="/files", tags=["File Management"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics & Reporting"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(health_router, prefix="/health", tags=["Health Checks"])

