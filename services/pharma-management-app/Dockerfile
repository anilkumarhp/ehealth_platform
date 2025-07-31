FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for gRPC
RUN apt-get update && apt-get install -y \
    build-essential \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files and generate gRPC code
COPY app/protos/ /app/app/protos/
RUN python -m grpc_tools.protoc \
    -I/app/app/protos \
    --python_out=/app/app/protos \
    --grpc_python_out=/app/app/protos \
    /app/app/protos/notification.proto \
    && touch /app/app/protos/__init__.py

# Copy the rest of the application
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]