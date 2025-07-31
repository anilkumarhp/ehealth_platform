import requests
import json

API_URL = "http://localhost:8000"

def test_register_with_mfa():
    url = f"{API_URL}/api/v1/auth/register-with-mfa"
    
    data = {
        "email": "test_mfa@example.com",
        "password": "Password123!",
        "primary_phone": "1234567890",
        "enable_mfa": True,
        "organization_name": "Test Org",
        "personal_info": {
            "first_name": "Test",
            "last_name": "User"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_register_with_mfa()