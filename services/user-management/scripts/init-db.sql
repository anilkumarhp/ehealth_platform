-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ehealth_user_management;

-- Connect to the database
\c ehealth_user_management;

-- Create the UUID extension if it doesn't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the organizations table if it doesn't exist
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    type VARCHAR(50),
    registration_number VARCHAR(100) UNIQUE,
    abha_facility_id VARCHAR(100) UNIQUE,
    license_details JSONB,
    address JSONB,
    contact_info JSONB,
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'FREE',
    payment_gateway_order_id VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index on organization name
CREATE INDEX IF NOT EXISTS idx_organization_name ON organizations(name);

-- Create the Patients organization if it doesn't exist
INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at)
SELECT '11111111-1111-1111-1111-111111111111', 'Patients', TRUE, 'FREE', NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM organizations WHERE name = 'Patients'
);