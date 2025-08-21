"""
Sales data processor for analyzing Clover orders and updating cache.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
from src.models.sales_cache import SalesCache
from src.models.user import db
from src.services.clover_api import CloverAPIClient
from src.config import Config

logger = logging.getLogger(__name__)

class SalesProcessor:
    """Processes sales data from Clover API and updates the cache."""
    
    def __init__(self, clover_client: CloverAPIClient = None):
        """
        Initialize the sales processor.
        
        Args:
            clover_client: Clover API client instance
        """
        self.clover_client = clover_client or CloverAPIClient()
    
    def process_and_cache_sales_data(self, merchant_id: str, days_back: int = 7) -> Dict:
        """
        Process sales data from Clover API and update the cache.
        
        Args:
            merchant_id: Merchant ID to process data for
            days_back: Number of days back to fetch data
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            logger.info(f"Processing sales data for merchant {merchant_id} from {start_date} to {end_date}")
            
            # Fetch orders from Clover API
            orders = self.clover_client.get_orders(start_date=start_date, end_date=end_date)
            
            # Fetch inventory items for item details
            inventory_items = self.clover_client.get_inventory_items()
            item_lookup = {item['id']: item for item in inventory_items}
            
            # Process orders to calculate sales metrics
            sales_data = self._calculate_sales_metrics(orders, item_lookup)
            
            # Update cache in database
            cache_results = self._update_sales_cache(merchant_id, sales_data, start_date, end_date)
            
            return {
                'success': True,
                'orders_processed': len(orders),
                'items_updated': len(cache_results),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'sales_data': sales_data
            }
            
        except Exception as e:
            logger.error(f"Error processing sales data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_sales_metrics(self, orders: List[Dict], item_lookup: Dict) -> Dict:
        """
        Calculate sales metrics from orders.
        
        Args:
            orders: List of order dictionaries
            item_lookup: Dictionary mapping item IDs to item details
            
        Returns:
            Dictionary with sales metrics per item
        """
        sales_metrics = defaultdict(lambda: {
            'quantity_sold': 0,
            'total_revenue': 0.0,
            'item_name': '',
            'category': ''
        })
        
        for order in orders:
            line_items = order.get('lineItems', {}).get('elements', [])
            
            for line_item in line_items:
                item = line_item.get('item', {})
                item_id = item.get('id')
                
                if not item_id:
                    continue
                
                quantity = line_item.get('unitQty', 1)
                price = line_item.get('price', 0) / 100.0  # Convert from cents to dollars
                
                # Get item details from inventory
                item_details = item_lookup.get(item_id, {})
                item_name = item.get('name') or item_details.get('name', f'Unknown Item {item_id}')
                
                # Get category
                categories = item_details.get('categories', {}).get('elements', [])
                category = categories[0].get('name', 'Uncategorized') if categories else 'Uncategorized'
                
                # Update metrics
                sales_metrics[item_id]['quantity_sold'] += quantity
                sales_metrics[item_id]['total_revenue'] += price * quantity
                sales_metrics[item_id]['item_name'] = item_name
                sales_metrics[item_id]['category'] = category
        
        return dict(sales_metrics)
    
    def _update_sales_cache(self, merchant_id: str, sales_data: Dict, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Update the sales cache in the database.
        
        Args:
            merchant_id: Merchant ID
            sales_data: Sales metrics dictionary
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            List of updated item IDs
        """
        updated_items = []
        
        try:
            # Clear existing cache for this period and merchant
            SalesCache.query.filter_by(
                merchant_id=merchant_id,
                period_start=start_date,
                period_end=end_date
            ).delete()
            
            # Insert new cache entries
            for item_id, metrics in sales_data.items():
                cache_entry = SalesCache(
                    merchant_id=merchant_id,
                    item_id=item_id,
                    item_name=metrics['item_name'],
                    category=metrics['category'],
                    quantity_sold=metrics['quantity_sold'],
                    total_revenue=metrics['total_revenue'],
                    period_start=start_date,
                    period_end=end_date,
                    last_updated=datetime.utcnow()
                )
                
                db.session.add(cache_entry)
                updated_items.append(item_id)
            
            db.session.commit()
            logger.info(f"Updated cache for {len(updated_items)} items")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating sales cache: {e}")
            raise
        
        return updated_items
    
    def get_best_selling_items(self, merchant_id: str, limit: int = 10, category: str = None) -> List[Dict]:
        """
        Get best-selling items from the cache.
        
        Args:
            merchant_id: Merchant ID
            limit: Maximum number of items to return
            category: Optional category filter
            
        Returns:
            List of best-selling items
        """
        try:
            query = SalesCache.query.filter_by(merchant_id=merchant_id)
            
            if category:
                query = query.filter_by(category=category)
            
            # Get the most recent cache entries
            latest_period = query.order_by(SalesCache.last_updated.desc()).first()
            if not latest_period:
                return []
            
            # Filter by the latest period
            query = query.filter_by(
                period_start=latest_period.period_start,
                period_end=latest_period.period_end
            )
            
            # Order by quantity sold and limit results
            best_selling = query.order_by(SalesCache.quantity_sold.desc()).limit(limit).all()
            
            return [item.to_dict() for item in best_selling]
            
        except Exception as e:
            logger.error(f"Error getting best-selling items: {e}")
            return []
    
    def is_cache_fresh(self, merchant_id: str, max_age_hours: int = None) -> bool:
        """
        Check if the cache is fresh enough.
        
        Args:
            merchant_id: Merchant ID
            max_age_hours: Maximum age in hours (defaults to config value)
            
        Returns:
            True if cache is fresh, False otherwise
        """
        if max_age_hours is None:
            max_age_hours = Config.CACHE_EXPIRY_HOURS
        
        try:
            latest_cache = SalesCache.query.filter_by(merchant_id=merchant_id).order_by(
                SalesCache.last_updated.desc()
            ).first()
            
            if not latest_cache:
                return False
            
            age = datetime.utcnow() - latest_cache.last_updated
            return age.total_seconds() < (max_age_hours * 3600)
            
        except Exception as e:
            logger.error(f"Error checking cache freshness: {e}")
            return False

