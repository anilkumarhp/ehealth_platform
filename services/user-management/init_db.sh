#!/bin/bash
# Script to initialize the database

echo "Initializing database..."
cd /app
python -m app.db.init_db
echo "Database initialization complete"