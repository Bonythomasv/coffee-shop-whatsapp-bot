#!/usr/bin/env python3
"""
Unit tests for Message Processor.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.services.message_processor import MessageProcessor


class TestMessageProcessor(unittest.TestCase):
    """Test cases for MessageProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = MessageProcessor()

    @patch('src.services.message_processor.SalesProcessor')
    @patch('src.services.message_processor.LLMClient')
    def test_process_message_greeting(self, mock_llm, mock_sales):
        """Test processing greeting message."""
        mock_llm_instance = Mock()
        mock_llm_instance.generate_response.return_value = "Hello! I'm your assistant."
        mock_llm.return_value = mock_llm_instance

        response = self.processor.process_message("Hello", "whatsapp:+1234567890")
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 5)

    @patch('src.services.message_processor.SalesProcessor')
    @patch('src.services.message_processor.LLMClient')
    def test_process_message_sales_query(self, mock_llm, mock_sales):
        """Test processing sales query message."""
        mock_sales_instance = Mock()
        mock_sales_instance.get_best_selling_items.return_value = [
            {'item_name': 'Cappuccino', 'quantity_sold': 150}
        ]
        mock_sales.return_value = mock_sales_instance

        mock_llm_instance = Mock()
        mock_llm_instance.generate_response.return_value = "Your best-selling item is Cappuccino."
        mock_llm.return_value = mock_llm_instance

        response = self.processor.process_message("What's my best-selling drink?", "whatsapp:+1234567890")
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 10)

    def test_process_message_empty(self):
        """Test processing empty message."""
        response = self.processor.process_message("", "whatsapp:+1234567890")
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)


if __name__ == '__main__':
    unittest.main()
