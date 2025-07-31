import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def init_db():
    """Initialize the database with migrations"""
    print("Initializing database...")
    
    # Create database engine
    engine = create_async_engine(settings.DATABASE_URL)
    
    # Try to connect to the database
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        print("Database connection successful")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Run migrations
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations applied successfully")
    except Exception as e:
        print(f"Error applying migrations: {e}")
        return
    
    print("Database initialization complete")

if __name__ == "__main__":
    asyncio.run(init_db())