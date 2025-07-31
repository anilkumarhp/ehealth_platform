@echo off
echo Creating default Patients organization...

REM Get PostgreSQL connection details from environment variables or use defaults
set PGHOST=%POSTGRES_HOST%
if "%PGHOST%"=="" set PGHOST=localhost
set PGPORT=%POSTGRES_PORT%
if "%PGPORT%"=="" set PGPORT=5432
set PGDATABASE=%POSTGRES_DB%
if "%PGDATABASE%"=="" set PGDATABASE=ehealth_user_management
set PGUSER=%POSTGRES_USER%
if "%PGUSER%"=="" set PGUSER=postgres
set PGPASSWORD=%POSTGRES_PASSWORD%
if "%PGPASSWORD%"=="" set PGPASSWORD=postgres

REM Run the SQL script
psql -h %PGHOST% -p %PGPORT% -d %PGDATABASE% -U %PGUSER% -f scripts/create_patients_org.sql

echo Done.
pause