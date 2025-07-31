#!/bin/bash

echo "Starting user-management and notification services..."
docker-compose -f user-notification.yml up --build