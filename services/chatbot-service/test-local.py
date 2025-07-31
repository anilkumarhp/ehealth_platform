import requests
import json
import time
import sys

def test_llm_service():
    """Test the LLM service directly"""
    print("Testing LLM service...")
    
    url = "http://localhost:8008/v1/completions"
    payload = {
        "prompt": "I have a headache, what should I do?",
        "max_tokens": 100
    }
    
    max_retries = 5
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"LLM response: {result['text']}")
                return True
            else:
                print(f"Attempt {i+1}/{max_retries}: LLM service returned {response.status_code}")
                print(response.text)
        except requests.exceptions.ConnectionError:
            print(f"Attempt {i+1}/{max_retries}: LLM service not ready yet")
        
        if i < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print("Failed to connect to LLM service after multiple attempts")
    return False

def test_chatbot_service():
    """Test the chatbot service"""
    print("\nTesting chatbot service...")
    
    url = "http://localhost:8002/api/v1/chat"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "I have a headache, what should I do?"
            }
        ],
        "max_tokens": 100
    }
    
    max_retries = 5
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                print("\nChatbot response:")
                print("-" * 50)
                print(f"User: {payload['messages'][0]['content']}")
                print(f"Assistant: {result['response']}")
                print("-" * 50)
                return True
            else:
                print(f"Attempt {i+1}/{max_retries}: Chatbot service returned {response.status_code}")
                print(response.text)
        except requests.exceptions.ConnectionError:
            print(f"Attempt {i+1}/{max_retries}: Chatbot service not ready yet")
        
        if i < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print("Failed to connect to chatbot service after multiple attempts")
    return False

if __name__ == "__main__":
    print("Starting tests...")
    print("=" * 50)
    
    llm_success = test_llm_service()
    if not llm_success:
        print("LLM service test failed")
        sys.exit(1)
    
    print("\nLLM service is working!")
    print("=" * 50)
    
    chatbot_success = test_chatbot_service()
    if not chatbot_success:
        print("Chatbot service test failed")
        sys.exit(1)
    
    print("\nAll tests passed successfully!")
    sys.exit(0)