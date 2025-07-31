FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for gRPC
RUN apt-get update && apt-get install -y \
    build-essential \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Compile protobuf files
RUN python -m grpc_tools.protoc -I./protos --python_out=./app/generated --grpc_python_out=./app/generated ./protos/*.proto

# Expose the port
EXPOSE 8003

# Run the application with auto-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]