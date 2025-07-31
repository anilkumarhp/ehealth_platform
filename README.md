# eHealth Platform

## Running Services

### Database Migrations

If you need to run database migrations manually:

```bash
# From the root directory
./run_migrations.bat  # Windows
./run_migrations.sh   # Linux/Mac
```

Migrations are automatically run when starting the services with docker-compose.

### Option 1: Run All Services Together (Recommended)

This option uses a shared Redis instance for all services:

```bash
# From the root directory
./run_all_services.bat
```

### Option 2: Run Services Individually

Each service can be run individually with its own Redis instance:

```bash
# Run User Management Service
cd services/user-management
docker-compose up --build

# Run Notification Service
cd services/notification-service
docker-compose up --build

# Run Chatbot Service
cd services/chatbot-service
docker-compose up --build
```

## Cleaning Up Docker Resources

### Standard Cleanup

To stop all containers and remove volumes for the eHealth platform:

```bash
# From the root directory
./cleanup.bat  # Windows
./cleanup.sh   # Linux/Mac
```

### Deep Cleanup

To stop and remove ALL Docker containers, volumes, networks, and images on your system:

```bash
# From the root directory
./deep_cleanup.bat  # Windows
./deep_cleanup.sh   # Linux/Mac
```

## Service Ports

- User Management: 8000
- Notification Service: 8004 (REST), 50051 (gRPC)
- Chatbot Service: 8002
- LLM Service: 8008

## Redis Ports

When running services individually:
- User Management Redis: 6382
- Notification Service Redis: 6380
- Chatbot Service Redis: 6381

When running all services together:
- Shared Redis: 6379