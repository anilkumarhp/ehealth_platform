#!/bin/bash

# Set Python path
export PYTHONPATH=/app

# Install dependencies
pip install -r requirements.txt
pip install celery psycopg2-binary boto3 python-jose[cryptography] stripe pyjwt cryptography

# Generate gRPC code
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/protos/notification.proto

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug