#!/usr/bin/env python3
"""
Database initialization script for the Coffee Shop WhatsApp Bot.
This script creates all necessary tables and can be used to reset the database.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app, db
from src.models.user import User
from src.models.sales_cache import SalesCache, WhatsAppMessage

def init_database():
    """Initialize the database with all tables."""
    with app.app_context():
        # Drop all tables (use with caution in production)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database initialized successfully!")
        print("Created tables:")
        print("- users")
        print("- sales_cache")
        print("- whatsapp_messages")

def add_sample_data():
    """Add sample data for testing purposes."""
    with app.app_context():
        from datetime import datetime, timedelta
        
        # Add sample sales cache data
        sample_sales = [
            SalesCache(
                merchant_id="TEST_MERCHANT_001",
                item_id="ITEM_001",
                item_name="Cappuccino",
                category="Coffee",
                quantity_sold=150,
                total_revenue=750.0,
                period_start=datetime.utcnow() - timedelta(days=7),
                period_end=datetime.utcnow()
            ),
            SalesCache(
                merchant_id="TEST_MERCHANT_001",
                item_id="ITEM_002",
                item_name="Latte",
                category="Coffee",
                quantity_sold=120,
                total_revenue=660.0,
                period_start=datetime.utcnow() - timedelta(days=7),
                period_end=datetime.utcnow()
            ),
            SalesCache(
                merchant_id="TEST_MERCHANT_001",
                item_id="ITEM_003",
                item_name="Espresso",
                category="Coffee",
                quantity_sold=80,
                total_revenue=320.0,
                period_start=datetime.utcnow() - timedelta(days=7),
                period_end=datetime.utcnow()
            ),
            SalesCache(
                merchant_id="TEST_MERCHANT_001",
                item_id="ITEM_004",
                item_name="Croissant",
                category="Pastry",
                quantity_sold=45,
                total_revenue=135.0,
                period_start=datetime.utcnow() - timedelta(days=7),
                period_end=datetime.utcnow()
            )
        ]
        
        for sale in sample_sales:
            db.session.add(sale)
        
        db.session.commit()
        print("Sample data added successfully!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument("--sample-data", action="store_true", 
                       help="Add sample data for testing")
    
    args = parser.parse_args()
    
    init_database()
    
    if args.sample_data:
        add_sample_data()

