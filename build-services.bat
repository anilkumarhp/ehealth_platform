@echo off
setlocal enabledelayedexpansion

REM Create base Dockerfile
echo FROM python:3.10-slim > Dockerfile.base
echo WORKDIR /app >> Dockerfile.base
echo COPY requirements-base.txt /app/ >> Dockerfile.base
echo RUN pip install --no-cache-dir -r /app/requirements-base.txt >> Dockerfile.base

REM Build base image with common dependencies
docker build -t ehealth-base -f Dockerfile.base .

REM Define services and their ports
set "services=user-management pharma-management chatbot-service lab-management notification-service hospital-management"
set "user-management_port=8000"
set "pharma-management_port=8001"
set "chatbot-service_port=8002"
set "lab-management_port=8003"
set "notification-service_port=8004"
set "hospital-management_port=8005"

REM Build each service
for %%s in (%services%) do (
  set "service=%%s"
  set "port=!%%s_port!"
  echo Building !service! on port !port!...
  
  REM Create temporary Dockerfile for this service
  echo FROM ehealth-base > Dockerfile.!service!
  echo WORKDIR /app >> Dockerfile.!service!
  echo COPY ./services/!service!/requirements.txt /app/ >> Dockerfile.!service!
  echo RUN pip install --no-cache-dir -r /app/requirements.txt >> Dockerfile.!service!
  echo COPY ./services/!service! /app/ >> Dockerfile.!service!
  echo ENV PYTHONPATH=/app >> Dockerfile.!service!
  echo ENV PYTHONDONTWRITEBYTECODE=1 >> Dockerfile.!service!
  echo ENV PYTHONUNBUFFERED=1 >> Dockerfile.!service!
  echo EXPOSE !port! >> Dockerfile.!service!
  echo CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "!port!", "--reload"] >> Dockerfile.!service!
  
  REM Build the service
  docker build -t ehealth-!service! -f Dockerfile.!service! .
  
  REM Remove temporary Dockerfile
  del Dockerfile.!service!
)

echo All services built successfully!
del Dockerfile.base