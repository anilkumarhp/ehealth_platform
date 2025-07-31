#!/bin/bash

echo "Starting notification service only..."
docker-compose -f notification-only.yml up --build