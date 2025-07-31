# app/services/test_order_service.py (Updated with Authorization)

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from app.repositories.test_order_repo import test_order_repo
from app.repositories.lab_service_repo import lab_service_repo
from app.models.test_order import TestOrder, TestOrderStatusEnum
from app.schemas.test_order import TestOrderCreate, TestOrderUpdate
from app.core.security import TokenPayload # Import TokenPayload

class TestOrderService:
    # ... (create_order method remains the same) ...
    async def create_order(self, db: AsyncSession, *, obj_in: TestOrderCreate, patient_user_id: UUID, requesting_entity_id: UUID, organization_id: UUID) -> TestOrder:
        lab_service = await lab_service_repo.get(db, id=obj_in.lab_service_id)
        if not lab_service:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Lab service with ID {obj_in.lab_service_id} not found.")
        if not lab_service.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Lab service '{lab_service.name}' is currently not active.")
        return await test_order_repo.create_with_owner(db, obj_in=obj_in, patient_user_id=patient_user_id, requesting_entity_id=requesting_entity_id, organization_id=organization_id)

    # --- THIS METHOD IS UPDATED ---
    async def get_order_by_id(self, db: AsyncSession, *, order_id: UUID, current_user: TokenPayload) -> Optional[TestOrder]:
        """
        Retrieves a single test order by its ID after checking permissions.
        """
        order = await test_order_repo.get(db, id=order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test order not found.")

        # --- Authorization Check ---
        # Allow access if the user is the patient OR the doctor who requested it.
        if order.patient_user_id != current_user.sub and order.requesting_entity_id != current_user.sub:
            # A more complex check could be to see if the user is a doctor in the same org.
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permission denied to view this test order.")
        # --- End of Authorization Check ---

        return order

    async def get_orders_by_patient(self, db: AsyncSession, *, patient_user_id: UUID, skip: int = 0, limit: int = 100) -> List[TestOrder]:
        # This method is called by an endpoint that already checks if the current_user is the patient,
        # so no additional check is needed here.
        return await test_order_repo.get_by_patient_id(db, patient_user_id=patient_user_id, skip=skip, limit=limit)

    async def update_order_status(self, db: AsyncSession, *, order_id: UUID, new_status: TestOrderStatusEnum, user_id: UUID) -> TestOrder:
        db_order = await test_order_repo.get(db, id=order_id) # Use repo directly to avoid circular permission checks
        if not db_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test order not found.")
        if db_order.patient_user_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to update this order.")
        update_schema = TestOrderUpdate(status=new_status)
        return await test_order_repo.update(db, db_obj=db_order, obj_in=update_schema)

# Instantiate the service
test_order_service = TestOrderService()