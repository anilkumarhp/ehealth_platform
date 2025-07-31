# alembic/env.py (Final Corrected Version)

import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# --- THIS IS THE ROBUST FIX ---
# 1. Load environment variables from the .env file in the project root
load_dotenv()

# 2. Get the database URL from the environment
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")
# --- END OF FIX ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- THIS IS THE ROBUST FIX ---
# 3. Programmatically set the sqlalchemy.url in the config object
config.set_main_option("sqlalchemy.url", db_url)
# --- END OF FIX ---


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import our project's Base and models so Alembic can see them
from app.db.base import Base
from app.models import report, appointment, payment, lab_service, test_definition, access_permission, access_request, audit_log, test_order

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,  # Use the db_url directly
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())