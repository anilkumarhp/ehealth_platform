"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.routers import (
    pharmacies,
    staff,
    medicines,
    prescriptions,
    orders,
    inventory,
    billing,
    clinical,
    notifications,
    compliance,
    health
)

api_router = APIRouter()

# Include all routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    pharmacies.router,
    prefix="/pharmacies",
    tags=["pharmacies"]
)

api_router.include_router(
    staff.router,
    prefix="/pharmacies",
    tags=["staff"]
)

api_router.include_router(
    medicines.router,
    prefix="/medicines",
    tags=["medicines"]
)

api_router.include_router(
    prescriptions.router,
    prefix="/prescriptions",
    tags=["prescriptions"]
)

api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["orders"]
)

api_router.include_router(
    inventory.router,
    prefix="",  # No prefix, as endpoints already include /pharmacies or /inventory
    tags=["inventory"]
)

api_router.include_router(
    billing.router,
    prefix="/billing",
    tags=["billing"]
)

api_router.include_router(
    clinical.router,
    prefix="/clinical",
    tags=["clinical"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"]
)

api_router.include_router(
    compliance.router,
    prefix="/compliance",
    tags=["compliance"]
)