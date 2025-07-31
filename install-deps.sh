#!/bin/bash

echo "Installing dependencies for user-management service..."
docker-compose exec user-management bash -c "pip install -r requirements.txt && pip install celery psycopg2-binary boto3 python-jose[cryptography] && python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/protos/notification.proto"

echo "Installing dependencies for notification service..."
docker-compose exec notification bash -c "pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-dev.txt && python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/protos/notification.proto"