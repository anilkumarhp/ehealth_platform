#!/bin/bash
# Script to directly add timestamp columns to the roles table

# Connect to PostgreSQL and execute SQL commands
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "
-- Add created_at column if it doesn't exist
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'roles' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE roles ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;
        RAISE NOTICE 'Added created_at column to roles table';
    ELSE
        RAISE NOTICE 'created_at column already exists in roles table';
    END IF;
END \$\$;

-- Add updated_at column if it doesn't exist
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'roles' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE roles ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;
        RAISE NOTICE 'Added updated_at column to roles table';
    ELSE
        RAISE NOTICE 'updated_at column already exists in roles table';
    END IF;
END \$\$;
"

echo "Added timestamp columns to roles table if they didn't exist"