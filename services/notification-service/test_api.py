import requests
import json
import sys

def test_notification_api():
    base_url = "http://localhost:8004/api/v1"
    user_id = "test-user-123"
    notification_id = "user_management:test-notif-123"
    
    print("1. Creating a notification...")
    create_response = requests.post(
        f"{base_url}/notifications/",
        json={
            "id": "test-notif-123",
            "service": "user_management",
            "type": "info",
            "title": "Test Notification",
            "message": "This is a test notification",
            "user_id": user_id
        }
    )
    print(f"Status: {create_response.status_code}")
    print(f"Response: {create_response.json()}")
    
    print("\n2. Getting user notifications...")
    get_response = requests.get(f"{base_url}/notifications/user/{user_id}")
    print(f"Status: {get_response.status_code}")
    print(f"Response: {json.dumps(get_response.json(), indent=2)}")
    
    print("\n3. Marking notification as read...")
    mark_response = requests.put(f"{base_url}/notifications/user/{user_id}/{notification_id}/read")
    print(f"Status: {mark_response.status_code}")
    print(f"Response: {mark_response.json()}")
    
    print("\n4. Getting user notifications again (should be marked as read)...")
    get_response = requests.get(f"{base_url}/notifications/user/{user_id}")
    print(f"Status: {get_response.status_code}")
    print(f"Response: {json.dumps(get_response.json(), indent=2)}")
    
    print("\nManual testing completed!")

if __name__ == "__main__":
    test_notification_api()