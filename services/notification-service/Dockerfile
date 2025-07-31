FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for gRPC
RUN apt-get update && apt-get install -y \
    build-essential \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Generate gRPC code
RUN python -m grpc_tools.protoc \
    -I./app/protos \
    --python_out=./app/protos \
    --grpc_python_out=./app/protos \
    ./app/protos/notification.proto \
    && touch ./app/protos/__init__.py

# Expose the ports
EXPOSE 8004
EXPOSE 50051

# Run the application with auto-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]