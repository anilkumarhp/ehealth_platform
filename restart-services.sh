#!/bin/bash

echo "Stopping all services..."
docker-compose down

echo "Starting all services with updated configuration..."
docker-compose up --build