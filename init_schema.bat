@echo off
echo Initializing database schema...

REM Get PostgreSQL connection details from environment variables or use defaults
set PGHOST=localhost
set PGPORT=5432
set PGDATABASE=ehealth_user_management
set PGUSER=postgres
set PGPASSWORD=postgres

REM Run the SQL script
psql -h %PGHOST% -p %PGPORT% -d %PGDATABASE% -U %PGUSER% -f services/user-management/scripts/init_schema.sql

echo Database schema initialized.
pause