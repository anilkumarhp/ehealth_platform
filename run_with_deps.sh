#!/bin/bash

echo "Starting all eHealth Platform services with full dependencies..."

# Clean up any existing containers
docker-compose down

# Start the services
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Install additional dependencies for user-management if needed
echo "Installing additional dependencies for user-management..."
docker-compose exec user-management bash -c "pip install -r requirements.txt && pip install celery psycopg2-binary boto3 python-jose[cryptography] stripe pyjwt cryptography"

# Install additional dependencies for notification service if needed
echo "Installing additional dependencies for notification service..."
docker-compose exec notification bash -c "pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-dev.txt && pip install aioredis==2.0.1 python-socketio==5.10.0 websockets==12.0"

# Generate gRPC code for both services
echo "Generating gRPC code for user-management..."
docker-compose exec user-management bash -c "python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/protos/notification.proto"

echo "Generating gRPC code for notification service..."
docker-compose exec notification bash -c "python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/protos/notification.proto"

# Show logs
echo "Services started. Showing logs..."
docker-compose logs -f