@echo off
echo Checking eHealth Platform services...
echo.

echo Checking User Management Service...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/health > temp.txt
set /p status=<temp.txt
del temp.txt
if "%status%"=="200" (
    echo [OK] User Management Service is running
) else (
    echo [ERROR] User Management Service is not running or not responding
)

echo Checking Notification Service...
curl -s -o nul -w "%%{http_code}" http://localhost:8004/api/v1/health > temp.txt
set /p status=<temp.txt
del temp.txt
if "%status%"=="200" (
    echo [OK] Notification Service is running
) else (
    echo [ERROR] Notification Service is not running or not responding
)

echo Checking Chatbot Service...
curl -s -o nul -w "%%{http_code}" http://localhost:8002/api/v1/health > temp.txt
set /p status=<temp.txt
del temp.txt
if "%status%"=="200" (
    echo [OK] Chatbot Service is running
) else (
    echo [ERROR] Chatbot Service is not running or not responding
)

echo.
echo If any services are not running, please start them using:
echo ./run_all_services.bat
echo.
pause