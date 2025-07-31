import requests
import json
import sys

def test_chatbot_service():
    """
    Test the chatbot service by sending a chat request and printing the response.
    """
    print("Testing chatbot service...")
    
    # Define the API endpoint
    url = "http://localhost:8002/api/v1/chat"
    
    # Define the request payload
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, I'm having a headache. What should I do?"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    # Send the request
    try:
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("\nChatbot response:")
            print("-" * 50)
            print(f"User: {payload['messages'][0]['content']}")
            print(f"Assistant: {result['response']}")
            print("-" * 50)
            print("\nTest successful!")
            return True
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_chatbot_service()
    sys.exit(0 if success else 1)