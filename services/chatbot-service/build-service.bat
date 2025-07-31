@echo off
echo Building chatbot service...
cd ..\..\
docker-compose build --no-cache chatbot-service
echo Done!
pause