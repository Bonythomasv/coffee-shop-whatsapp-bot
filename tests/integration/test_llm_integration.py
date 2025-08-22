#!/usr/bin/env python3
"""
Test script for LLM integration and enhanced message processing.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.main import app
from src.services.llm_client import LLMClient
from src.services.message_processor import MessageProcessor
from src.services.sales_processor import SalesProcessor

def test_llm_client():
    """Test LLM client functionality."""
    print("Testing LLM Client...")
    print("=" * 50)
    
    llm_client = LLMClient()
    
    # Test basic response generation
    test_questions = [
        "What's my best-selling drink this week?",
        "How is my coffee sales performance?",
        "Show me revenue analysis",
        "What are my top 5 items?"
    ]
    
    # Mock sales data
    mock_sales_data = {
        'best_selling_items': [
            {'item_name': 'Cappuccino', 'quantity_sold': 150, 'total_revenue': 750.0, 'category': 'Coffee'},
            {'item_name': 'Latte', 'quantity_sold': 120, 'total_revenue': 660.0, 'category': 'Coffee'},
            {'item_name': 'Espresso', 'quantity_sold': 80, 'total_revenue': 320.0, 'category': 'Coffee'},
            {'item_name': 'Croissant', 'quantity_sold': 45, 'total_revenue': 135.0, 'category': 'Pastry'}
        ],
        'category_filter': None,
        'total_items': 4
    }
    
    for question in test_questions:
        print(f"\\nQuestion: {question}")
        response = llm_client.generate_response(question, "", mock_sales_data)
        print(f"Response: {response}")
        print("-" * 30)

def test_enhanced_message_processor():
    """Test enhanced message processor with LLM integration."""
    print("\\nTesting Enhanced Message Processor...")
    print("=" * 50)
    
    with app.app_context():
        # Refresh sales data first
        sales_processor = SalesProcessor()
        sales_processor.process_and_cache_sales_data("TEST_MERCHANT_001", days_back=7)
        
        # Test message processor
        processor = MessageProcessor()
        
        test_messages = [
            "What's my best-selling drink this week?",
            "How many cappuccinos did I sell?",
            "Show me my coffee sales performance",
            "What's my total revenue?",
            "Give me a sales analysis",
            "How are my pastries doing?",
            "What should I focus on to improve sales?"
        ]
        
        for message in test_messages:
            print(f"\\nMessage: {message}")
            response = processor.process_message(message, "whatsapp:+1234567890")
            print(f"Response: {response}")
            print("-" * 40)

def test_sales_trend_analysis():
    """Test sales trend analysis functionality."""
    print("\\nTesting Sales Trend Analysis...")
    print("=" * 50)
    
    with app.app_context():
        llm_client = LLMClient()
        sales_processor = SalesProcessor()
        
        # Get sales data
        best_selling = sales_processor.get_best_selling_items("TEST_MERCHANT_001", limit=10)
        
        if best_selling:
            trend_questions = [
                "What trends do you see in my sales data?",
                "Which category is performing best?",
                "What recommendations do you have for improving sales?",
                "How does my coffee vs pastry sales compare?"
            ]
            
            for question in trend_questions:
                print(f"\\nTrend Question: {question}")
                analysis = llm_client.analyze_sales_trends(best_selling, question)
                print(f"Analysis: {analysis}")
                print("-" * 40)
        else:
            print("No sales data available for trend analysis")

def test_different_scenarios():
    """Test different conversation scenarios."""
    print("\\nTesting Different Conversation Scenarios...")
    print("=" * 50)
    
    with app.app_context():
        processor = MessageProcessor()
        
        scenarios = [
            # Greeting scenario
            ("Hello", "Greeting"),
            
            # Help scenario
            ("Help me understand what you can do", "Help Request"),
            
            # Specific product inquiry
            ("How many lattes did I sell yesterday?", "Product Inquiry"),
            
            # Revenue question
            ("What's my total revenue this week?", "Revenue Question"),
            
            # Comparison question
            ("Which sells better, cappuccino or latte?", "Comparison"),
            
            # Business advice
            ("What should I promote more?", "Business Advice"),
            
            # Category-specific
            ("Show me all my coffee sales", "Category Filter"),
            
            # Time-based
            ("How did I do today compared to yesterday?", "Time Comparison")
        ]
        
        for message, scenario_type in scenarios:
            print(f"\\nScenario: {scenario_type}")
            print(f"Message: {message}")
            response = processor.process_message(message, "whatsapp:+1234567890")
            print(f"Response: {response}")
            print("-" * 40)

def main():
    """Run all LLM integration tests."""
    print("Starting LLM Integration Tests...")
    print("=" * 60)
    
    try:
        test_llm_client()
        test_enhanced_message_processor()
        test_sales_trend_analysis()
        test_different_scenarios()
        
        print("\\n" + "=" * 60)
        print("✅ All LLM integration tests completed successfully!")
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

