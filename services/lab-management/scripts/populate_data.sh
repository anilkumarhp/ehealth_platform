#!/bin/bash

# Script to populate the lab management database with sample data

echo "🔧 Lab Management Data Population Script"
echo "========================================"

# Check if we're in Docker environment
if [ -f /.dockerenv ]; then
    echo "📦 Running in Docker environment"
    PYTHON_CMD="python"
else
    echo "💻 Running in local environment"
    PYTHON_CMD="python3"
fi

# Set the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Script directory: $SCRIPT_DIR"

# Change to project root
cd "$PROJECT_ROOT"

# Check if database is accessible
echo "🔍 Checking database connection..."
if ! $PYTHON_CMD -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def check_db():
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.execute('SELECT 1')
        await engine.dispose()
        print('✅ Database connection successful')
        return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

result = asyncio.run(check_db())
exit(0 if result else 1)
"; then
    echo "❌ Cannot connect to database. Please ensure the database is running."
    exit 1
fi

# Run database migrations first
echo "🔄 Running database migrations..."
if command -v alembic &> /dev/null; then
    alembic upgrade head
    if [ $? -ne 0 ]; then
        echo "⚠️  Migration failed, but continuing with data population..."
    fi
else
    echo "⚠️  Alembic not found, skipping migrations..."
fi

# Run the population script
echo "📊 Populating database with sample data..."
$PYTHON_CMD scripts/populate_data.py

if [ $? -eq 0 ]; then
    echo "🎉 Data population completed successfully!"
    echo ""
    echo "📋 Sample data created:"
    echo "  - 5 Lab Services with test definitions"
    echo "  - 5 Test Orders for different patients"
    echo "  - 3 Appointments (scheduled)"
    echo "  - 3 Labs, 3 Patients, 3 Doctors (referenced by UUID)"
    echo ""
    echo "🔗 You can now test the API endpoints with the populated data."
else
    echo "❌ Data population failed!"
    exit 1
fi