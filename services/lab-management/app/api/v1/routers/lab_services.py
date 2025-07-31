# app/api/v1/endpoints/lab_services.py (Updated)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.session import get_db_session
from app.schemas.lab_service import LabService, LabServiceCreate, LabServiceUpdate
from app.services.lab_service_service import lab_service_service
from app.api.deps import get_current_user
from app.core.security import TokenPayload

router = APIRouter()

# ... (create_lab_service, get_lab_services, get_lab_service remain the same) ...
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=LabService)
async def create_lab_service(*, db: AsyncSession = Depends(get_db_session), service_in: LabServiceCreate, current_user: TokenPayload = Depends(get_current_user)):
    if not current_user.org_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is not associated with any lab.")
    return await lab_service_service.create_service(db=db, obj_in=service_in, lab_id=current_user.org_id)

@router.get("/by-lab/{lab_id}", response_model=List[LabService])
async def get_lab_services(*, db: AsyncSession = Depends(get_db_session), lab_id: UUID, skip: int = 0, limit: int = 100):
    return await lab_service_service.get_services_by_lab(db=db, lab_id=lab_id, skip=skip, limit=limit)

@router.get("/{service_id}", response_model=LabService)
async def get_lab_service(*, db: AsyncSession = Depends(get_db_session), service_id: UUID):
    return await lab_service_service.get_service_by_id(db=db, service_id=service_id)


# --- THIS ENDPOINT IS UPDATED ---
@router.patch("/{service_id}", response_model=LabService)
async def update_lab_service(
    *,
    db: AsyncSession = Depends(get_db_session),
    service_id: UUID,
    service_in: LabServiceUpdate,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Update a lab service. The user must belong to the lab that owns the service.
    """
    return await lab_service_service.update_service(
        db=db, service_id=service_id, obj_in=service_in, current_user=current_user
    )

# --- THIS ENDPOINT IS UPDATED ---
@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lab_service(
    *,
    db: AsyncSession = Depends(get_db_session),
    service_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Delete a lab service. The user must belong to the lab that owns the service.
    """
    await lab_service_service.delete_service(
        db=db, service_id=service_id, current_user=current_user
    )
    return None