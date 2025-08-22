#!/usr/bin/env python3
"""
Unit tests for Sales Processor.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.services.sales_processor import SalesProcessor


class TestSalesProcessor(unittest.TestCase):
    """Test cases for SalesProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = SalesProcessor()

    @patch('src.services.sales_processor.CloverAPIClient')
    def test_process_and_cache_sales_data(self, mock_clover_client):
        """Test sales data processing and caching."""
        mock_client = Mock()
        mock_client.get_orders.return_value = [
            {
                'id': 'ORDER_1',
                'total': 500,
                'lineItems': {
                    'elements': [
                        {'item': {'id': 'ITEM_1', 'name': 'Cappuccino'}, 'unitQty': 2}
                    ]
                }
            }
        ]
        mock_clover_client.return_value = mock_client

        result = self.processor.process_and_cache_sales_data('TEST_MERCHANT')
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('orders_processed', result)

    def test_get_best_selling_items_empty(self):
        """Test getting best selling items with empty data."""
        items = self.processor.get_best_selling_items('INVALID_MERCHANT')
        
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    def test_is_cache_fresh_no_data(self):
        """Test cache freshness check with no data."""
        is_fresh = self.processor.is_cache_fresh('INVALID_MERCHANT')
        
        self.assertFalse(is_fresh)


if __name__ == '__main__':
    unittest.main()
