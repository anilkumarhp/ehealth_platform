"""
Dynamic table creation for pharmacy-specific data isolation
"""

from sqlalchemy import MetaData, Table, Column, String, Integer, Numeric, DateTime, Boolean, ForeignKey, JSON, Text, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as UUIDType
import logging

logger = logging.getLogger(__name__)


class PharmacyTableManager:
    """Manages pharmacy-specific table creation and operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.metadata = MetaData()
    
    def get_pharmacy_table_name(self, pharmacy_id: UUIDType, base_table: str) -> str:
        """Generate pharmacy-specific table name."""
        pharmacy_short_id = str(pharmacy_id).replace('-', '')[:8]
        return f"{base_table}_pharma_{pharmacy_short_id}"
    
    async def create_pharmacy_tables(self, pharmacy_id: UUIDType) -> dict:
        """Create all necessary tables for a pharmacy."""
        try:
            tables_created = {}
            
            # Inventory table
            inventory_table_name = self.get_pharmacy_table_name(pharmacy_id, "inventory_items")
            inventory_table = Table(
                inventory_table_name,
                self.metadata,
                Column('id', UUID(as_uuid=True), primary_key=True),
                Column('medicine_id', UUID(as_uuid=True), nullable=False, index=True),
                Column('current_stock', Integer, nullable=False, default=0),
                Column('reserved_stock', Integer, nullable=False, default=0),
                Column('minimum_stock', Integer, nullable=False, default=10),
                Column('reorder_point', Integer, nullable=False, default=20),
                Column('cost_price', Numeric(10, 2), nullable=False),
                Column('selling_price', Numeric(10, 2), nullable=False),
                Column('mrp', Numeric(10, 2), nullable=False),
                Column('storage_location', String(100), nullable=True),
                Column('status', String(50), default="active"),
                Column('created_at', DateTime, nullable=False),
                Column('updated_at', DateTime, nullable=False),
                Column('is_active', Boolean, default=True)
            )
            tables_created['inventory'] = inventory_table_name
            
            # Orders table
            orders_table_name = self.get_pharmacy_table_name(pharmacy_id, "orders")
            orders_table = Table(
                orders_table_name,
                self.metadata,
                Column('id', UUID(as_uuid=True), primary_key=True),
                Column('order_number', String(100), nullable=False, unique=True),
                Column('patient_id', UUID(as_uuid=True), nullable=False),
                Column('prescription_id', UUID(as_uuid=True), nullable=True),
                Column('status', String(50), nullable=False, default="pending"),
                Column('total_amount', Numeric(10, 2), nullable=False),
                Column('payment_status', String(50), default="pending"),
                Column('delivery_type', String(50), default="pickup"),
                Column('created_at', DateTime, nullable=False),
                Column('updated_at', DateTime, nullable=False),
                Column('is_active', Boolean, default=True)
            )
            tables_created['orders'] = orders_table_name
            
            # Prescriptions table
            prescriptions_table_name = self.get_pharmacy_table_name(pharmacy_id, "prescriptions")
            prescriptions_table = Table(
                prescriptions_table_name,
                self.metadata,
                Column('id', UUID(as_uuid=True), primary_key=True),
                Column('prescription_number', String(100), nullable=False, unique=True),
                Column('patient_id', UUID(as_uuid=True), nullable=False),
                Column('doctor_id', UUID(as_uuid=True), nullable=False),
                Column('patient_name', String(255), nullable=False),
                Column('doctor_name', String(255), nullable=False),
                Column('issue_date', DateTime, nullable=False),
                Column('expiry_date', DateTime, nullable=False),
                Column('status', String(50), default="uploaded"),
                Column('validation_status', String(50), default="pending"),
                Column('created_at', DateTime, nullable=False),
                Column('updated_at', DateTime, nullable=False),
                Column('is_active', Boolean, default=True)
            )
            tables_created['prescriptions'] = prescriptions_table_name
            
            # Create tables in database
            await self.db.execute(f"CREATE SCHEMA IF NOT EXISTS pharma_{str(pharmacy_id).replace('-', '')[:8]}")
            
            # Use raw SQL to create tables
            for table in [inventory_table, orders_table, prescriptions_table]:
                create_sql = str(table.create_statement().compile(dialect=self.db.bind.dialect))
                await self.db.execute(create_sql)
            
            await self.db.commit()
            
            logger.info(f"Created pharmacy-specific tables for {pharmacy_id}: {tables_created}")
            return tables_created
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating pharmacy tables for {pharmacy_id}: {e}")
            raise
    
    async def drop_pharmacy_tables(self, pharmacy_id: UUIDType) -> bool:
        """Drop all tables for a pharmacy."""
        try:
            schema_name = f"pharma_{str(pharmacy_id).replace('-', '')[:8]}"
            await self.db.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
            await self.db.commit()
            
            logger.info(f"Dropped pharmacy tables for {pharmacy_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error dropping pharmacy tables for {pharmacy_id}: {e}")
            raise
    
    def get_pharmacy_inventory_table(self, pharmacy_id: UUIDType) -> str:
        """Get pharmacy-specific inventory table name."""
        return self.get_pharmacy_table_name(pharmacy_id, "inventory_items")
    
    def get_pharmacy_orders_table(self, pharmacy_id: UUIDType) -> str:
        """Get pharmacy-specific orders table name."""
        return self.get_pharmacy_table_name(pharmacy_id, "orders")
    
    def get_pharmacy_prescriptions_table(self, pharmacy_id: UUIDType) -> str:
        """Get pharmacy-specific prescriptions table name."""
        return self.get_pharmacy_table_name(pharmacy_id, "prescriptions")