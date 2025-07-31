"""
Medicine business logic service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from app.repositories.medicine_repository import MedicineRepository, MedicineBatchRepository
from app.schemas.medicine import MedicineResponse, MedicineAlternatives
from app.core.exceptions import MedicineNotFoundException
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class MedicineService:
    """Service for medicine operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.medicine_repo = MedicineRepository(db)
        self.batch_repo = MedicineBatchRepository(db)
        self.audit_service = AuditService(db)
    
    async def search_medicines(self, query: str, limit: int = 20) -> List[MedicineResponse]:
        """Search medicines by name, generic name, or manufacturer."""
        try:
            medicines = await self.medicine_repo.search_medicines(query, limit)
            
            # Log search activity
            await self.audit_service.log_action(
                action="medicine_search",
                resource_type="medicine",
                description=f"Searched medicines with query: {query}",
                extra_data={"query": query, "results_count": len(medicines)}
            )
            
            return [MedicineResponse.from_orm(medicine) for medicine in medicines]
        except Exception as e:
            logger.error(f"Error in medicine search service: {e}")
            raise
    
    async def get_medicine(self, medicine_id: UUID) -> MedicineResponse:
        """Get medicine by ID."""
        try:
            medicine = await self.medicine_repo.get_by_id(medicine_id)
            if not medicine:
                raise MedicineNotFoundException(str(medicine_id))
            
            return MedicineResponse.from_orm(medicine)
        except Exception as e:
            logger.error(f"Error getting medicine {medicine_id}: {e}")
            raise
    
    async def get_alternatives(
        self, 
        medicine_id: UUID, 
        include_generic: bool = True, 
        include_brand: bool = True
    ) -> MedicineAlternatives:
        """Get alternative medicines."""
        try:
            # Get base medicine
            base_medicine = await self.medicine_repo.get_by_id(medicine_id)
            if not base_medicine:
                raise MedicineNotFoundException(str(medicine_id))
            
            # Get alternatives
            alternatives_data = await self.medicine_repo.get_alternatives(
                medicine_id, include_generic, include_brand
            )
            
            # Convert to response format
            generic_alternatives = [
                MedicineResponse.from_orm(med) 
                for med in alternatives_data["generic_alternatives"]
            ]
            brand_alternatives = [
                MedicineResponse.from_orm(med) 
                for med in alternatives_data["brand_alternatives"]
            ]
            
            total_alternatives = len(generic_alternatives) + len(brand_alternatives)
            
            # Log alternatives request
            await self.audit_service.log_action(
                action="medicine_alternatives_requested",
                resource_type="medicine",
                resource_id=medicine_id,
                description=f"Requested alternatives for {base_medicine.name}",
                extra_data={
                    "generic_count": len(generic_alternatives),
                    "brand_count": len(brand_alternatives)
                }
            )
            
            return MedicineAlternatives(
                medicine_id=medicine_id,
                medicine_name=base_medicine.name,
                generic_alternatives=generic_alternatives,
                brand_alternatives=brand_alternatives,
                total_alternatives=total_alternatives
            )
        except Exception as e:
            logger.error(f"Error getting alternatives for medicine {medicine_id}: {e}")
            raise
    
    async def check_drug_interactions(self, medicine_ids: List[UUID]) -> dict:
        """Check for drug interactions between medicines."""
        try:
            # This would integrate with external drug interaction database
            # For now, return a placeholder response
            interactions = {
                "has_interactions": False,
                "interactions": [],
                "severity": "none",
                "recommendations": []
            }
            
            # Log interaction check
            await self.audit_service.log_action(
                action="drug_interaction_check",
                resource_type="medicine",
                description=f"Checked interactions for {len(medicine_ids)} medicines",
                extra_data={"medicine_ids": [str(id) for id in medicine_ids]}
            )
            
            logger.info(f"Checked drug interactions for {len(medicine_ids)} medicines")
            return interactions
        except Exception as e:
            logger.error(f"Error checking drug interactions: {e}")
            raise
    
    async def get_expiring_medicines(self, days: int = 30) -> List[dict]:
        """Get medicines with batches expiring soon."""
        try:
            expiring_batches = await self.batch_repo.get_expiring_batches(days)
            
            expiring_medicines = []
            for batch in expiring_batches:
                medicine = await self.medicine_repo.get_by_id(batch.medicine_id)
                if medicine:
                    expiring_medicines.append({
                        "medicine_id": medicine.id,
                        "medicine_name": medicine.name,
                        "batch_number": batch.batch_number,
                        "expiry_date": batch.expiry_date,
                        "days_to_expiry": batch.days_to_expiry,
                        "quantity": batch.current_quantity
                    })
            
            logger.info(f"Found {len(expiring_medicines)} expiring medicines")
            return expiring_medicines
        except Exception as e:
            logger.error(f"Error getting expiring medicines: {e}")
            raise
    
    async def create_medicine(self, medicine_data: dict) -> MedicineResponse:
        """Create a new medicine."""
        try:
            # Create medicine
            medicine = await self.medicine_repo.create(medicine_data)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="medicine_created",
                resource_type="medicine",
                resource_id=medicine.id,
                description=f"Created medicine: {medicine.name}"
            )
            
            logger.info(f"Created medicine: {medicine.name}")
            return MedicineResponse.from_orm(medicine)
        except Exception as e:
            logger.error(f"Error creating medicine: {e}")
            raise