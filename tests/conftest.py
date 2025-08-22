#!/usr/bin/env python3
"""
Pytest configuration file for Coffee Shop WhatsApp Bot tests.
"""

import pytest
import os
import sys
from unittest.mock import Mock

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.main import app, db


@pytest.fixture(scope='session')
def flask_app():
    """Create and configure a test Flask application."""
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(flask_app):
    """Create a test client for the Flask application."""
    return flask_app.test_client()


@pytest.fixture(scope='function')
def app_context(flask_app):
    """Create an application context for tests."""
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def mock_clover_client():
    """Mock Clover API client for testing."""
    mock_client = Mock()
    mock_client.get_orders.return_value = [
        {
            'id': 'ORDER_TEST_001',
            'total': 500,
            'lineItems': {
                'elements': [
                    {
                        'item': {'id': 'ITEM_001', 'name': 'Cappuccino'},
                        'unitQty': 2,
                        'price': 500
                    }
                ]
            }
        }
    ]
    mock_client.get_inventory_items.return_value = [
        {
            'id': 'ITEM_001',
            'name': 'Cappuccino',
            'price': 500,
            'categories': {'elements': [{'name': 'Coffee'}]}
        }
    ]
    return mock_client


@pytest.fixture
def mock_whatsapp_client():
    """Mock WhatsApp client for testing."""
    mock_client = Mock()
    mock_client.send_message.return_value = {
        'success': True,
        'message_sid': 'TEST_SID_123'
    }
    mock_client.validate_phone_number.return_value = True
    return mock_client


@pytest.fixture
def sample_sales_data():
    """Sample sales data for testing."""
    return {
        'best_selling_items': [
            {
                'item_name': 'Cappuccino',
                'quantity_sold': 150,
                'total_revenue': 750.0,
                'category': 'Coffee'
            },
            {
                'item_name': 'Latte',
                'quantity_sold': 120,
                'total_revenue': 660.0,
                'category': 'Coffee'
            }
        ]
    }
