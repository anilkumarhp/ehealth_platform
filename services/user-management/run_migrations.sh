#!/bin/bash

# Run Alembic migrations
echo "Running database migrations..."
cd /app
alembic upgrade head

echo "Migrations completed successfully!"