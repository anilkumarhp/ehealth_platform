from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.session import get_db_session
from app.schemas.test_order import TestOrder, TestOrderCreate
from app.models.test_order import TestOrderStatusEnum
from app.services.test_order_service import test_order_service
from app.api.deps import get_current_user
from app.core.security import TokenPayload


router = APIRouter()

# ... (create_test_order_for_patient remains the same) ...
@router.post("/for-patient/{patient_user_id}", status_code=status.HTTP_201_CREATED, response_model=TestOrder)
async def create_test_order_for_patient(*, db: AsyncSession = Depends(get_db_session), patient_user_id: UUID, order_in: TestOrderCreate, current_user: TokenPayload = Depends(get_current_user)):
  
    if not current_user.org_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is not associated with any organization.")
    return await test_order_service.create_order(db=db, obj_in=order_in, patient_user_id=patient_user_id, requesting_entity_id=current_user.sub, organization_id=current_user.org_id)

# --- THIS ENDPOINT IS UPDATED ---
@router.get("/for-patient/my-orders", response_model=List[TestOrder])
async def get_my_test_orders(
    *,
    db: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Retrieve all test orders for the currently authenticated patient.
    """
    return await test_order_service.get_orders_by_patient(
        db=db, patient_user_id=current_user.sub, skip=skip, limit=limit
    )

# --- THIS ENDPOINT IS UPDATED ---
@router.get("/{order_id}", response_model=TestOrder)
async def get_test_order(
    *,
    db: AsyncSession = Depends(get_db_session),
    order_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Retrieve a specific test order by its ID.
    Access is restricted to the patient or the requesting doctor.
    """
    return await test_order_service.get_order_by_id(
        db=db, order_id=order_id, current_user=current_user
    )

# ... (approve_test_order_consent remains the same) ...
@router.patch("/{order_id}/consent/approve", response_model=TestOrder)
async def approve_test_order_consent(*, db: AsyncSession = Depends(get_db_session), order_id: UUID, current_user: TokenPayload = Depends(get_current_user)):
    return await test_order_service.update_order_status(db=db, order_id=order_id, new_status=TestOrderStatusEnum.AWAITING_APPOINTMENT, user_id=current_user.sub)