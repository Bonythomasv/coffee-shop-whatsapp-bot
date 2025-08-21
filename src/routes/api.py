"""
API routes for sales data queries and system management.
"""

import logging
from flask import Blueprint, request, jsonify
from src.services.sales_processor import SalesProcessor
from src.services.clover_api import CloverAPIClient
from src.models.sales_cache import SalesCache, WhatsAppMessage
from src.models.user import db

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize services
sales_processor = SalesProcessor()

@api_bp.route('/sales/best-selling', methods=['GET'])
def get_best_selling_items():
    """
    Get best-selling items for a merchant.
    
    Query parameters:
    - merchant_id: Merchant ID (default: TEST_MERCHANT_001)
    - limit: Number of items to return (default: 10)
    - category: Filter by category (optional)
    """
    try:
        merchant_id = request.args.get('merchant_id', 'TEST_MERCHANT_001')
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category')
        
        # Get best-selling items
        items = sales_processor.get_best_selling_items(
            merchant_id=merchant_id,
            limit=limit,
            category=category
        )
        
        return jsonify({
            'success': True,
            'merchant_id': merchant_id,
            'items': items,
            'total': len(items),
            'category_filter': category
        })
        
    except Exception as e:
        logger.error(f"Error getting best-selling items: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sales/refresh', methods=['POST'])
def refresh_sales_data():
    """
    Refresh sales data from Clover API.
    
    JSON body:
    - merchant_id: Merchant ID (default: TEST_MERCHANT_001)
    - days_back: Number of days to fetch (default: 7)
    """
    try:
        data = request.get_json() or {}
        merchant_id = data.get('merchant_id', 'TEST_MERCHANT_001')
        days_back = data.get('days_back', 7)
        
        # Process and cache sales data
        result = sales_processor.process_and_cache_sales_data(
            merchant_id=merchant_id,
            days_back=days_back
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error refreshing sales data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sales/cache-status', methods=['GET'])
def get_cache_status():
    """
    Get cache status for a merchant.
    
    Query parameters:
    - merchant_id: Merchant ID (default: TEST_MERCHANT_001)
    """
    try:
        merchant_id = request.args.get('merchant_id', 'TEST_MERCHANT_001')
        
        # Check cache freshness
        is_fresh = sales_processor.is_cache_fresh(merchant_id)
        
        # Get latest cache entry
        latest_cache = SalesCache.query.filter_by(merchant_id=merchant_id).order_by(
            SalesCache.last_updated.desc()
        ).first()
        
        cache_info = None
        if latest_cache:
            cache_info = {
                'last_updated': latest_cache.last_updated.isoformat(),
                'period_start': latest_cache.period_start.isoformat(),
                'period_end': latest_cache.period_end.isoformat()
            }
        
        return jsonify({
            'success': True,
            'merchant_id': merchant_id,
            'is_fresh': is_fresh,
            'cache_info': cache_info
        })
        
    except Exception as e:
        logger.error(f"Error getting cache status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/messages', methods=['GET'])
def get_whatsapp_messages():
    """
    Get WhatsApp message history.
    
    Query parameters:
    - limit: Number of messages to return (default: 50)
    - from_number: Filter by sender number (optional)
    """
    try:
        limit = int(request.args.get('limit', 50))
        from_number = request.args.get('from_number')
        
        query = WhatsAppMessage.query
        
        if from_number:
            query = query.filter_by(from_number=from_number)
        
        messages = query.order_by(WhatsAppMessage.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'messages': [msg.to_dict() for msg in messages],
            'total': len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        # Test Clover API (mock)
        clover_client = CloverAPIClient()
        orders = clover_client.get_orders()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected',
            'clover_api': 'available' if orders else 'unavailable',
            'mock_data': clover_client.use_mock_data
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/test/webhook', methods=['POST'])
def test_webhook():
    """
    Test endpoint for simulating WhatsApp webhook calls.
    
    JSON body should mimic Twilio webhook format:
    - MessageSid: Message ID
    - From: Sender number
    - To: Recipient number
    - Body: Message text
    """
    try:
        data = request.get_json() or {}
        
        # Simulate webhook data
        webhook_data = {
            'MessageSid': data.get('MessageSid', 'TEST_MSG_001'),
            'From': data.get('From', 'whatsapp:+1234567890'),
            'To': data.get('To', 'whatsapp:+14155238886'),
            'Body': data.get('Body', 'What is my best-selling drink this week?')
        }
        
        # Process the message (similar to webhook handler)
        from src.services.message_processor import MessageProcessor
        processor = MessageProcessor()
        
        response_text = processor.process_message(
            webhook_data['Body'],
            webhook_data['From']
        )
        
        return jsonify({
            'success': True,
            'webhook_data': webhook_data,
            'response': response_text
        })
        
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

