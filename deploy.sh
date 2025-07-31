#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and update with secure passwords"
    exit 1
fi

# Build and start all services in production mode
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

echo "eHealth Platform deployed successfully!"
echo "Access the platform at http://localhost"