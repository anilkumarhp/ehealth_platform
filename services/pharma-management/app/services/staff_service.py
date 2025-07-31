"""
Staff management service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from app.models.staff import PharmacyStaff
from app.repositories.base_repository import BaseRepository
from app.schemas.staff import StaffCreate, StaffResponse, StaffList
from app.core.exceptions import PharmacyNotFoundException
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class StaffService:
    """Service for staff management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.staff_repo = BaseRepository(db, PharmacyStaff)
        self.audit_service = AuditService(db)
    
    async def add_staff_member(
        self, 
        pharmacy_id: UUID, 
        staff_data: StaffCreate
    ) -> StaffResponse:
        """Add new staff member to pharmacy."""
        try:
            # Verify pharmacy exists
            from sqlalchemy import select
            from app.models.pharmacy import Pharmacy
            
            pharmacy_result = await self.db.execute(
                select(Pharmacy).where(Pharmacy.id == pharmacy_id)
            )
            pharmacy = pharmacy_result.scalar_one_or_none()
            if not pharmacy:
                raise PharmacyNotFoundException(str(pharmacy_id))
            
            # Check for existing staff with same email
            existing_staff = await self.staff_repo.get_multi(
                filters={"pharmacy_id": pharmacy_id, "email": staff_data.email, "is_active": True}
            )
            if existing_staff:
                raise ValueError(f"Staff member with email {staff_data.email} already exists in this pharmacy")
            
            # Create staff member data
            staff_dict = staff_data.dict()
            staff_dict["pharmacy_id"] = pharmacy_id
            
            # Create staff member
            staff_member = await self.staff_repo.create(staff_dict)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="staff_member_added",
                resource_type="staff",
                resource_id=staff_member.id,
                pharmacy_id=pharmacy_id,
                description=f"Added staff member: {staff_data.first_name} {staff_data.last_name}",
                extra_data={
                    "role": staff_data.role,
                    "email": staff_data.email,
                    "permissions": {
                        "validate_prescriptions": staff_data.can_validate_prescriptions,
                        "dispense_controlled": staff_data.can_dispense_controlled_substances,
                        "manage_inventory": staff_data.can_manage_inventory,
                        "process_payments": staff_data.can_process_payments
                    }
                }
            )
            
            logger.info(f"Added staff member {staff_member.id} to pharmacy {pharmacy_id}")
            return StaffResponse.from_orm(staff_member)
        except PharmacyNotFoundException as e:
            logger.error(f"Pharmacy not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding staff member: {e}")
            raise
    
    async def get_pharmacy_staff(self, pharmacy_id: UUID) -> List[StaffList]:
        """Get all staff members for a pharmacy."""
        try:
            staff_members = await self.staff_repo.get_multi(
                filters={"pharmacy_id": pharmacy_id, "is_active": True}
            )
            
            logger.info(f"Retrieved {len(staff_members)} staff members for pharmacy {pharmacy_id}")
            return [StaffList.from_orm(staff) for staff in staff_members]
        except Exception as e:
            logger.error(f"Error getting pharmacy staff: {e}")
            raise
    
    async def get_staff_member(self, staff_id: UUID) -> StaffResponse:
        """Get staff member by ID."""
        try:
            staff_member = await self.staff_repo.get_by_id(staff_id)
            if not staff_member:
                raise ValueError("Staff member not found")
            
            return StaffResponse.from_orm(staff_member)
        except Exception as e:
            logger.error(f"Error getting staff member {staff_id}: {e}")
            raise
    
    async def update_staff_permissions(
        self, 
        staff_id: UUID, 
        permissions: dict
    ) -> StaffResponse:
        """Update staff member permissions."""
        try:
            staff_member = await self.staff_repo.get_by_id(staff_id)
            if not staff_member:
                raise ValueError("Staff member not found")
            
            # Update permissions
            updated_staff = await self.staff_repo.update(staff_id, permissions)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="staff_permissions_updated",
                resource_type="staff",
                resource_id=staff_id,
                pharmacy_id=staff_member.pharmacy_id,
                description=f"Updated permissions for {staff_member.first_name} {staff_member.last_name}",
                old_values={
                    "can_validate_prescriptions": staff_member.can_validate_prescriptions,
                    "can_dispense_controlled_substances": staff_member.can_dispense_controlled_substances,
                    "can_manage_inventory": staff_member.can_manage_inventory,
                    "can_process_payments": staff_member.can_process_payments
                },
                new_values=permissions
            )
            
            logger.info(f"Updated permissions for staff member {staff_id}")
            return StaffResponse.from_orm(updated_staff)
        except Exception as e:
            logger.error(f"Error updating staff permissions: {e}")
            raise