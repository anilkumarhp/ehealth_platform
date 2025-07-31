"""
Script to modify the init_db.py file to check if tables exist before creating them.
"""
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def modify_init_db():
    """Modify the init_db.py file to check if tables exist before creating them"""
    try:
        # Path to the init_db.py file
        file_path = os.path.join('app', 'db', 'init_db.py')
        
        # Read the file
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Find the line where tables are created
        pattern = r'# Create all tables defined in the models\n\s+logger\.info\("Creating all tables from SQLAlchemy models"\)\n\s+Base\.metadata\.create_all\(bind=app_engine\)'
        
        # Replace with a version that checks if tables exist
        replacement = r'# Create all tables defined in the models\n        logger.info("Creating tables from SQLAlchemy models if they don\'t exist")\n        \n        # Check if tables exist before creating them\n        with app_engine.connect() as conn:\n            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = \'organizations\')"))\n            tables_exist = result.scalar()\n            \n        if not tables_exist:\n            Base.metadata.create_all(bind=app_engine)\n            logger.info("All tables created successfully")\n        else:\n            logger.info("Tables already exist, skipping creation")'
        
        # Perform the replacement
        modified_content = re.sub(pattern, replacement, content)
        
        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(modified_content)
        
        logger.info("Successfully modified init_db.py to check if tables exist")
        return True
    
    except Exception as e:
        logger.error(f"Error modifying init_db.py: {str(e)}")
        return False

if __name__ == "__main__":
    modify_init_db()