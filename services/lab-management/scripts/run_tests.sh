#!/bin/bash

# Script to run tests in Docker environment

echo "Starting database and dependencies..."
docker-compose up -d db redis

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker-compose run --rm app alembic upgrade head

echo "Running tests..."
docker-compose run --rm test

echo "Cleaning up..."
docker-compose down