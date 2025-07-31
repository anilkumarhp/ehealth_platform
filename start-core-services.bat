@echo off
echo Starting core services (user-management and notification)...

REM Stop any running containers
docker-compose down

REM Start only the required services
docker-compose up -d shared-redis user-management-db notification user-management

REM Show logs
docker-compose logs -f notification user-management