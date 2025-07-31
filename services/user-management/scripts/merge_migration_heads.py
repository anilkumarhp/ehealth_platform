"""
Script to merge multiple Alembic migration heads.
"""
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_migration_heads():
    """Merge multiple Alembic migration heads"""
    try:
        # Get the current heads
        result = subprocess.run(
            ["alembic", "heads"],
            capture_output=True,
            text=True,
            check=True
        )
        
        heads = [line.split(' ')[0] for line in result.stdout.strip().split('\n')]
        
        if len(heads) <= 1:
            logger.info("No multiple heads found, nothing to merge")
            return True
        
        logger.info(f"Found {len(heads)} migration heads: {heads}")
        
        # Create a merge migration
        merge_message = "Merge multiple heads"
        subprocess.run(
            ["alembic", "merge", "-m", merge_message] + heads,
            check=True
        )
        
        logger.info("Successfully merged migration heads")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running alembic command: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error merging migration heads: {str(e)}")
        return False

if __name__ == "__main__":
    merge_migration_heads()