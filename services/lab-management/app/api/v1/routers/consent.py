# app/api/v1/endpoints/consent.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.api.deps import get_current_user
from app.core.security import TokenPayload

router = APIRouter()

@router.get("/test")
async def test_consent():
    """Test endpoint for consent."""
    return {"message": "Consent API working"}