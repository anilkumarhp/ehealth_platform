#!/bin/bash

echo "Stopping all Docker containers and cleaning up resources..."

# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Remove all volumes
docker volume prune -f

# Remove all networks
docker network prune -f

# Remove dangling images
docker image prune -f

echo "Cleanup completed!"