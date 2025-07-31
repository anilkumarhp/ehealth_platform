#!/bin/bash

echo "Testing notification integration between user-management and notification services..."

# Test sending a notification from user-management to notification service
echo "Sending test notification..."
docker-compose exec user-management bash -c "cd /app && python test_notification_integration.py"

# Test the notification API directly
echo "Testing notification API..."
docker-compose exec notification bash -c "cd /app && python test_api.py"

# Test the gRPC client
echo "Testing gRPC client..."
docker-compose exec notification bash -c "cd /app && python test_grpc_client.py"

echo "Tests completed!"