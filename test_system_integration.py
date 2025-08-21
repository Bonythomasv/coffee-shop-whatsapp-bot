#!/usr/bin/env python3
"""
Comprehensive system integration test for the Coffee Shop WhatsApp Bot.
This test validates the entire system flow from WhatsApp message to response.
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.services.clover_api import CloverAPIClient
from src.services.sales_processor import SalesProcessor
from src.services.message_processor import MessageProcessor
from src.services.whatsapp_client import WhatsAppClient
from src.services.llm_client import LLMClient
from src.models.sales_cache import SalesCache, WhatsAppMessage
from src.models.user import db

class SystemIntegrationTest:
    """Comprehensive system integration test suite."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.test_results = []
        self.merchant_id = "TEST_MERCHANT_001"
        self.test_phone = "whatsapp:+1234567890"
        
    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting Comprehensive System Integration Tests")
        print("=" * 60)
        
        with app.app_context():
            # Test individual components
            self.test_database_connectivity()
            self.test_clover_api_integration()
            self.test_sales_data_processing()
            self.test_llm_integration()
            self.test_whatsapp_client()
            self.test_message_processing_pipeline()
            self.test_end_to_end_flow()
            self.test_error_handling()
            self.test_performance()
            
        # Generate test report
        self.generate_test_report()
    
    def test_database_connectivity(self):
        """Test database connectivity and operations."""
        print("\\n📊 Testing Database Connectivity...")
        
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            
            # Test creating and querying data
            test_message = WhatsAppMessage(
                message_sid='TEST_INTEGRATION_001',
                from_number=self.test_phone,
                to_number='whatsapp:+14155238886',
                message_body='Integration test message'
            )
            
            db.session.add(test_message)
            db.session.commit()
            
            # Query the data back
            retrieved = WhatsAppMessage.query.filter_by(
                message_sid='TEST_INTEGRATION_001'
            ).first()
            
            assert retrieved is not None
            assert retrieved.message_body == 'Integration test message'
            
            # Clean up
            db.session.delete(retrieved)
            db.session.commit()
            
            self.test_results.append(("Database Connectivity", "✅ PASS", "Database operations working correctly"))
            print("✅ Database connectivity test passed")
            
        except Exception as e:
            self.test_results.append(("Database Connectivity", "❌ FAIL", str(e)))
            print(f"❌ Database connectivity test failed: {e}")
    
    def test_clover_api_integration(self):
        """Test Clover API integration."""
        print("\\n🏪 Testing Clover API Integration...")
        
        try:
            client = CloverAPIClient()
            
            # Test fetching orders
            orders = client.get_orders()
            assert isinstance(orders, list)
            assert len(orders) > 0
            
            # Test fetching inventory
            inventory = client.get_inventory_items()
            assert isinstance(inventory, list)
            assert len(inventory) > 0
            
            # Validate order structure
            if orders:
                order = orders[0]
                required_fields = ['id', 'lineItems']
                for field in required_fields:
                    assert field in order, f"Missing field: {field}"
            
            self.test_results.append(("Clover API Integration", "✅ PASS", f"Retrieved {len(orders)} orders and {len(inventory)} items"))
            print(f"✅ Clover API test passed - {len(orders)} orders, {len(inventory)} items")
            
        except Exception as e:
            self.test_results.append(("Clover API Integration", "❌ FAIL", str(e)))
            print(f"❌ Clover API test failed: {e}")
    
    def test_sales_data_processing(self):
        """Test sales data processing and caching."""
        print("\\n📈 Testing Sales Data Processing...")
        
        try:
            processor = SalesProcessor()
            
            # Process sales data
            result = processor.process_and_cache_sales_data(self.merchant_id, days_back=7)
            
            assert result['success'] == True
            assert result['orders_processed'] > 0
            assert result['items_updated'] > 0
            
            # Test cache retrieval
            best_selling = processor.get_best_selling_items(self.merchant_id, limit=5)
            assert isinstance(best_selling, list)
            assert len(best_selling) > 0
            
            # Validate data structure
            if best_selling:
                item = best_selling[0]
                required_fields = ['item_name', 'quantity_sold', 'total_revenue']
                for field in required_fields:
                    assert field in item, f"Missing field: {field}"
            
            # Test cache freshness
            is_fresh = processor.is_cache_fresh(self.merchant_id)
            assert is_fresh == True
            
            self.test_results.append(("Sales Data Processing", "✅ PASS", f"Processed {result['orders_processed']} orders, cached {result['items_updated']} items"))
            print(f"✅ Sales processing test passed - {result['orders_processed']} orders processed")
            
        except Exception as e:
            self.test_results.append(("Sales Data Processing", "❌ FAIL", str(e)))
            print(f"❌ Sales processing test failed: {e}")
    
    def test_llm_integration(self):
        """Test LLM integration and response generation."""
        print("\\n🤖 Testing LLM Integration...")
        
        try:
            llm_client = LLMClient()
            
            # Test basic response generation
            test_questions = [
                "What's my best-selling drink?",
                "Show me sales data",
                "Help me understand my revenue"
            ]
            
            mock_sales_data = {
                'best_selling_items': [
                    {'item_name': 'Cappuccino', 'quantity_sold': 150, 'total_revenue': 750.0, 'category': 'Coffee'}
                ]
            }
            
            responses_generated = 0
            for question in test_questions:
                response = llm_client.generate_response(question, "", mock_sales_data)
                assert isinstance(response, str)
                assert len(response) > 10  # Ensure meaningful response
                responses_generated += 1
            
            # Test trend analysis
            trend_response = llm_client.analyze_sales_trends(
                mock_sales_data['best_selling_items'], 
                "What trends do you see?"
            )
            assert isinstance(trend_response, str)
            assert len(trend_response) > 20
            
            self.test_results.append(("LLM Integration", "✅ PASS", f"Generated {responses_generated} responses successfully"))
            print(f"✅ LLM integration test passed - {responses_generated} responses generated")
            
        except Exception as e:
            self.test_results.append(("LLM Integration", "❌ FAIL", str(e)))
            print(f"❌ LLM integration test failed: {e}")
    
    def test_whatsapp_client(self):
        """Test WhatsApp client functionality."""
        print("\\n📱 Testing WhatsApp Client...")
        
        try:
            client = WhatsAppClient()
            
            # Test phone number validation
            valid_numbers = ['+1234567890', 'whatsapp:+1234567890']
            invalid_numbers = ['1234567890', '+123', 'invalid']
            
            for number in valid_numbers:
                assert client.validate_phone_number(number) == True
            
            for number in invalid_numbers:
                assert client.validate_phone_number(number) == False
            
            # Test message sending (mock mode)
            result = client.send_message(self.test_phone, "Test message")
            assert result['success'] == True
            assert 'message_sid' in result
            
            # Test message formatting
            mock_data = {
                'best_selling_items': [
                    {'item_name': 'Cappuccino', 'quantity_sold': 150, 'total_revenue': 750.0, 'category': 'Coffee'}
                ]
            }
            
            formatted_msg = client.format_business_message(mock_data, 'sales_summary')
            assert isinstance(formatted_msg, str)
            assert len(formatted_msg) > 50
            assert 'Cappuccino' in formatted_msg
            
            self.test_results.append(("WhatsApp Client", "✅ PASS", "Message sending and formatting working correctly"))
            print("✅ WhatsApp client test passed")
            
        except Exception as e:
            self.test_results.append(("WhatsApp Client", "❌ FAIL", str(e)))
            print(f"❌ WhatsApp client test failed: {e}")
    
    def test_message_processing_pipeline(self):
        """Test the complete message processing pipeline."""
        print("\\n🔄 Testing Message Processing Pipeline...")
        
        try:
            processor = MessageProcessor()
            
            # Test different types of messages
            test_cases = [
                ("What's my best-selling drink this week?", "sales question"),
                ("Hello", "greeting"),
                ("Help", "help request"),
                ("Show me coffee sales", "category-specific query"),
                ("What's my revenue?", "revenue question")
            ]
            
            successful_responses = 0
            for message, message_type in test_cases:
                response = processor.process_message(message, self.test_phone)
                
                assert isinstance(response, str)
                assert len(response) > 10
                
                # Validate response content based on message type
                if message_type == "greeting":
                    assert any(word in response.lower() for word in ["hello", "hi", "assistant"])
                elif message_type == "help request":
                    assert "help" in response.lower() or "ask" in response.lower()
                
                successful_responses += 1
            
            self.test_results.append(("Message Processing Pipeline", "✅ PASS", f"Processed {successful_responses}/{len(test_cases)} message types successfully"))
            print(f"✅ Message processing test passed - {successful_responses}/{len(test_cases)} cases")
            
        except Exception as e:
            self.test_results.append(("Message Processing Pipeline", "❌ FAIL", str(e)))
            print(f"❌ Message processing test failed: {e}")
    
    def test_end_to_end_flow(self):
        """Test the complete end-to-end flow."""
        print("\\n🔗 Testing End-to-End Flow...")
        
        try:
            # Simulate the complete flow:
            # 1. Refresh sales data
            # 2. Process incoming message
            # 3. Generate response
            # 4. Format for WhatsApp
            
            # Step 1: Refresh sales data
            sales_processor = SalesProcessor()
            sales_result = sales_processor.process_and_cache_sales_data(self.merchant_id)
            assert sales_result['success'] == True
            
            # Step 2: Process incoming message
            message_processor = MessageProcessor()
            user_message = "What's my best-selling drink this week?"
            response = message_processor.process_message(user_message, self.test_phone)
            
            # Step 3: Validate response
            assert isinstance(response, str)
            assert len(response) > 20
            
            # Step 4: Test WhatsApp formatting
            whatsapp_client = WhatsAppClient()
            send_result = whatsapp_client.send_message(self.test_phone, response)
            assert send_result['success'] == True
            
            # Step 5: Store message in database
            message_record = WhatsAppMessage(
                message_sid='E2E_TEST_001',
                from_number=self.test_phone,
                to_number='whatsapp:+14155238886',
                message_body=user_message,
                response_body=response,
                processed=True
            )
            
            db.session.add(message_record)
            db.session.commit()
            
            # Verify storage
            stored_message = WhatsAppMessage.query.filter_by(message_sid='E2E_TEST_001').first()
            assert stored_message is not None
            assert stored_message.processed == True
            
            # Clean up
            db.session.delete(stored_message)
            db.session.commit()
            
            self.test_results.append(("End-to-End Flow", "✅ PASS", "Complete flow from message to response working correctly"))
            print("✅ End-to-end flow test passed")
            
        except Exception as e:
            self.test_results.append(("End-to-End Flow", "❌ FAIL", str(e)))
            print(f"❌ End-to-end flow test failed: {e}")
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        print("\\n⚠️ Testing Error Handling...")
        
        try:
            # Test invalid merchant ID
            sales_processor = SalesProcessor()
            best_selling = sales_processor.get_best_selling_items("INVALID_MERCHANT", limit=5)
            assert isinstance(best_selling, list)  # Should return empty list, not crash
            
            # Test invalid phone number
            whatsapp_client = WhatsAppClient()
            is_valid = whatsapp_client.validate_phone_number("invalid_number")
            assert is_valid == False
            
            # Test empty message processing
            message_processor = MessageProcessor()
            response = message_processor.process_message("", self.test_phone)
            assert isinstance(response, str)
            assert len(response) > 0
            
            # Test LLM with empty data
            llm_client = LLMClient()
            response = llm_client.generate_response("Test question", "", None)
            assert isinstance(response, str)
            
            self.test_results.append(("Error Handling", "✅ PASS", "System handles error scenarios gracefully"))
            print("✅ Error handling test passed")
            
        except Exception as e:
            self.test_results.append(("Error Handling", "❌ FAIL", str(e)))
            print(f"❌ Error handling test failed: {e}")
    
    def test_performance(self):
        """Test system performance."""
        print("\\n⚡ Testing Performance...")
        
        try:
            # Test message processing speed
            message_processor = MessageProcessor()
            
            start_time = time.time()
            for i in range(5):
                response = message_processor.process_message(
                    f"Test message {i}", 
                    self.test_phone
                )
            end_time = time.time()
            
            avg_response_time = (end_time - start_time) / 5
            
            # Test sales data processing speed
            sales_processor = SalesProcessor()
            start_time = time.time()
            result = sales_processor.process_and_cache_sales_data(self.merchant_id)
            processing_time = time.time() - start_time
            
            # Performance assertions
            assert avg_response_time < 5.0  # Should respond within 5 seconds
            assert processing_time < 30.0   # Should process data within 30 seconds
            
            self.test_results.append(("Performance", "✅ PASS", f"Avg response: {avg_response_time:.2f}s, Processing: {processing_time:.2f}s"))
            print(f"✅ Performance test passed - Response: {avg_response_time:.2f}s, Processing: {processing_time:.2f}s")
            
        except Exception as e:
            self.test_results.append(("Performance", "❌ FAIL", str(e)))
            print(f"❌ Performance test failed: {e}")
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        print("\\n📋 Generating Test Report...")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, status, _ in self.test_results if "✅" in status)
        failed_tests = total_tests - passed_tests
        
        print(f"\\n📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\\n📝 DETAILED RESULTS")
        print("-" * 60)
        
        for test_name, status, details in self.test_results:
            print(f"{status} {test_name}")
            print(f"   {details}")
        
        # Save report to file
        report_content = f"""# System Integration Test Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}
- Success Rate: {(passed_tests/total_tests)*100:.1f}%

## Detailed Results
"""
        
        for test_name, status, details in self.test_results:
            report_content += f"\\n### {test_name}\\n"
            report_content += f"Status: {status}\\n"
            report_content += f"Details: {details}\\n"
        
        with open('/home/ubuntu/coffee-shop-whatsapp-bot/integration_test_report.md', 'w') as f:
            f.write(report_content)
        
        print(f"\\n💾 Test report saved to: integration_test_report.md")
        
        if failed_tests == 0:
            print("\\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        else:
            print(f"\\n⚠️ {failed_tests} test(s) failed. Please review and fix issues before deployment.")

def main():
    """Run the comprehensive system integration test."""
    test_suite = SystemIntegrationTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()

