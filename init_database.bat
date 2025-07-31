@echo off
echo Initializing database...

cd services\user-management

echo Running migrations...
alembic upgrade head

echo Creating Patients organization...
python -c "from app.scripts.ensure_patients_org import ensure_patients_organization_exists; ensure_patients_organization_exists()"

echo Database initialization complete.
pause