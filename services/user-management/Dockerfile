FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install celery psycopg2-binary boto3 python-jose[cryptography] stripe pyjwt cryptography

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV REDIS_URL=redis://shared-redis:6379/0
ENV NOTIFICATION_SERVICE_URL=notification:50051

# Expose the port
EXPOSE 8000

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Generate gRPC code and run the application
CMD ["bash", "-c", "python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/protos/notification.proto && /docker-entrypoint.sh"]