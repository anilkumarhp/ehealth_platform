#!/bin/bash
echo "Stopping all Docker containers and cleaning up resources..."

# Stop and remove all containers
docker-compose -f docker-compose.yml down -v
cd services/notification-service && docker-compose down -v && cd ../..
cd services/user-management && docker-compose down -v && cd ../..
cd services/chatbot-service && docker-compose down -v && cd ../..

# Remove all stopped containers, dangling images, and unused networks
docker system prune -f

echo "Cleanup completed!"