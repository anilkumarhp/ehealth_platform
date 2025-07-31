"""
Script to modify the init_db.py file to handle the case where created_at and updated_at columns don't exist.
"""
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def modify_init_db():
    """Modify the init_db.py file to handle missing columns"""
    try:
        # Path to the init_db.py file
        file_path = os.path.join('app', 'db', 'init_db.py')
        
        # Read the file
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Find the SQL insert statement for roles
        pattern = r'text\("INSERT INTO roles \(id, name, description, organization_id, created_at, updated_at\) VALUES \(:id, :name, :description, :org_id, NOW\(\), NOW\(\)\)"\)'
        
        # Replace with a version that checks if the columns exist
        replacement = r'text("""DO $$ \n                    BEGIN \n                        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name=\'roles\' AND column_name=\'created_at\') THEN \n                            INSERT INTO roles (id, name, description, organization_id, created_at, updated_at) VALUES (:id, :name, :description, :org_id, NOW(), NOW()); \n                        ELSE \n                            INSERT INTO roles (id, name, description, organization_id) VALUES (:id, :name, :description, :org_id); \n                        END IF; \n                    END $$;""")'
        
        # Perform the replacement
        modified_content = re.sub(pattern, replacement, content)
        
        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(modified_content)
        
        logger.info("Successfully modified init_db.py to handle missing columns")
        return True
    
    except Exception as e:
        logger.error(f"Error modifying init_db.py: {str(e)}")
        return False

if __name__ == "__main__":
    modify_init_db()