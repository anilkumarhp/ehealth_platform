from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.db.session import get_db_session
from app.api.deps import get_current_user
from app.core.security import TokenPayload
from app.services.workflow_service import workflow_service
from app.services.business_rules import business_rules
from app.services.event_publisher import event_publisher
from app.schemas.test_order import TestOrder


router = APIRouter()


@router.post("/test-order/create-with-consent", response_model=TestOrder)
async def create_test_order_with_consent(
    *,
    db: AsyncSession = Depends(get_db_session),
    patient_id: UUID,
    lab_service_id: UUID,
    clinical_notes: Optional[str] = None,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Create test order and initiate consent workflow."""
    
    # Validate eligibility
    is_eligible = await business_rules.validate_test_order_eligibility(
        db=db, patient_id=patient_id, lab_service_id=lab_service_id
    )
    
    if not is_eligible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient not eligible for this test order"
        )
    
    # Create order with consent request
    order = await workflow_service.create_order_with_consent_request(
        db=db,
        patient_id=patient_id,
        lab_service_id=lab_service_id,
        requesting_entity_id=current_user.sub,
        organization_id=current_user.org_id,
        clinical_notes=clinical_notes
    )
    
    # Publish event for notification service
    await event_publisher.publish_test_order_created({
        "id": order.id,
        "patient_user_id": order.patient_user_id,
        "lab_service_id": order.lab_service_id,
        "status": order.status.value,
        "requesting_entity_id": order.requesting_entity_id
    })
    
    return order


@router.patch("/test-order/{order_id}/approve-consent", response_model=TestOrder)
async def approve_test_order_consent(
    *,
    db: AsyncSession = Depends(get_db_session),
    order_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Approve consent for test order."""
    
    # Process consent approval
    order = await workflow_service.process_consent_approval(
        db=db,
        order_id=order_id,
        patient_id=current_user.sub
    )
    
    # Publish event
    await event_publisher.publish_consent_approved({
        "order_id": order_id,
        "patient_id": current_user.sub
    })
    
    return order


@router.get("/available-slots/{lab_id}")
async def get_available_appointment_slots(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: UUID,
    date: str,  # Format: YYYY-MM-DD
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get available appointment slots for a specific lab and date."""
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Generate available slots (9 AM to 5 PM, hourly)
    available_slots = []
    for hour in range(9, 17):
        slot_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=hour))
        
        # Check if slot is available
        is_available = await business_rules.validate_appointment_scheduling(
            db=db,
            lab_id=lab_id,
            appointment_time=slot_datetime
        )
        
        if is_available:
            available_slots.append({
                "datetime": slot_datetime.isoformat(),
                "available": True
            })
    
    return {"available_slots": available_slots}


@router.get("/test-completion-estimate/{lab_service_id}")
async def get_test_completion_estimate(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_service_id: UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get estimated completion time for a test."""
    
    # Get lab service details
    from app.services.lab_service_service import lab_service_service
    service = await lab_service_service.get_service(db=db, service_id=lab_service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab service not found"
        )
    
    # Calculate estimated completion time
    test_count = len(service.test_definitions) if service.test_definitions else 1
    estimated_completion = business_rules.calculate_estimated_completion_time(test_count)
    
    return {
        "lab_service_id": lab_service_id,
        "estimated_completion_time": estimated_completion.isoformat(),
        "estimated_duration_hours": test_count * 0.5  # 30 minutes per test
    }