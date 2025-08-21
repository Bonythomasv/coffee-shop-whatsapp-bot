#!/usr/bin/env python3
"""
Test script for webhook endpoints and API routes.
"""

import requests
import json
import time

# Base URL for the Flask application
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_best_selling_api():
    """Test the best-selling items API."""
    print("\\nTesting best-selling items API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sales/best-selling?limit=5")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cache_status():
    """Test the cache status API."""
    print("\\nTesting cache status API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sales/cache-status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_refresh_sales_data():
    """Test the refresh sales data API."""
    print("\\nTesting refresh sales data API...")
    
    try:
        data = {
            "merchant_id": "TEST_MERCHANT_001",
            "days_back": 7
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sales/refresh",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_webhook_simulation():
    """Test the webhook simulation endpoint."""
    print("\\nTesting webhook simulation...")
    
    try:
        # Test different types of messages
        test_messages = [
            "What's my best-selling drink this week?",
            "Hello",
            "Help",
            "Show me coffee sales",
            "How many cappuccinos did I sell?"
        ]
        
        for message in test_messages:
            print(f"\\nTesting message: '{message}'")
            
            data = {
                "MessageSid": f"TEST_MSG_{int(time.time())}",
                "From": "whatsapp:+1234567890",
                "To": "whatsapp:+14155238886",
                "Body": message
            }
            
            response = requests.post(
                f"{BASE_URL}/api/test/webhook",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result.get('response', 'No response')}")
            else:
                print(f"Error: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_messages_api():
    """Test the messages API."""
    print("\\nTesting messages API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/messages?limit=10")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting webhook and API tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Best Selling API", test_best_selling_api),
        ("Cache Status", test_cache_status),
        ("Refresh Sales Data", test_refresh_sales_data),
        ("Webhook Simulation", test_webhook_simulation),
        ("Messages API", test_messages_api)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\\n" + "="*50)
    print("Test Results Summary:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

if __name__ == "__main__":
    main()

