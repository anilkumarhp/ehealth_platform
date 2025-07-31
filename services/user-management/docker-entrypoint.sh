#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"

# Run migrations
alembic upgrade head

# Create default Patients organization
echo "Creating default Patients organization..."
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Patients') THEN
        INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at)
        VALUES ('11111111-1111-1111-1111-111111111111', 'Patients', true, 'FREE', NOW(), NOW());
        RAISE NOTICE 'Created default Patients organization';
    ELSE
        RAISE NOTICE 'Patients organization already exists';
    END IF;
END \$\$;
"

echo "Database initialization complete"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000