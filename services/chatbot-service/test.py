import requests
import time
import sys

def test_ollama_service():
    """Test the Ollama service directly"""
    print("Testing Ollama service...")
    
    url = "http://localhost:8008/api/generate"
    payload = {
        "model": "phi3:mini",
        "prompt": "I have a headache, what should I do?",
        "system": "You are a helpful healthcare assistant."
    }
    
    max_retries = 10
    retry_delay = 10
    
    for i in range(max_retries):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"Ollama response: {result['response']}")
                return True
            else:
                print(f"Attempt {i+1}/{max_retries}: Ollama service returned {response.status_code}")
                print(response.text)
        except requests.exceptions.ConnectionError:
            print(f"Attempt {i+1}/{max_retries}: Ollama service not ready yet")
        
        if i < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print("Failed to connect to Ollama service after multiple attempts")
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
        ]
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
                print(f"Intent: {result['intent']}")
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

def test_appointment_scenario():
    """Test the appointment scheduling scenario"""
    print("\nTesting appointment scheduling scenario...")
    
    url = "http://localhost:8002/api/v1/chat"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "I'd like to schedule an appointment with a doctor"
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("\nAppointment scenario response:")
            print("-" * 50)
            print(f"User: {payload['messages'][0]['content']}")
            print(f"Assistant: {result['response']}")
            print(f"Intent: {result['intent']}")
            print(f"Requires auth: {result['requires_auth']}")
            print("-" * 50)
            return True
        else:
            print(f"Appointment scenario test failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error in appointment scenario test: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting tests...")
    print("=" * 50)
    
    ollama_success = test_ollama_service()
    if not ollama_success:
        print("Ollama service test failed")
        sys.exit(1)
    
    print("\nOllama service is working!")
    print("=" * 50)
    
    chatbot_success = test_chatbot_service()
    if not chatbot_success:
        print("Chatbot service test failed")
        sys.exit(1)
    
    print("\nChatbot service is working!")
    print("=" * 50)
    
    appointment_success = test_appointment_scenario()
    if not appointment_success:
        print("Appointment scenario test failed")
        sys.exit(1)
    
    print("\nAll tests passed successfully!")
    sys.exit(0)