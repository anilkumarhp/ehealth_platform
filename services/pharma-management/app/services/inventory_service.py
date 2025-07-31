"""
Inventory management service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

from app.repositories.inventory_repository import InventoryRepository, InventoryTransactionRepository
from app.repositories.medicine_repository import MedicineRepository
from app.schemas.inventory import InventoryUpdate, InventoryItemResponse, InventoryAvailability
from app.schemas.inventory import InventoryItemCreate, InventoryItemResponse, InventoryTransactionCreate
from app.core.exceptions import MedicineNotFoundException, InsufficientStockException
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for inventory management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_repo = InventoryRepository(db)
        self.transaction_repo = InventoryTransactionRepository(db)
        self.medicine_repo = MedicineRepository(db)
        self.audit_service = AuditService(db)
    
    async def add_medicine_batch(
        self, 
        pharmacy_id: UUID, 
        inventory_data: InventoryUpdate
    ) -> InventoryItemResponse:
        """Add new medicine batch to inventory."""
        try:
            # Verify medicine exists
            medicine = await self.medicine_repo.get_by_id(inventory_data.medicine_id)
            if not medicine:
                raise MedicineNotFoundException(str(inventory_data.medicine_id))
            
            # Check if inventory item already exists
            existing_items = await self.inventory_repo.get_pharmacy_inventory(
                pharmacy_id, inventory_data.medicine_id
            )
            
            if existing_items:
                # Update existing inventory
                inventory_item = existing_items[0]
                old_stock = inventory_item.current_stock
                new_stock = old_stock + inventory_data.quantity
                
                update_data = {
                    "current_stock": new_stock,
                    "cost_price": inventory_data.cost_price,
                    "selling_price": inventory_data.selling_price,
                    "mrp": inventory_data.mrp,
                    "updated_at": datetime.utcnow()
                }
                
                updated_item = await self.inventory_repo.update(inventory_item.id, update_data)
                
                # Create transaction record
                await self.inventory_repo.update_stock(
                    pharmacy_id=pharmacy_id,
                    medicine_id=inventory_data.medicine_id,
                    quantity_change=inventory_data.quantity,
                    transaction_type="purchase",
                    reference_number=inventory_data.batch_number
                )
                
                result_item = updated_item
            else:
                # Create new inventory item
                inventory_item_data = {
                    "pharmacy_id": pharmacy_id,
                    "medicine_id": inventory_data.medicine_id,
                    "current_stock": inventory_data.quantity,
                    "cost_price": inventory_data.cost_price,
                    "selling_price": inventory_data.selling_price,
                    "mrp": inventory_data.mrp,
                    "minimum_stock": 10,  # Default minimum stock
                    "reorder_point": 20,  # Default reorder point
                    "primary_supplier": inventory_data.supplier
                }
                
                result_item = await self.inventory_repo.create(inventory_item_data)
            
            # Log audit trail
            await self.audit_service.log_inventory_action(
                action="inventory_batch_added",
                inventory_id=result_item.id,
                pharmacy_id=pharmacy_id,
                description=f"Added batch {inventory_data.batch_number} of {medicine.name}",
                new_values={
                    "quantity": inventory_data.quantity,
                    "batch_number": inventory_data.batch_number,
                    "cost_price": float(inventory_data.cost_price)
                }
            )
            
            # Convert to response format
            response = InventoryItemResponse(
                id=result_item.id,
                pharmacy_id=result_item.pharmacy_id,
                medicine_id=result_item.medicine_id,
                medicine_name=medicine.name,
                current_stock=result_item.current_stock,
                available_stock=result_item.available_stock,
                reserved_stock=result_item.reserved_stock,
                minimum_stock=result_item.minimum_stock,
                reorder_point=result_item.reorder_point,
                cost_price=result_item.cost_price,
                selling_price=result_item.selling_price,
                mrp=result_item.mrp,
                needs_reorder=result_item.needs_reorder,
                is_overstocked=result_item.is_overstocked,
                storage_location=result_item.storage_location
            )
            
            logger.info(f"Added medicine batch to inventory: {inventory_data.batch_number}")
            return response
        except Exception as e:
            logger.error(f"Error adding medicine batch: {e}")
            raise
    
    async def update_inventory_item(
        self, 
        pharmacy_id: UUID, 
        inventory_id: UUID, 
        inventory_data: InventoryUpdate
    ) -> InventoryItemResponse:
        """Update inventory item."""
        try:
            # Get existing inventory item
            inventory_item = await self.inventory_repo.get_by_id(inventory_id)
            if not inventory_item or inventory_item.pharmacy_id != pharmacy_id:
                raise ValueError("Inventory item not found or access denied")
            
            # Get medicine details
            medicine = await self.medicine_repo.get_by_id(inventory_item.medicine_id)
            
            # Calculate stock change
            stock_change = inventory_data.quantity - inventory_item.current_stock
            
            # Update inventory item
            update_data = {
                "current_stock": inventory_data.quantity,
                "cost_price": inventory_data.cost_price,
                "selling_price": inventory_data.selling_price,
                "mrp": inventory_data.mrp,
                "updated_at": datetime.utcnow()
            }
            
            updated_item = await self.inventory_repo.update(inventory_id, update_data)
            
            # Create transaction record if stock changed
            if stock_change != 0:
                transaction_type = "adjustment"
                await self.inventory_repo.update_stock(
                    pharmacy_id=pharmacy_id,
                    medicine_id=inventory_item.medicine_id,
                    quantity_change=stock_change,
                    transaction_type=transaction_type,
                    reference_number=f"ADJ-{inventory_id}"
                )
            
            # Log audit trail
            await self.audit_service.log_inventory_action(
                action="inventory_updated",
                inventory_id=inventory_id,
                pharmacy_id=pharmacy_id,
                description=f"Updated inventory for {medicine.name}",
                old_values={"current_stock": inventory_item.current_stock},
                new_values={"current_stock": inventory_data.quantity}
            )
            
            # Convert to response format
            response = InventoryItemResponse(
                id=updated_item.id,
                pharmacy_id=updated_item.pharmacy_id,
                medicine_id=updated_item.medicine_id,
                medicine_name=medicine.name,
                current_stock=updated_item.current_stock,
                available_stock=updated_item.available_stock,
                reserved_stock=updated_item.reserved_stock,
                minimum_stock=updated_item.minimum_stock,
                reorder_point=updated_item.reorder_point,
                cost_price=updated_item.cost_price,
                selling_price=updated_item.selling_price,
                mrp=updated_item.mrp,
                needs_reorder=updated_item.needs_reorder,
                is_overstocked=updated_item.is_overstocked,
                storage_location=updated_item.storage_location
            )
            
            logger.info(f"Updated inventory item: {inventory_id}")
            return response
        except Exception as e:
            logger.error(f"Error updating inventory item: {e}")
            raise
    
    async def check_availability(
        self, 
        medicine_ids: List[UUID],
        pharmacy_id: Optional[UUID] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: float = 10.0
    ) -> List[InventoryAvailability]:
        """Check medicine availability."""
        try:
            # Get availability data
            availability_data = await self.inventory_repo.check_availability(
                medicine_ids, pharmacy_id
            )
            
            availability_list = []
            for data in availability_data:
                availability = InventoryAvailability(
                    medicine_id=data["medicine_id"],
                    medicine_name=data["medicine_name"],
                    total_available=data["total_available"],
                    pharmacies=[],  # Would be populated with nearby pharmacy data
                    nearest_pharmacy=None  # Would be calculated based on location
                )
                availability_list.append(availability)
            
            # Log availability check
            await self.audit_service.log_action(
                action="availability_check",
                resource_type="inventory",
                description=f"Checked availability for {len(medicine_ids)} medicines",
                metadata={
                    "medicine_ids": [str(id) for id in medicine_ids],
                    "pharmacy_id": str(pharmacy_id) if pharmacy_id else None
                }
            )
            
            logger.info(f"Checked availability for {len(medicine_ids)} medicines")
            return availability_list
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            raise
    
    async def reserve_medicines(
        self, 
        pharmacy_id: UUID, 
        medicine_quantities: List[dict]
    ) -> bool:
        """Reserve medicines for an order."""
        try:
            for item in medicine_quantities:
                medicine_id = item["medicine_id"]
                quantity = item["quantity"]
                
                success = await self.inventory_repo.reserve_stock(
                    pharmacy_id, medicine_id, quantity
                )
                
                if not success:
                    # Rollback previous reservations
                    await self._rollback_reservations(pharmacy_id, medicine_quantities[:medicine_quantities.index(item)])
                    raise InsufficientStockException(
                        medicine_name=str(medicine_id),
                        available=0,
                        requested=quantity
                    )
            
            logger.info(f"Reserved medicines for pharmacy {pharmacy_id}")
            return True
        except Exception as e:
            logger.error(f"Error reserving medicines: {e}")
            raise
    
    async def _rollback_reservations(
        self, 
        pharmacy_id: UUID, 
        medicine_quantities: List[dict]
    ):
        """Rollback medicine reservations."""
        try:
            for item in medicine_quantities:
                await self.inventory_repo.release_stock(
                    pharmacy_id, item["medicine_id"], item["quantity"]
                )
        except Exception as e:
            logger.error(f"Error rolling back reservations: {e}")
    
    async def add_inventory_item(self, pharmacy_id: UUID, inventory_data: InventoryItemCreate) -> InventoryItemResponse:
        """Add inventory item to pharmacy."""
        try:
            # Check if medicine exists
            medicine = await self.medicine_repo.get_by_id(inventory_data.medicine_id)
            if not medicine:
                raise MedicineNotFoundException(str(inventory_data.medicine_id))
            
            # Create inventory item data
            inventory_item_data = {
                "pharmacy_id": pharmacy_id,
                "medicine_id": inventory_data.medicine_id,
                "current_stock": inventory_data.current_stock,
                "minimum_stock": inventory_data.minimum_stock,
                "maximum_stock": inventory_data.maximum_stock,
                "reorder_point": inventory_data.reorder_point,
                "cost_price": inventory_data.cost_price,
                "selling_price": inventory_data.selling_price,
                "mrp": inventory_data.mrp,
                "storage_location": inventory_data.storage_location
            }
            
            # Create inventory item
            inventory_item = await self.inventory_repo.create(inventory_item_data)
            
            # Log audit trail
            await self.audit_service.log_inventory_action(
                action="inventory_item_added",
                inventory_id=inventory_item.id,
                pharmacy_id=pharmacy_id,
                description=f"Added inventory item for {medicine.name}"
            )
            
            # Convert to response format
            response = InventoryItemResponse(
                id=inventory_item.id,
                pharmacy_id=inventory_item.pharmacy_id,
                medicine_id=inventory_item.medicine_id,
                medicine_name=medicine.name,
                current_stock=inventory_item.current_stock,
                available_stock=inventory_item.available_stock,
                reserved_stock=inventory_item.reserved_stock,
                minimum_stock=inventory_item.minimum_stock,
                reorder_point=inventory_item.reorder_point,
                cost_price=inventory_item.cost_price,
                selling_price=inventory_item.selling_price,
                mrp=inventory_item.mrp,
                needs_reorder=inventory_item.needs_reorder,
                is_overstocked=inventory_item.is_overstocked,
                storage_location=inventory_item.storage_location
            )
            
            logger.info(f"Added inventory item for medicine {medicine.name}")
            return response
        except Exception as e:
            logger.error(f"Error adding inventory item: {e}")
            raise
    
    async def get_pharmacy_inventory(self, pharmacy_id: UUID) -> List[InventoryItemResponse]:
        """Get all inventory items for a pharmacy."""
        try:
            # Get inventory items
            inventory_items = await self.inventory_repo.get_pharmacy_inventory(pharmacy_id)
            
            # Convert to response format
            response_items = []
            for item in inventory_items:
                # Get medicine details
                medicine = await self.medicine_repo.get_by_id(item.medicine_id)
                
                response_item = InventoryItemResponse(
                    id=item.id,
                    pharmacy_id=item.pharmacy_id,
                    medicine_id=item.medicine_id,
                    medicine_name=medicine.name if medicine else "Unknown Medicine",
                    current_stock=item.current_stock,
                    available_stock=item.available_stock,
                    reserved_stock=item.reserved_stock,
                    minimum_stock=item.minimum_stock,
                    reorder_point=item.reorder_point,
                    cost_price=item.cost_price,
                    selling_price=item.selling_price,
                    mrp=item.mrp,
                    needs_reorder=item.needs_reorder,
                    is_overstocked=item.is_overstocked,
                    storage_location=item.storage_location
                )
                response_items.append(response_item)
            
            logger.info(f"Retrieved {len(response_items)} inventory items for pharmacy {pharmacy_id}")
            return response_items
        except Exception as e:
            logger.error(f"Error getting pharmacy inventory: {e}")
            raise
    
    async def get_low_stock_items(self, pharmacy_id: UUID, threshold: Optional[int] = None) -> List[InventoryItemResponse]:
        """Get low stock items for a pharmacy."""
        try:
            # Get inventory items
            inventory_items = await self.inventory_repo.get_pharmacy_inventory(pharmacy_id)
            
            # Filter low stock items
            low_stock_items = []
            for item in inventory_items:
                if threshold:
                    if item.current_stock <= threshold:
                        low_stock_items.append(item)
                elif item.current_stock <= item.reorder_point:
                    low_stock_items.append(item)
            
            # Convert to response format
            response_items = []
            for item in low_stock_items:
                # Get medicine details
                medicine = await self.medicine_repo.get_by_id(item.medicine_id)
                
                response_item = InventoryItemResponse(
                    id=item.id,
                    pharmacy_id=item.pharmacy_id,
                    medicine_id=item.medicine_id,
                    medicine_name=medicine.name if medicine else "Unknown Medicine",
                    current_stock=item.current_stock,
                    available_stock=item.available_stock,
                    reserved_stock=item.reserved_stock,
                    minimum_stock=item.minimum_stock,
                    reorder_point=item.reorder_point,
                    cost_price=item.cost_price,
                    selling_price=item.selling_price,
                    mrp=item.mrp,
                    needs_reorder=item.needs_reorder,
                    is_overstocked=item.is_overstocked,
                    storage_location=item.storage_location
                )
                response_items.append(response_item)
            
            logger.info(f"Retrieved {len(response_items)} low stock items for pharmacy {pharmacy_id}")
            return response_items
        except Exception as e:
            logger.error(f"Error getting low stock items: {e}")
            raise
    
    async def update_inventory_stock(self, transaction_data: InventoryTransactionCreate) -> InventoryItemResponse:
        """Update inventory stock levels based on transaction."""
        try:
            # Get inventory item
            inventory_item = await self.inventory_repo.get_by_id(transaction_data.inventory_item_id)
            if not inventory_item:
                raise ValueError(f"Inventory item {transaction_data.inventory_item_id} not found")
            
            # Calculate stock change based on transaction type
            if transaction_data.transaction_type in ["purchase", "return_in", "adjustment_in"]:
                # Positive stock change
                quantity_change = transaction_data.quantity
            elif transaction_data.transaction_type in ["sale", "return_out", "adjustment_out", "expired", "damaged"]:
                # Negative stock change
                quantity_change = -transaction_data.quantity
                # Check if enough stock available
                if inventory_item.current_stock < transaction_data.quantity:
                    raise InsufficientStockException(
                        medicine_name="Unknown",  # Would get medicine name
                        available=inventory_item.current_stock,
                        requested=transaction_data.quantity
                    )
            else:
                raise ValueError(f"Invalid transaction type: {transaction_data.transaction_type}")
            
            # Update stock
            await self.inventory_repo.update_stock(
                pharmacy_id=inventory_item.pharmacy_id,
                medicine_id=inventory_item.medicine_id,
                quantity_change=quantity_change,
                transaction_type=transaction_data.transaction_type,
                reference_number=transaction_data.reference_number
            )
            
            # Get updated inventory item
            updated_item = await self.inventory_repo.get_by_id(transaction_data.inventory_item_id)
            
            # Get medicine details
            medicine = await self.medicine_repo.get_by_id(updated_item.medicine_id)
            
            # Convert to response format
            response = InventoryItemResponse(
                id=updated_item.id,
                pharmacy_id=updated_item.pharmacy_id,
                medicine_id=updated_item.medicine_id,
                medicine_name=medicine.name if medicine else "Unknown Medicine",
                current_stock=updated_item.current_stock,
                available_stock=updated_item.available_stock,
                reserved_stock=updated_item.reserved_stock,
                minimum_stock=updated_item.minimum_stock,
                reorder_point=updated_item.reorder_point,
                cost_price=updated_item.cost_price,
                selling_price=updated_item.selling_price,
                mrp=updated_item.mrp,
                needs_reorder=updated_item.needs_reorder,
                is_overstocked=updated_item.is_overstocked,
                storage_location=updated_item.storage_location
            )
            
            logger.info(f"Updated inventory stock: {quantity_change} units for item {updated_item.id}")
            return response
        except Exception as e:
            logger.error(f"Error updating inventory stock: {e}")
            raise