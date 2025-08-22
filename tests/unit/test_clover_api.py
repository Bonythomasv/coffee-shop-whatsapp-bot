#!/usr/bin/env python3
"""
Unit tests for Clover API client.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.services.clover_api import CloverAPIClient


class TestCloverAPIClient(unittest.TestCase):
    """Test cases for CloverAPIClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = CloverAPIClient()

    @patch('src.services.clover_api.requests.get')
    def test_get_orders_success(self, mock_get):
        """Test successful order retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'elements': [
                {'id': 'ORDER_1', 'total': 500, 'lineItems': {'elements': []}}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        orders = self.client.get_orders()
        
        self.assertIsInstance(orders, list)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]['id'], 'ORDER_1')

    @patch('src.services.clover_api.requests.get')
    def test_get_inventory_items_success(self, mock_get):
        """Test successful inventory retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'elements': [
                {'id': 'ITEM_1', 'name': 'Cappuccino', 'price': 500}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        items = self.client.get_inventory_items()
        
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Cappuccino')

    def test_validate_phone_number(self):
        """Test phone number validation."""
        valid_numbers = ['+1234567890', 'whatsapp:+1234567890']
        invalid_numbers = ['1234567890', '+123', 'invalid']

        for number in valid_numbers:
            self.assertTrue(self.client.validate_phone_number(number))

        for number in invalid_numbers:
            self.assertFalse(self.client.validate_phone_number(number))


if __name__ == '__main__':
    unittest.main()
