@echo off
echo Starting PostgreSQL database...
docker-compose -f db-only.docker-compose.yml up -d
echo Database started. You can now run the services.
pause