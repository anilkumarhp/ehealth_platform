@echo off
echo Starting eHealth Platform services...

echo Step 1: Starting database...
docker-compose -f db-only.docker-compose.yml up -d
echo Waiting for database to be ready...
timeout /t 10

echo Step 2: Initializing database schema...
psql -h localhost -p 5432 -d ehealth_user_management -U postgres -f services/user-management/scripts/init_schema.sql

echo Step 3: Starting services...
docker-compose up -d

echo All services started.
echo You can check the logs with: docker-compose logs -f
pause