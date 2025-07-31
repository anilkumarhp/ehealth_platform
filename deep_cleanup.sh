#!/bin/bash
echo "Performing deep cleanup of all Docker resources..."

# Stop all running containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all volumes
docker volume prune -f

# Remove all networks
docker network prune -f

# Remove all images
docker image prune -a -f

echo "Deep cleanup completed!"