@echo off
echo Rebuilding and restarting services...

echo Stopping all services...
docker-compose down -v

echo Rebuilding services...
docker-compose build

echo Starting all services...
docker-compose up -d

echo Services restarted.
echo You can check the logs with: docker-compose logs -f user-management
pause