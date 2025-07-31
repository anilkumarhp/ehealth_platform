#!/bin/bash

# Build base image with common dependencies
echo "Building base image with common dependencies..."
docker build -t ehealth-base -f Dockerfile.base .

# Run docker-compose with build
echo "Starting all services..."
docker-compose up --build