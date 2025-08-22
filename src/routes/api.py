"""
API routes for sales data queries and system management.
"""

import logging
from flask import Blueprint, jsonify, request
from src.services.sales_processor import SalesProcessor
from src.services.clover_api import CloverAPIClient
from src.config import Config
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Get scheduler instance from main app
scheduler = None

def set_scheduler(scheduler_instance):
    """Set the scheduler instance for API endpoints."""
    global scheduler
    scheduler = scheduler_instance

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
        merchant_id = request.args.get('merchant_id', Config.CLOVER_MERCHANT_ID or 'TEST_MERCHANT_001')
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
        merchant_id = data.get('merchant_id', Config.CLOVER_MERCHANT_ID or 'TEST_MERCHANT_001')
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
        merchant_id = request.args.get('merchant_id', Config.CLOVER_MERCHANT_ID or 'TEST_MERCHANT_001')
        
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

@api_bp.route('/sales/cache-clear', methods=['POST'])
def clear_sales_cache():
    """
    Clear sales cache for a specific merchant.
    
    JSON body:
    - merchant_id: Merchant ID to clear cache for (required)
    """
    try:
        data = request.get_json() or {}
        merchant_id = data.get('merchant_id')
        
        if not merchant_id:
            return jsonify({
                'success': False,
                'error': 'merchant_id is required'
            }), 400
        
        # Clear cache for the specified merchant
        deleted_count = SalesCache.query.filter_by(merchant_id=merchant_id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} cache entries for merchant {merchant_id}'
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        db.session.rollback()
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

@api_bp.route('/env', methods=['GET'])
def get_environment_variables():
    """
    Display environment variables for debugging.
    Note: Sensitive values are masked for security.
    """
    import os
    from src.config import Config
    
    try:
        # Get all environment variables related to the app
        env_vars = {
            'FLASK_ENV': os.getenv('FLASK_ENV', 'NOT SET'),
            'FLASK_DEBUG': os.getenv('FLASK_DEBUG', 'NOT SET'),
            'SECRET_KEY': 'SET' if os.getenv('SECRET_KEY') else 'NOT SET',
            'DATABASE_URL': 'SET' if os.getenv('DATABASE_URL') else 'NOT SET',
            
            # Clover API
            'CLOVER_API_TOKEN': 'SET' if os.getenv('CLOVER_API_TOKEN') else 'NOT SET',
            'CLOVER_MERCHANT_ID': 'SET' if os.getenv('CLOVER_MERCHANT_ID') else 'NOT SET',
            'CLOVER_BASE_URL': os.getenv('CLOVER_BASE_URL', 'NOT SET'),
            
            # Twilio
            'TWILIO_ACCOUNT_SID': 'SET' if os.getenv('TWILIO_ACCOUNT_SID') else 'NOT SET',
            'TWILIO_AUTH_TOKEN': 'SET' if os.getenv('TWILIO_AUTH_TOKEN') else 'NOT SET',
            'TWILIO_WHATSAPP_NUMBER': os.getenv('TWILIO_WHATSAPP_NUMBER', 'NOT SET'),
            
            # LLM
            'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'NOT SET'),
            'OPENAI_API_KEY': 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET',
            'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'NOT SET'),
            'TOGETHER_API_KEY': 'SET' if os.getenv('TOGETHER_API_KEY') else 'NOT SET',
            'XAI_API_KEY': 'SET' if os.getenv('XAI_API_KEY') else 'NOT SET',
            
            # Other
            'DEBUG': os.getenv('DEBUG', 'NOT SET'),
            'TESTING': os.getenv('TESTING', 'NOT SET'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'NOT SET'),
            'CACHE_EXPIRY_HOURS': os.getenv('CACHE_EXPIRY_HOURS', 'NOT SET')
        }
        
        # Config class values
        config_values = {
            'Config.CLOVER_ACCESS_TOKEN': 'SET' if Config.CLOVER_ACCESS_TOKEN else 'NOT SET',
            'Config.CLOVER_MERCHANT_ID': 'SET' if Config.CLOVER_MERCHANT_ID else 'NOT SET',
            'Config.CLOVER_API_BASE_URL': Config.CLOVER_API_BASE_URL,
            'Config.OPENAI_API_KEY': 'SET' if Config.OPENAI_API_KEY else 'NOT SET',
            'Config.TWILIO_ACCOUNT_SID': 'SET' if Config.TWILIO_ACCOUNT_SID else 'NOT SET',
            'Config.SQLALCHEMY_DATABASE_URI': 'SET' if Config.SQLALCHEMY_DATABASE_URI else 'NOT SET'
        }
        
        return jsonify({
            'success': True,
            'environment_variables': env_vars,
            'config_class_values': config_values,
            'note': 'Sensitive values are masked for security'
        })
        
    except Exception as e:
        logger.error(f"Error getting environment variables: {e}")
        return jsonify({
            'success': False,
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

@api_bp.route('/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler status and job information."""
    try:
        if not scheduler:
            return jsonify({
                'success': False,
                'error': 'Scheduler not initialized'
            }), 500
            
        status = scheduler.get_scheduler_status()
        next_refresh = scheduler.get_next_refresh_time()
        
        return jsonify({
            'success': True,
            'scheduler_status': status,
            'next_refresh': next_refresh.isoformat() if next_refresh else None
        })
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/scheduler/refresh', methods=['POST'])
def trigger_manual_refresh():
    """Trigger a manual sales data refresh."""
    try:
        if not scheduler:
            return jsonify({
                'success': False,
                'error': 'Scheduler not initialized'
            }), 500
            
        scheduler.trigger_manual_refresh()
        
        return jsonify({
            'success': True,
            'message': 'Manual refresh triggered successfully'
        })
        
    except Exception as e:
        logger.error(f"Error triggering manual refresh: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

