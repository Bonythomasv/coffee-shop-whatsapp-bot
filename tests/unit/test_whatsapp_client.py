#!/usr/bin/env python3
"""
Unit tests for WhatsApp client.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.services.whatsapp_client import WhatsAppClient


class TestWhatsAppClient(unittest.TestCase):
    """Test cases for WhatsAppClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = WhatsAppClient()

    def test_validate_phone_number_valid(self):
        """Test phone number validation with valid numbers."""
        valid_numbers = [
            '+1234567890',
            'whatsapp:+1234567890',
            '+44123456789',
            'whatsapp:+44123456789'
        ]
        
        for number in valid_numbers:
            with self.subTest(number=number):
                self.assertTrue(self.client.validate_phone_number(number))

    def test_validate_phone_number_invalid(self):
        """Test phone number validation with invalid numbers."""
        invalid_numbers = [
            '1234567890',  # Missing +
            '+123',        # Too short
            '+123456789012345678',  # Too long
            'invalid',     # Not a number
            '',            # Empty
            None           # None
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                self.assertFalse(self.client.validate_phone_number(number))

    @patch('src.services.whatsapp_client.client')
    def test_send_message_success(self, mock_twilio_client):
        """Test successful message sending."""
        mock_message = Mock()
        mock_message.sid = 'TEST_SID_123'
        mock_twilio_client.messages.create.return_value = mock_message

        result = self.client.send_message('+1234567890', 'Test message')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message_sid'], 'TEST_SID_123')

    def test_format_business_message_sales_summary(self):
        """Test formatting sales summary message."""
        mock_data = {
            'best_selling_items': [
                {'item_name': 'Cappuccino', 'quantity_sold': 150, 'total_revenue': 750.0, 'category': 'Coffee'},
                {'item_name': 'Latte', 'quantity_sold': 120, 'total_revenue': 660.0, 'category': 'Coffee'}
            ]
        }
        
        formatted_msg = self.client.format_business_message(mock_data, 'sales_summary')
        
        self.assertIsInstance(formatted_msg, str)
        self.assertIn('Cappuccino', formatted_msg)
        self.assertIn('150', formatted_msg)
        self.assertIn('750.00', formatted_msg)


if __name__ == '__main__':
    unittest.main()
