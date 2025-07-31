"""
Medicine repository for data access operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from uuid import UUID
import logging

from app.models.medicine import Medicine, MedicineBatch
from app.repositories.base_repository import BaseRepository
from app.core.exceptions import MedicineNotFoundException

logger = logging.getLogger(__name__)


class MedicineRepository(BaseRepository[Medicine]):
    """Repository for medicine operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Medicine)
    
    async def search_medicines(self, query: str, limit: int = 20) -> List[Medicine]:
        """Search medicines by name, generic name, or manufacturer."""
        try:
            search_query = select(Medicine).where(
                and_(
                    Medicine.is_active == True,
                    or_(
                        Medicine.name.ilike(f"%{query}%"),
                        Medicine.generic_name.ilike(f"%{query}%"),
                        Medicine.brand_name.ilike(f"%{query}%"),
                        Medicine.manufacturer.ilike(f"%{query}%")
                    )
                )
            ).order_by(Medicine.name).limit(limit)
            
            result = await self.db.execute(search_query)
            medicines = result.scalars().all()
            
            logger.info(f"Found {len(medicines)} medicines for query: {query}")
            return medicines
        except Exception as e:
            logger.error(f"Error searching medicines: {e}")
            raise
    
    async def get_alternatives(
        self, 
        medicine_id: UUID, 
        include_generic: bool = True, 
        include_brand: bool = True
    ) -> dict:
        """Get alternative medicines."""
        try:
            # Get the base medicine
            base_medicine = await self.get_by_id(medicine_id)
            if not base_medicine:
                raise MedicineNotFoundException(str(medicine_id))
            
            alternatives = {
                "generic_alternatives": [],
                "brand_alternatives": []
            }
            
            # Find generic alternatives
            if include_generic and base_medicine.generic_alternatives:
                generic_query = select(Medicine).where(
                    and_(
                        Medicine.id.in_(base_medicine.generic_alternatives),
                        Medicine.is_active == True
                    )
                )
                result = await self.db.execute(generic_query)
                alternatives["generic_alternatives"] = result.scalars().all()
            
            # Find brand alternatives
            if include_brand and base_medicine.brand_alternatives:
                brand_query = select(Medicine).where(
                    and_(
                        Medicine.id.in_(base_medicine.brand_alternatives),
                        Medicine.is_active == True
                    )
                )
                result = await self.db.execute(brand_query)
                alternatives["brand_alternatives"] = result.scalars().all()
            
            logger.info(f"Found alternatives for medicine {medicine_id}")
            return alternatives
        except Exception as e:
            logger.error(f"Error getting alternatives for medicine {medicine_id}: {e}")
            raise
    
    async def get_by_ndc(self, ndc_number: str) -> Optional[Medicine]:
        """Get medicine by NDC number."""
        try:
            result = await self.db.execute(
                select(Medicine).where(
                    and_(
                        Medicine.ndc_number == ndc_number,
                        Medicine.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting medicine by NDC {ndc_number}: {e}")
            raise
    
    async def get_controlled_substances(self) -> List[Medicine]:
        """Get all controlled substances."""
        try:
            result = await self.db.execute(
                select(Medicine).where(
                    and_(
                        Medicine.controlled_substance == True,
                        Medicine.is_active == True
                    )
                )
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting controlled substances: {e}")
            raise


class MedicineBatchRepository(BaseRepository[MedicineBatch]):
    """Repository for medicine batch operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, MedicineBatch)
    
    async def get_expiring_batches(self, days: int = 30) -> List[MedicineBatch]:
        """Get batches expiring within specified days."""
        try:
            from datetime import date, timedelta
            expiry_threshold = date.today() + timedelta(days=days)
            
            result = await self.db.execute(
                select(MedicineBatch).where(
                    and_(
                        MedicineBatch.expiry_date <= expiry_threshold,
                        MedicineBatch.current_quantity > 0,
                        MedicineBatch.is_active == True
                    )
                ).order_by(MedicineBatch.expiry_date)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting expiring batches: {e}")
            raise
    
    async def get_expired_batches(self) -> List[MedicineBatch]:
        """Get expired batches."""
        try:
            from datetime import date
            today = date.today()
            
            result = await self.db.execute(
                select(MedicineBatch).where(
                    and_(
                        MedicineBatch.expiry_date < today,
                        MedicineBatch.current_quantity > 0,
                        MedicineBatch.is_active == True
                    )
                ).order_by(MedicineBatch.expiry_date)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting expired batches: {e}")
            raise
    
    async def get_batches_by_medicine(self, medicine_id: UUID) -> List[MedicineBatch]:
        """Get all batches for a medicine."""
        try:
            result = await self.db.execute(
                select(MedicineBatch).where(
                    and_(
                        MedicineBatch.medicine_id == medicine_id,
                        MedicineBatch.is_active == True
                    )
                ).order_by(MedicineBatch.expiry_date)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting batches for medicine {medicine_id}: {e}")
            raise