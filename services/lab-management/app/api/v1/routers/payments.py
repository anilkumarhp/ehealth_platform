# app/api/v1/endpoints/payments.py

from fastapi import APIRouter, Depends, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_current_user
from app.core.security import TokenPayload

router = APIRouter()

@router.get("/test")
async def test_payments():
    """Test endpoint for payments."""
    return {"message": "Payments API working"}