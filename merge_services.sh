#!/bin/bash

# Exit on error
set -e

# Define services to merge
SERVICES=("user-management" "lab-management" "pharma-management" "hospital-management")

# Function to merge API service into core service
merge_service() {
  local service=$1
  local api_service="${service}-api"
  
  echo "Merging ${api_service} into ${service}..."
  
  # Check if both directories exist
  if [ ! -d "./services/${service}" ]; then
    echo "Error: ${service} directory not found"
    return 1
  fi
  
  if [ ! -d "./services/${api_service}" ]; then
    echo "Warning: ${api_service} directory not found, skipping"
    return 0
  fi
  
  # Create protos directory in core service if it doesn't exist
  mkdir -p "./services/${service}/app/protos"
  
  # Copy notification proto files
  if [ -d "./services/${api_service}/app/protos" ]; then
    cp -r "./services/${api_service}/app/protos/"* "./services/${service}/app/protos/"
    echo "  - Copied proto files"
  fi
  
  # Copy gRPC client implementation
  if [ -f "./services/${api_service}/app/grpc_client.py" ]; then
    cp "./services/${api_service}/app/grpc_client.py" "./services/${service}/app/"
    echo "  - Copied gRPC client"
  fi
  
  # Copy notification examples
  if [ -f "./services/${api_service}/app/api/notification_examples.py" ]; then
    mkdir -p "./services/${service}/app/api"
    cp "./services/${api_service}/app/api/notification_examples.py" "./services/${service}/app/api/"
    echo "  - Copied notification examples"
  fi
  
  # Update requirements.txt to include gRPC dependencies
  if [ -f "./services/${service}/requirements.txt" ]; then
    if ! grep -q "grpcio" "./services/${service}/requirements.txt"; then
      echo "grpcio==1.54.0" >> "./services/${service}/requirements.txt"
      echo "grpcio-tools==1.54.0" >> "./services/${service}/requirements.txt"
      echo "protobuf==4.22.3" >> "./services/${service}/requirements.txt"
      echo "  - Updated requirements.txt with gRPC dependencies"
    fi
  fi
  
  echo "Merge completed for ${service}"
}

# Process each service
for service in "${SERVICES[@]}"; do
  merge_service "$service"
done

echo "All services merged successfully!"
echo "Note: You may need to update imports in the merged files to match the new directory structure."