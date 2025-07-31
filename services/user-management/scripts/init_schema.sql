-- Create the database schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create organizations table
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

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret VARCHAR,
    abha_id VARCHAR(100) UNIQUE,
    role VARCHAR(50) NOT NULL DEFAULT 'PATIENT',
    permissions VARCHAR[],
    personal_info JSONB,
    profile_data JSONB,
    last_login TIMESTAMP,
    invitation_token VARCHAR UNIQUE,
    invitation_expires_at TIMESTAMP,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    password_reset_token VARCHAR UNIQUE,
    password_reset_expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    primary_phone VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create default Patients organization
INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at)
SELECT '11111111-1111-1111-1111-111111111111', 'Patients', TRUE, 'FREE', NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM organizations WHERE name = 'Patients'
);