# app/api/v1/endpoints/reports.py (Updated)

from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import json

from app.api.deps import get_current_user
from app.core.security import TokenPayload

router = APIRouter()

@router.get("/test")
async def test_reports():
    """Test endpoint for reports."""
    return {"message": "Reports API working"}