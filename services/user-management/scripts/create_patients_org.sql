-- Create the Patients organization with a fixed UUID if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Patients') THEN
        INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at)
        VALUES ('11111111-1111-1111-1111-111111111111', 'Patients', true, 'FREE', NOW(), NOW());
        RAISE NOTICE 'Created default Patients organization';
    ELSE
        RAISE NOTICE 'Patients organization already exists';
    END IF;
END $$;