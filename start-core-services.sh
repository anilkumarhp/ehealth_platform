#!/bin/bash

echo "Starting core services (user-management and notification)..."

# Stop any running containers
docker-compose down

# Start only the required services
docker-compose up -d shared-redis user-management-db notification user-management

# Show logs
docker-compose logs -f notification user-management