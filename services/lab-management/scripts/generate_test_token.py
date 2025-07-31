#!/usr/bin/env python3
"""
Generate a test JWT token for API testing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jwt
from datetime import datetime, timedelta
from uuid import UUID

# Test user data
TEST_USER_DATA = {
    "sub": "12345678-1234-4234-8234-123456789012",
    "full_name": "Test User",
    "date_of_birth": "1990-01-01",
    "gender": "M",
    "primary_mobile_number": "+1234567890",
    "email": "test@example.com",
    "roles": ["lab-admin"],
    "org_id": "87654321-4321-4321-8321-210987654321",
    "exp": datetime.utcnow() + timedelta(hours=1),
    "iat": datetime.utcnow()
}

# Secret key (same as in config)
SECRET_KEY = "a_very_secret_key_that_should_be_changed"

def generate_token():
    """Generate a JWT token for testing."""
    token = jwt.encode(TEST_USER_DATA, SECRET_KEY, algorithm="HS256")
    return token

if __name__ == "__main__":
    token = generate_token()
    print("Test JWT Token (1 hour expiry):")
    print("=" * 50)
    print(token)
    print("=" * 50)
    print("\nToken Details:")
    print(f"User ID: {TEST_USER_DATA['sub']}")
    print(f"Name: {TEST_USER_DATA['full_name']}")
    print(f"Email: {TEST_USER_DATA['email']}")
    print(f"Org ID: {TEST_USER_DATA['org_id']}")
    print(f"Roles: {TEST_USER_DATA['roles']}")
    print(f"Expires: {TEST_USER_DATA['exp']}")
    print("\nUsage in Swagger:")
    print("1. Go to http://localhost:8000/docs")
    print("2. Click 'Authorize' button")
    print("3. Enter: Bearer <token>")
    print("4. Replace <token> with the token above")