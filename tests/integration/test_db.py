#!/usr/bin/env python3
"""
Test script for database operations
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.main import app, db
from src.models.sales_cache import SalesCache, WhatsAppMessage

def test_database_operations():
    """Test basic database operations."""
    with app.app_context():
        # Test reading sales data
        sales = SalesCache.query.all()
        print(f'Found {len(sales)} sales records:')
        for sale in sales:
            print(f'- {sale.item_name}: {sale.quantity_sold} sold, ${sale.total_revenue} revenue')
        
        # Test finding best-selling item
        best_selling = SalesCache.query.order_by(SalesCache.quantity_sold.desc()).first()
        if best_selling:
            print(f'\nBest-selling item: {best_selling.item_name} ({best_selling.quantity_sold} sold)')
        
        # Test WhatsApp messages table
        messages = WhatsAppMessage.query.all()
        print(f'\nFound {len(messages)} WhatsApp messages')

if __name__ == "__main__":
    test_database_operations()

