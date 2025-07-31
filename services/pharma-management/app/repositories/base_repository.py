"""
Base repository with common CRUD operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Type, TypeVar, Generic, Dict, Any
from uuid import UUID
import logging

from app.models.base import BaseModel

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    async def create(self, obj_data: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        try:
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with ID: {db_obj.id}")
            return db_obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get record by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            raise
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get multiple records with filtering and pagination."""
        try:
            query = select(self.model)
            
            # Apply filters
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, list):
                            filter_conditions.append(getattr(self.model, key).in_(value))
                        else:
                            filter_conditions.append(getattr(self.model, key) == value)
                
                if filter_conditions:
                    query = query.where(and_(*filter_conditions))
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise
    
    async def update(self, id: UUID, update_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update record by ID."""
        try:
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if not update_data:
                return await self.get_by_id(id)
            
            await self.db.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
            )
            await self.db.commit()
            
            logger.info(f"Updated {self.model.__name__} with ID: {id}")
            return await self.get_by_id(id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise
    
    async def delete(self, id: UUID) -> bool:
        """Soft delete record by ID."""
        try:
            await self.db.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(is_active=False)
            )
            await self.db.commit()
            
            logger.info(f"Deleted {self.model.__name__} with ID: {id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise
    
    async def hard_delete(self, id: UUID) -> bool:
        """Hard delete record by ID."""
        try:
            await self.db.execute(
                delete(self.model).where(self.model.id == id)
            )
            await self.db.commit()
            
            logger.info(f"Hard deleted {self.model.__name__} with ID: {id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error hard deleting {self.model.__name__} {id}: {e}")
            raise
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        try:
            query = select(self.model)
            
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        filter_conditions.append(getattr(self.model, key) == value)
                
                if filter_conditions:
                    query = query.where(and_(*filter_conditions))
            
            result = await self.db.execute(query)
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise
    
    async def exists(self, id: UUID) -> bool:
        """Check if record exists."""
        try:
            result = await self.db.execute(
                select(self.model.id).where(self.model.id == id)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id}: {e}")
            raise