#!/bin/bash

# Start all lab management services

echo "Starting Lab Management Services..."

# Start the main application
echo "Starting FastAPI application..."
docker-compose up -d app

# Start Celery worker
echo "Starting Celery worker..."
docker-compose up -d worker

# Start Celery beat scheduler
echo "Starting Celery beat scheduler..."
docker-compose up -d beat

# Check service status
echo "Checking service status..."
docker-compose ps

echo "All services started successfully!"
echo "API available at: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo "Health check: http://localhost:8000/api/v1/health/"