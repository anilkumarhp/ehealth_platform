@echo off
echo Running database migrations...

echo Creating merge migration if needed...
docker-compose exec user-management bash -c "cd /app && alembic merge heads -m merge_multiple_heads"

echo Applying all migrations...
docker-compose exec user-management bash -c "cd /app && alembic upgrade heads"

echo Migrations completed successfully!