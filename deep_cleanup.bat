@echo off
echo Performing deep cleanup of all Docker resources...

REM Stop all running containers
FOR /f "tokens=*" %%i IN ('docker ps -q') DO docker stop %%i

REM Remove all containers
FOR /f "tokens=*" %%i IN ('docker ps -a -q') DO docker rm %%i

REM Remove all volumes
docker volume prune -f

REM Remove all networks
docker network prune -f

REM Remove all images
docker image prune -a -f

echo Deep cleanup completed!