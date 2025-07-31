#!/bin/bash

# Define services and their ports
declare -A services=(
  ["user-management"]="8000"
  ["pharma-management"]="8001"
  ["chatbot-service"]="8002"
  ["lab-management"]="8003"
  ["notification-service"]="8004"
  ["hospital-management"]="8005"
)

# Build base image with common dependencies
docker build -t ehealth-base -f Dockerfile.base .

# Build each service
for service in "${!services[@]}"; do
  port=${services[$service]}
  echo "Building $service on port $port..."
  
  # Create temporary Dockerfile for this service
  cat > Dockerfile.$service <<EOF
FROM ehealth-base

WORKDIR /app

# Install service-specific dependencies
COPY ./services/$service/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY ./services/$service /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE $port

# Run the application with auto-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$port", "--reload"]
EOF

  # Build the service
  docker build -t ehealth-$service -f Dockerfile.$service .
  
  # Remove temporary Dockerfile
  rm Dockerfile.$service
done

echo "All services built successfully!"