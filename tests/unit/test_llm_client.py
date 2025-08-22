#!/usr/bin/env python3
"""
Unit tests for LLM Client.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.services.llm_client import LLMClient


class TestLLMClient(unittest.TestCase):
    """Test cases for LLMClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = LLMClient()

    def test_generate_response_fallback(self):
        """Test response generation with fallback mode."""
        response = self.client.generate_response(
            "What's my best-selling drink?", 
            "", 
            {'best_selling_items': []}
        )
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 10)

    def test_analyze_sales_trends_fallback(self):
        """Test sales trend analysis with fallback mode."""
        mock_items = [
            {'item_name': 'Cappuccino', 'quantity_sold': 150, 'total_revenue': 750.0}
        ]
        
        response = self.client.analyze_sales_trends(mock_items, "What trends do you see?")
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 20)

    @patch('src.services.llm_client.openai')
    def test_generate_response_with_openai(self, mock_openai):
        """Test response generation with OpenAI."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Your best-selling drink is Cappuccino."
        mock_openai.ChatCompletion.create.return_value = mock_response

        response = self.client.generate_response(
            "What's my best-selling drink?", 
            "", 
            {'best_selling_items': [{'item_name': 'Cappuccino', 'quantity_sold': 150}]}
        )
        
        self.assertIsInstance(response, str)


if __name__ == '__main__':
    unittest.main()
