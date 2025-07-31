#!/bin/bash
echo "Adding image columns to users table..."

docker-compose exec user-management bash -c "cd /app && python -m scripts.add_image_columns"

echo "Done!"