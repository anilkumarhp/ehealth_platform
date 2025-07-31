#!/bin/bash
# Script to fix the init_db.py file to handle the case where the tables already exist

# Path to the init_db.py file
INIT_DB_FILE="/app/app/db/init_db.py"

# Create a backup of the original file
cp "$INIT_DB_FILE" "${INIT_DB_FILE}.bak"

# Replace the create_all call with a conditional check
sed -i 's/Base.metadata.create_all(bind=app_engine)/# Check if tables exist before creating them\n        with app_engine.connect() as conn:\n            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '\''organizations'\'')"))\n            tables_exist = result.scalar()\n            \n        if not tables_exist:\n            Base.metadata.create_all(bind=app_engine)\n            logger.info("All tables created successfully")\n        else:\n            logger.info("Tables already exist, skipping creation")/' "$INIT_DB_FILE"

# Replace the INSERT INTO roles statement with a conditional check
sed -i 's/text("INSERT INTO roles (id, name, description, organization_id, created_at, updated_at) VALUES (:id, :name, :description, :org_id, NOW(), NOW())")/text("""DO $$ \n                    BEGIN \n                        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='\''roles'\'' AND column_name='\''created_at'\'') THEN \n                            INSERT INTO roles (id, name, description, organization_id, created_at, updated_at) \n                            VALUES (:id, :name, :description, :org_id, NOW(), NOW()) \n                            ON CONFLICT DO NOTHING; \n                        ELSE \n                            INSERT INTO roles (id, name, description, organization_id) \n                            VALUES (:id, :name, :description, :org_id) \n                            ON CONFLICT DO NOTHING; \n                        END IF; \n                    END $$;""")/' "$INIT_DB_FILE"

echo "Fixed init_db.py file to handle existing tables"