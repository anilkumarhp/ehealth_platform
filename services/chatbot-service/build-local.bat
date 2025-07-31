@echo off
echo Building chatbot API service locally...
docker-compose build --no-cache chatbot-api
echo Done!
pause