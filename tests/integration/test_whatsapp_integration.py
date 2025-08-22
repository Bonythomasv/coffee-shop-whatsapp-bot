#!/usr/bin/env python3
"""
Test script for WhatsApp integration and end-to-end message flow.
"""

import os
import sys
import requests
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.main import app
from src.services.whatsapp_client import WhatsAppClient
from src.services.sales_processor import SalesProcessor

def test_whatsapp_client():
    """Test WhatsApp client functionality."""
    print("Testing WhatsApp Client...")
    print("=" * 50)
    
    client = WhatsAppClient()
    
    # Test phone number validation
    test_numbers = [
        '+1234567890',
        'whatsapp:+1234567890',
        '+44123456789',
        '1234567890',  # Invalid - no +
        '+123',        # Invalid - too short
        '+123456789012345678'  # Invalid - too long
    ]
    
    print("Phone number validation tests:")
    for number in test_numbers:
        is_valid = client.validate_phone_number(number)
        print(f"  {number}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test sending messages
    print("\\nMessage sending tests:")
    
    test_messages = [
        {
            'to': '+1234567890',
            'message': 'Hello! This is a test message from your coffee shop bot.',
            'description': 'Simple text message'
        },
        {
            'to': 'whatsapp:+1234567890',
            'message': 'Your best-selling drink this week is Cappuccino with 150 units sold!',
            'description': 'Sales update message'
        }
    ]
    
    for test_msg in test_messages:
        print(f"\\nTesting: {test_msg['description']}")
        result = client.send_message(test_msg['to'], test_msg['message'])
        
        if result['success']:
            print(f"✅ Message sent successfully")
            print(f"   Message SID: {result['message_sid']}")
            print(f"   Status: {result.get('status', 'unknown')}")
            if result.get('mock'):
                print("   (Mock mode - no actual message sent)")
        else:
            print(f"❌ Failed to send message: {result['error']}")

def test_message_formatting():
    """Test business message formatting."""
    print("\\nTesting Message Formatting...")
    print("=" * 50)
    
    client = WhatsAppClient()
    
    # Mock sales data
    mock_sales_data = {
        'best_selling_items': [
            {'item_name': 'Cappuccino', 'quantity_sold': 150, 'total_revenue': 750.0, 'category': 'Coffee'},
            {'item_name': 'Latte', 'quantity_sold': 120, 'total_revenue': 660.0, 'category': 'Coffee'},
            {'item_name': 'Espresso', 'quantity_sold': 80, 'total_revenue': 320.0, 'category': 'Coffee'},
            {'item_name': 'Croissant', 'quantity_sold': 45, 'total_revenue': 135.0, 'category': 'Pastry'},
            {'item_name': 'Muffin', 'quantity_sold': 30, 'total_revenue': 105.0, 'category': 'Pastry'}
        ]
    }
    
    # Test different message formats
    formats = ['sales_summary', 'best_selling', 'revenue_report']
    
    for format_type in formats:
        print(f"\\n{format_type.replace('_', ' ').title()} Format:")
        print("-" * 30)
        formatted_msg = client.format_business_message(mock_sales_data, format_type)
        print(formatted_msg)

def test_end_to_end_flow():
    """Test end-to-end WhatsApp message flow."""
    print("\\nTesting End-to-End Flow...")
    print("=" * 50)
    
    with app.app_context():
        # Refresh sales data
        sales_processor = SalesProcessor()
        sales_processor.process_and_cache_sales_data("TEST_MERCHANT_001", days_back=7)
        
        # Simulate incoming webhook requests
        test_webhook_data = [
            {
                'MessageSid': 'TEST_MSG_001',
                'From': 'whatsapp:+1234567890',
                'To': 'whatsapp:+14155238886',
                'Body': 'What is my best-selling drink this week?'
            },
            {
                'MessageSid': 'TEST_MSG_002',
                'From': 'whatsapp:+1234567890',
                'To': 'whatsapp:+14155238886',
                'Body': 'Show me my coffee sales'
            },
            {
                'MessageSid': 'TEST_MSG_003',
                'From': 'whatsapp:+1234567890',
                'To': 'whatsapp:+14155238886',
                'Body': 'Help'
            }
        ]
        
        print("Simulating webhook requests:")
        
        for webhook_data in test_webhook_data:
            print(f"\\nIncoming message: '{webhook_data['Body']}'")
            
            # Process message using message processor
            from src.services.message_processor import MessageProcessor
            processor = MessageProcessor()
            
            response = processor.process_message(
                webhook_data['Body'],
                webhook_data['From']
            )
            
            print(f"Generated response: {response}")

def test_api_endpoints():
    """Test WhatsApp API endpoints."""
    print("\\nTesting API Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:5001"  # Assuming Flask is running on port 5001
    
    # Test sending a message via API
    print("Testing /webhook/whatsapp/send endpoint:")
    
    send_data = {
        'to': '+1234567890',
        'message': 'This is a test message sent via API'
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/whatsapp/send",
            json=send_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        print("Note: Make sure Flask server is running on port 5001")
    
    # Test sending a sales report
    print("\\nTesting /webhook/whatsapp/send-sales-report endpoint:")
    
    report_data = {
        'to': '+1234567890',
        'merchant_id': 'TEST_MERCHANT_001',
        'report_type': 'sales_summary'
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/whatsapp/send-sales-report",
            json=report_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        print("Note: Make sure Flask server is running on port 5001")

def test_webhook_simulation():
    """Test webhook simulation endpoint."""
    print("\\nTesting Webhook Simulation...")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    webhook_tests = [
        {
            'MessageSid': 'TEST_WEBHOOK_001',
            'From': 'whatsapp:+1234567890',
            'To': 'whatsapp:+14155238886',
            'Body': 'What is my best-selling drink this week?'
        },
        {
            'MessageSid': 'TEST_WEBHOOK_002',
            'From': 'whatsapp:+1234567890',
            'To': 'whatsapp:+14155238886',
            'Body': 'Send me a sales report'
        }
    ]
    
    for test_data in webhook_tests:
        print(f"\\nTesting webhook with message: '{test_data['Body']}'")
        
        try:
            response = requests.post(
                f"{base_url}/api/test/webhook",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result.get('response', 'No response')}")
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Webhook test failed: {e}")
            print("Note: Make sure Flask server is running on port 5001")

def main():
    """Run all WhatsApp integration tests."""
    print("Starting WhatsApp Integration Tests...")
    print("=" * 60)
    
    try:
        test_whatsapp_client()
        test_message_formatting()
        test_end_to_end_flow()
        test_api_endpoints()
        test_webhook_simulation()
        
        print("\\n" + "=" * 60)
        print("✅ All WhatsApp integration tests completed!")
        print("\\nNote: Some tests require a running Flask server on port 5001")
        print("To start the server: cd coffee-shop-whatsapp-bot && source venv/bin/activate && python src/main.py")
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

