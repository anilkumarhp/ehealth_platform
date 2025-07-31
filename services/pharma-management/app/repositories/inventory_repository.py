"""
Inventory repository for data access operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.medicine import Medicine
from app.models.pharmacy import Pharmacy
from app.repositories.base_repository import BaseRepository
from app.core.exceptions import InsufficientStockException

logger = logging.getLogger(__name__)


class InventoryRepository(BaseRepository[InventoryItem]):
    """Repository for inventory operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, InventoryItem)
    
    async def get_pharmacy_inventory(
        self, 
        pharmacy_id: UUID, 
        medicine_id: Optional[UUID] = None
    ) -> List[InventoryItem]:
        """Get inventory for a pharmacy."""
        try:
            query = select(InventoryItem).where(
                and_(
                    InventoryItem.pharmacy_id == pharmacy_id,
                    InventoryItem.is_active == True
                )
            )
            
            if medicine_id:
                query = query.where(InventoryItem.medicine_id == medicine_id)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting pharmacy inventory: {e}")
            raise
    
    async def check_availability(
        self, 
        medicine_ids: List[UUID], 
        pharmacy_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Check medicine availability across pharmacies."""
        try:
            query = select(
                InventoryItem.medicine_id,
                Medicine.name.label('medicine_name'),
                func.sum(InventoryItem.current_stock - InventoryItem.reserved_stock).label('total_available'),
                func.count(InventoryItem.pharmacy_id).label('pharmacy_count')
            ).join(
                Medicine, InventoryItem.medicine_id == Medicine.id
            ).where(
                and_(
                    InventoryItem.medicine_id.in_(medicine_ids),
                    InventoryItem.is_active == True,
                    Medicine.is_active == True
                )
            )
            
            if pharmacy_id:
                query = query.where(InventoryItem.pharmacy_id == pharmacy_id)
            
            query = query.group_by(InventoryItem.medicine_id, Medicine.name)
            
            result = await self.db.execute(query)
            availability_data = result.all()
            
            availability_list = []
            for row in availability_data:
                availability_list.append({
                    "medicine_id": row.medicine_id,
                    "medicine_name": row.medicine_name,
                    "total_available": int(row.total_available or 0),
                    "pharmacy_count": int(row.pharmacy_count)
                })
            
            return availability_list
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            raise
    
    async def reserve_stock(
        self, 
        pharmacy_id: UUID, 
        medicine_id: UUID, 
        quantity: int
    ) -> bool:
        """Reserve stock for an order."""
        try:
            # Get inventory item
            inventory_item = await self.db.execute(
                select(InventoryItem).where(
                    and_(
                        InventoryItem.pharmacy_id == pharmacy_id,
                        InventoryItem.medicine_id == medicine_id,
                        InventoryItem.is_active == True
                    )
                )
            )
            item = inventory_item.scalar_one_or_none()
            
            if not item:
                return False
            
            # Check if enough stock available
            available_stock = item.current_stock - item.reserved_stock
            if available_stock < quantity:
                raise InsufficientStockException(
                    medicine_name=str(medicine_id),
                    available=available_stock,
                    requested=quantity
                )
            
            # Reserve stock
            await self.db.execute(
                update(InventoryItem)
                .where(InventoryItem.id == item.id)
                .values(reserved_stock=item.reserved_stock + quantity)
            )
            
            await self.db.commit()
            logger.info(f"Reserved {quantity} units of medicine {medicine_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error reserving stock: {e}")
            raise
    
    async def release_stock(
        self, 
        pharmacy_id: UUID, 
        medicine_id: UUID, 
        quantity: int
    ) -> bool:
        """Release reserved stock."""
        try:
            inventory_item = await self.db.execute(
                select(InventoryItem).where(
                    and_(
                        InventoryItem.pharmacy_id == pharmacy_id,
                        InventoryItem.medicine_id == medicine_id,
                        InventoryItem.is_active == True
                    )
                )
            )
            item = inventory_item.scalar_one_or_none()
            
            if not item:
                return False
            
            # Release stock
            new_reserved = max(0, item.reserved_stock - quantity)
            await self.db.execute(
                update(InventoryItem)
                .where(InventoryItem.id == item.id)
                .values(reserved_stock=new_reserved)
            )
            
            await self.db.commit()
            logger.info(f"Released {quantity} units of medicine {medicine_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error releasing stock: {e}")
            raise
    
    async def update_stock(
        self, 
        pharmacy_id: UUID, 
        medicine_id: UUID, 
        quantity_change: int,
        transaction_type: str,
        reference_number: Optional[str] = None
    ) -> bool:
        """Update stock levels and create transaction record."""
        try:
            # Get inventory item
            inventory_item = await self.db.execute(
                select(InventoryItem).where(
                    and_(
                        InventoryItem.pharmacy_id == pharmacy_id,
                        InventoryItem.medicine_id == medicine_id,
                        InventoryItem.is_active == True
                    )
                )
            )
            item = inventory_item.scalar_one_or_none()
            
            if not item:
                return False
            
            # Calculate new stock
            old_stock = item.current_stock
            new_stock = max(0, old_stock + quantity_change)
            
            # Update inventory
            await self.db.execute(
                update(InventoryItem)
                .where(InventoryItem.id == item.id)
                .values(current_stock=new_stock)
            )
            
            # Create transaction record
            transaction = InventoryTransaction(
                inventory_item_id=item.id,
                transaction_type=transaction_type,
                quantity=quantity_change,
                stock_before=old_stock,
                stock_after=new_stock,
                reference_number=reference_number
            )
            
            self.db.add(transaction)
            await self.db.commit()
            
            logger.info(f"Updated stock for medicine {medicine_id}: {old_stock} -> {new_stock}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating stock: {e}")
            raise
    
    async def get_low_stock_items(self, pharmacy_id: UUID) -> List[InventoryItem]:
        """Get items that need reordering."""
        try:
            result = await self.db.execute(
                select(InventoryItem).where(
                    and_(
                        InventoryItem.pharmacy_id == pharmacy_id,
                        InventoryItem.current_stock <= InventoryItem.reorder_point,
                        InventoryItem.is_active == True
                    )
                ).order_by(InventoryItem.current_stock)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting low stock items: {e}")
            raise


class InventoryTransactionRepository(BaseRepository[InventoryTransaction]):
    """Repository for inventory transaction operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, InventoryTransaction)
    
    async def get_transactions_by_inventory(
        self, 
        inventory_item_id: UUID,
        limit: int = 50
    ) -> List[InventoryTransaction]:
        """Get transactions for an inventory item."""
        try:
            result = await self.db.execute(
                select(InventoryTransaction)
                .where(InventoryTransaction.inventory_item_id == inventory_item_id)
                .order_by(InventoryTransaction.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting inventory transactions: {e}")
            raise