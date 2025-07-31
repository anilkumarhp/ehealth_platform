"""
Simple script to run database population
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from populate_test_data import populate_database

if __name__ == "__main__":
    print("🚀 Starting database population...")
    asyncio.run(populate_database())
    print("✅ Database population completed!")