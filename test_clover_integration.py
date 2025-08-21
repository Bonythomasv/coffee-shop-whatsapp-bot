#!/usr/bin/env python3
"""
Test script for Clover API integration and sales processing.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app, db
from src.services.clover_api import CloverAPIClient
from src.services.sales_processor import SalesProcessor
from src.models.sales_cache import SalesCache

def test_clover_api():
    """Test Clover API client."""
    print("Testing Clover API client...")
    
    client = CloverAPIClient()
    
    # Test fetching orders
    orders = client.get_orders()
    print(f"Fetched {len(orders)} orders")
    
    if orders:
        print("Sample order:")
        print(f"- Order ID: {orders[0]['id']}")
        print(f"- Total: ${orders[0]['total'] / 100:.2f}")
        print(f"- Line items: {len(orders[0]['lineItems']['elements'])}")
    
    # Test fetching inventory
    inventory = client.get_inventory_items()
    print(f"\nFetched {len(inventory)} inventory items")
    
    if inventory:
        print("Sample inventory item:")
        print(f"- Item ID: {inventory[0]['id']}")
        print(f"- Name: {inventory[0]['name']}")
        print(f"- Price: ${inventory[0]['price'] / 100:.2f}")

def test_sales_processor():
    """Test sales processor."""
    print("\nTesting sales processor...")
    
    with app.app_context():
        processor = SalesProcessor()
        
        # Process sales data for test merchant
        result = processor.process_and_cache_sales_data("TEST_MERCHANT_001", days_back=7)
        
        print(f"Processing result: {result}")
        
        if result['success']:
            print(f"- Orders processed: {result['orders_processed']}")
            print(f"- Items updated: {result['items_updated']}")
            
            # Test getting best-selling items
            best_selling = processor.get_best_selling_items("TEST_MERCHANT_001", limit=5)
            print(f"\nTop 5 best-selling items:")
            for i, item in enumerate(best_selling, 1):
                print(f"{i}. {item['item_name']}: {item['quantity_sold']} sold, ${item['total_revenue']:.2f} revenue")
            
            # Test cache freshness
            is_fresh = processor.is_cache_fresh("TEST_MERCHANT_001")
            print(f"\nCache is fresh: {is_fresh}")

def test_database_queries():
    """Test database queries."""
    print("\nTesting database queries...")
    
    with app.app_context():
        # Get all sales cache entries
        all_sales = SalesCache.query.all()
        print(f"Total sales cache entries: {len(all_sales)}")
        
        # Get best-selling item
        best_item = SalesCache.query.order_by(SalesCache.quantity_sold.desc()).first()
        if best_item:
            print(f"Best-selling item: {best_item.item_name} ({best_item.quantity_sold} sold)")
        
        # Get sales by category
        coffee_sales = SalesCache.query.filter_by(category='Coffee').all()
        print(f"Coffee items in cache: {len(coffee_sales)}")

if __name__ == "__main__":
    test_clover_api()
    test_sales_processor()
    test_database_queries()

