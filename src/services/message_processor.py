"""
Message processor for handling WhatsApp messages and generating responses.
"""

import logging
import re
from typing import Dict, List
from src.services.sales_processor import SalesProcessor
from src.services.llm_client import LLMClient
from src.config import Config

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Processes incoming WhatsApp messages and generates appropriate responses."""
    
    def __init__(self):
        """Initialize the message processor."""
        self.sales_processor = SalesProcessor()
        self.llm_client = LLMClient()
        
        # Common patterns for sales-related questions
        self.sales_patterns = [
            r'best.selling|top.selling|most.popular',
            r'sales|revenue|income',
            r'how.many|quantity|sold',
            r'what.*drink|beverage|coffee',
            r'this.week|today|yesterday|last.*days?'
        ]
    
    def process_message(self, message_body: str, from_number: str) -> str:
        """
        Process an incoming message and generate a response.
        
        Args:
            message_body: The text content of the message
            from_number: The sender's phone number
            
        Returns:
            Response text to send back
        """
        try:
            message_body = message_body.strip().lower()
            
            # Handle empty messages
            if not message_body:
                return "Hello! I can help you with sales information for your coffee shop. Try asking 'What's my best-selling drink this week?'"
            
            # Handle greeting messages
            if self._is_greeting(message_body):
                return "Hello! I'm your coffee shop sales assistant. I can help you with sales data and analytics. Try asking about your best-selling items!"
            
            # Handle help requests
            if self._is_help_request(message_body):
                return self._get_help_message()
            
            # Check if this is a sales-related question
            if self._is_sales_question(message_body):
                return self._handle_sales_question(message_body, from_number)
            
            # For other messages, try to use LLM to understand intent
            return self._handle_general_question(message_body, from_number)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."
    
    def _is_greeting(self, message: str) -> bool:
        """Check if the message is a greeting."""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in message for greeting in greetings)
    
    def _is_help_request(self, message: str) -> bool:
        """Check if the message is asking for help."""
        help_keywords = ['help', 'what can you do', 'commands', 'options']
        return any(keyword in message for keyword in help_keywords)
    
    def _is_sales_question(self, message: str) -> bool:
        """Check if the message is asking about sales data."""
        return any(re.search(pattern, message, re.IGNORECASE) for pattern in self.sales_patterns)
    
    def _handle_sales_question(self, message: str, from_number: str) -> str:
        """
        Handle sales-related questions.
        
        Args:
            message: The message text
            from_number: Sender's phone number
            
        Returns:
            Response with sales information
        """
        try:
            # Extract merchant ID from phone number or use default
            merchant_id = self._get_merchant_id(from_number)
            
            # Check if cache is fresh, if not, refresh it
            if not self.sales_processor.is_cache_fresh(merchant_id):
                logger.info(f"Cache is stale for merchant {merchant_id}, refreshing...")
                self.sales_processor.process_and_cache_sales_data(merchant_id)
            
            # Get sales data
            sales_data = self._get_relevant_sales_data(message, merchant_id)
            
            # Use LLM to generate a natural response
            return self._generate_llm_response(message, sales_data)
            
        except Exception as e:
            logger.error(f"Error handling sales question: {e}")
            return "I'm having trouble accessing your sales data right now. Please try again later."
    
    def _handle_general_question(self, message: str, from_number: str) -> str:
        """
        Handle general questions using LLM.
        
        Args:
            message: The message text
            from_number: Sender's phone number
            
        Returns:
            Response text
        """
        try:
            # For general questions, provide a helpful response
            context = "You are a helpful assistant for a coffee shop owner. You can help with sales data and general business questions."
            return self.llm_client.generate_response(message, context)
            
        except Exception as e:
            logger.error(f"Error handling general question: {e}")
            return "I'm not sure how to help with that. Try asking about your sales data, like 'What's my best-selling drink this week?'"
    
    def _get_merchant_id(self, from_number: str) -> str:
        """
        Get merchant ID from phone number.
        In a real implementation, this would look up the merchant ID from a database.
        For now, we'll use a default test merchant ID.
        """
        # TODO: Implement proper merchant lookup
        return "TEST_MERCHANT_001"
    
    def _get_relevant_sales_data(self, message: str, merchant_id: str) -> Dict:
        """
        Get relevant sales data based on the message content.
        
        Args:
            message: The message text
            merchant_id: Merchant ID
            
        Returns:
            Dictionary with relevant sales data
        """
        # Determine what type of data to fetch based on the message
        limit = 10
        category = None
        
        # Check for category-specific requests
        if 'coffee' in message or 'drink' in message or 'beverage' in message:
            category = 'Coffee'
            limit = 5
        elif 'food' in message or 'pastry' in message:
            category = 'Pastry'
            limit = 5
        
        # Get best-selling items
        best_selling = self.sales_processor.get_best_selling_items(
            merchant_id, limit=limit, category=category
        )
        
        return {
            'best_selling_items': best_selling,
            'category_filter': category,
            'total_items': len(best_selling)
        }
    
    def _generate_llm_response(self, question: str, sales_data: Dict) -> str:
        """
        Generate a natural language response using LLM.
        
        Args:
            question: The original question
            sales_data: Sales data to include in the response
            
        Returns:
            Natural language response
        """
        try:
            # Prepare context with sales data
            context = self._prepare_sales_context(sales_data)
            
            # Generate response using enhanced LLM client
            response = self.llm_client.generate_response(question, context, sales_data)
            
            # If LLM fails, fall back to a simple response
            if not response or len(response.strip()) < 10:
                return self._generate_simple_response(sales_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._generate_simple_response(sales_data)
    
    def _prepare_sales_context(self, sales_data: Dict) -> str:
        """Prepare sales data context for LLM."""
        context = "You are a helpful assistant for a coffee shop owner. Here is the current sales data:\\n\\n"
        
        best_selling = sales_data.get('best_selling_items', [])
        if best_selling:
            context += "Best-selling items:\\n"
            for i, item in enumerate(best_selling[:5], 1):
                context += f"{i}. {item['item_name']}: {item['quantity_sold']} sold, ${item['total_revenue']:.2f} revenue\\n"
        
        context += "\\nPlease provide a helpful and friendly response to the user's question about their sales data."
        return context
    
    def _generate_simple_response(self, sales_data: Dict) -> str:
        """Generate a simple response without LLM."""
        best_selling = sales_data.get('best_selling_items', [])
        
        if not best_selling:
            return "I don't have any sales data available right now. Please check back later."
        
        top_item = best_selling[0]
        response = f"Your best-selling item is {top_item['item_name']} with {top_item['quantity_sold']} sold"
        
        if len(best_selling) > 1:
            response += f", followed by {best_selling[1]['item_name']} with {best_selling[1]['quantity_sold']} sold"
        
        response += "."
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message with available commands."""
        return """I can help you with your coffee shop sales data! Here are some things you can ask:

• "What's my best-selling drink this week?"
• "How many cappuccinos did I sell?"
• "What are my top 5 items?"
• "Show me coffee sales"
• "What's my revenue today?"

Just ask me any question about your sales and I'll help you find the answer!"""

