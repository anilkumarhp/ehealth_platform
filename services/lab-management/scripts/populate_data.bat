@echo off

echo 🔧 Lab Management Data Population Script
echo ========================================

echo 📦 Running in Windows environment

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo 📁 Project root: %PROJECT_ROOT%
echo 📁 Script directory: %SCRIPT_DIR%

REM Change to project root
cd /d "%PROJECT_ROOT%"

echo 🔍 Checking database connection...
python -c "
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
"

if %ERRORLEVEL% neq 0 (
    echo ❌ Cannot connect to database. Please ensure the database is running.
    exit /b 1
)

echo 🔄 Running database migrations...
where alembic >nul 2>nul
if %ERRORLEVEL% equ 0 (
    alembic upgrade head
    if %ERRORLEVEL% neq 0 (
        echo ⚠️  Migration failed, but continuing with data population...
    )
) else (
    echo ⚠️  Alembic not found, skipping migrations...
)

echo 📊 Populating database with sample data...
python scripts\populate_data.py

if %ERRORLEVEL% equ 0 (
    echo 🎉 Data population completed successfully!
    echo.
    echo 📋 Sample data created:
    echo   - 5 Lab Services with test definitions
    echo   - 5 Test Orders for different patients
    echo   - 3 Appointments ^(scheduled^)
    echo   - 3 Labs, 3 Patients, 3 Doctors ^(referenced by UUID^)
    echo.
    echo 🔗 You can now test the API endpoints with the populated data.
) else (
    echo ❌ Data population failed!
    exit /b 1
)