@echo off
echo Rebuilding and restarting services...

echo Stopping all services...
docker-compose down

echo Rebuilding user-management service...
docker-compose build user-management

echo Starting all services...
docker-compose up -d

echo Services restarted.
echo You can check the logs with: docker-compose logs -f user-management
pause