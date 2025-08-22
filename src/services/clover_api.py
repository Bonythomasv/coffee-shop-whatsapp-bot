"""
Clover API client for fetching sales data and orders.
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class CloverAPIClient:
    """Client for interacting with the Clover API."""
    
    def __init__(self, access_token: str = None, merchant_id: str = None, base_url: str = None):
        """
        Initialize the Clover API client.
        
        Args:
            access_token: Clover API access token
            merchant_id: Clover merchant ID
            base_url: Clover API base URL (defaults to sandbox)
        """
        self.access_token = access_token or Config.CLOVER_ACCESS_TOKEN
        self.merchant_id = merchant_id or Config.CLOVER_MERCHANT_ID
        self.base_url = base_url or Config.CLOVER_API_BASE_URL
        
        if not self.access_token or not self.merchant_id:
            logger.warning("Clover API credentials not configured. Using mock data.")
            self.use_mock_data = True
        else:
            self.use_mock_data = False
        
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
    
    def get_orders(self, start_date: datetime = None, end_date: datetime = None, limit: int = 1000) -> List[Dict]:
        """
        Fetch orders from Clover API.
        
        Args:
            start_date: Start date for order filtering
            end_date: End date for order filtering
            limit: Maximum number of orders to fetch
            
        Returns:
            List of order dictionaries
        """
        if self.use_mock_data:
            return self._get_mock_orders(start_date, end_date)
        
        try:
            url = f"{self.base_url}/merchants/{self.merchant_id}/orders"
            params = {
                'limit': limit,
                'expand': 'lineItems'
            }
            
            # Add date filtering for orders
            if start_date and end_date:
                start_ms = int(start_date.timestamp() * 1000)
                end_ms = int(end_date.timestamp() * 1000)
                params['filter'] = f'createdTime>={start_ms} AND createdTime<={end_ms}'
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('elements', [])
            
        except requests.RequestException as e:
            logger.error(f"Error fetching orders from Clover API: {e}")
            # Fall back to mock data on error
            return self._get_mock_orders(start_date, end_date)
    
    def get_inventory_items(self) -> List[Dict]:
        """
        Fetch inventory items from Clover API.
        
        Returns:
            List of inventory item dictionaries
        """
        if self.use_mock_data:
            return self._get_mock_inventory()
        
        try:
            url = f"{self.base_url}/merchants/{self.merchant_id}/items"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get('elements', [])
            
        except requests.RequestException as e:
            logger.error(f"Error fetching inventory from Clover API: {e}")
            # Fall back to mock data on error
            return self._get_mock_inventory()
    
    def _get_mock_orders(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Generate mock order data for testing."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Mock orders with line items
        mock_orders = []
        
        # Generate orders for the past week
        current_date = start_date
        order_id = 1000
        
        while current_date <= end_date:
            # Generate 10-20 orders per day
            for i in range(10, 21):
                order_time = current_date + timedelta(hours=8 + (i % 12), minutes=(i * 17) % 60)
                
                if order_time > end_date:
                    break
                
                order = {
                    'id': f'ORDER_{order_id}',
                    'createdTime': int(order_time.timestamp() * 1000),
                    'total': 0,
                    'lineItems': {
                        'elements': []
                    }
                }
                
                # Add 1-3 line items per order
                import random
                num_items = random.randint(1, 3)
                
                for j in range(num_items):
                    item_choice = random.choice([
                        {'id': 'ITEM_001', 'name': 'Cappuccino', 'price': 500},
                        {'id': 'ITEM_002', 'name': 'Latte', 'price': 550},
                        {'id': 'ITEM_003', 'name': 'Espresso', 'price': 400},
                        {'id': 'ITEM_004', 'name': 'Croissant', 'price': 300},
                        {'id': 'ITEM_005', 'name': 'Muffin', 'price': 350},
                    ])
                    
                    line_item = {
                        'id': f'LINE_{order_id}_{j}',
                        'item': item_choice,
                        'unitQty': 1,
                        'price': item_choice['price']
                    }
                    
                    order['lineItems']['elements'].append(line_item)
                    order['total'] += item_choice['price']
                
                mock_orders.append(order)
                order_id += 1
            
            current_date += timedelta(days=1)
        
        return mock_orders
    
    def _get_mock_inventory(self) -> List[Dict]:
        """Generate mock inventory data for testing."""
        return [
            {
                'id': 'ITEM_001',
                'name': 'Cappuccino',
                'price': 500,
                'categories': {'elements': [{'name': 'Coffee'}]}
            },
            {
                'id': 'ITEM_002',
                'name': 'Latte',
                'price': 550,
                'categories': {'elements': [{'name': 'Coffee'}]}
            },
            {
                'id': 'ITEM_003',
                'name': 'Espresso',
                'price': 400,
                'categories': {'elements': [{'name': 'Coffee'}]}
            },
            {
                'id': 'ITEM_004',
                'name': 'Croissant',
                'price': 300,
                'categories': {'elements': [{'name': 'Pastry'}]}
            },
            {
                'id': 'ITEM_005',
                'name': 'Muffin',
                'price': 350,
                'categories': {'elements': [{'name': 'Pastry'}]}
            }
        ]

