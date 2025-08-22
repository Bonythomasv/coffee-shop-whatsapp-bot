"""
Webhook routes for handling WhatsApp messages from Twilio.
"""

import logging
from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from src.config import Config
from src.models.sales_cache import WhatsAppMessage
from src.models.user import db
from src.services.message_processor import MessageProcessor
from src.services.whatsapp_client import WhatsAppClient

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__)

# Initialize services
message_processor = MessageProcessor()
whatsapp_client = WhatsAppClient()

@webhook_bp.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Handle incoming WhatsApp messages from Twilio.
    """
    try:
        # Validate the request (skip in development mode)
        if Config.TWILIO_AUTH_TOKEN and not Config.FLASK_ENV == 'development' and not _validate_twilio_request():
            logger.warning("Invalid Twilio request signature")
            return jsonify({'error': 'Invalid request'}), 403
        
        # Extract message data
        message_data = {
            'message_sid': request.form.get('MessageSid'),
            'from_number': request.form.get('From'),
            'to_number': request.form.get('To'),
            'message_body': request.form.get('Body', '').strip(),
            'num_media': int(request.form.get('NumMedia', 0))
        }
        
        logger.info(f"Received WhatsApp message: {message_data}")
        
        # Store the incoming message (handle duplicates)
        existing_message = WhatsAppMessage.query.filter_by(
            message_sid=message_data['message_sid']
        ).first()
        
        if existing_message:
            # Message already exists, skip processing if already processed
            if existing_message.processed:
                logger.info(f"Message {message_data['message_sid']} already processed, returning cached response")
                # Return the cached response instead of empty response
                twiml_response = MessagingResponse()
                twiml_response.message(existing_message.response_body or "I've already processed this message.")
                return str(twiml_response), 200, {'Content-Type': 'text/xml'}
            
            # Use existing message record
            whatsapp_message = existing_message
        else:
            # Create new message record
            whatsapp_message = WhatsAppMessage(
                message_sid=message_data['message_sid'],
                from_number=message_data['from_number'],
                to_number=message_data['to_number'],
                message_body=message_data['message_body']
            )
            
            db.session.add(whatsapp_message)
            db.session.commit()
        
        # Process the message and generate response
        response_text = message_processor.process_message(
            message_data['message_body'],
            message_data['from_number']
        )
        
        # Update the stored message with the response
        whatsapp_message.response_body = response_text
        whatsapp_message.processed = True
        db.session.commit()
        
        # Create Twilio response
        twiml_response = MessagingResponse()
        twiml_response.message(response_text)
        
        logger.info(f"Sent response: {response_text}")
        
        return str(twiml_response), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        
        # Send error response to user
        twiml_response = MessagingResponse()
        twiml_response.message("Sorry, I'm having trouble processing your request right now. Please try again later.")
        
        return str(twiml_response), 200, {'Content-Type': 'text/xml'}

@webhook_bp.route('/whatsapp/status', methods=['POST'])
def whatsapp_status_webhook():
    """
    Handle WhatsApp message status updates from Twilio.
    """
    try:
        status_data = {
            'message_sid': request.form.get('MessageSid'),
            'message_status': request.form.get('MessageStatus'),
            'error_code': request.form.get('ErrorCode'),
            'error_message': request.form.get('ErrorMessage')
        }
        
        logger.info(f"WhatsApp message status update: {status_data}")
        
        # Update message status in database if needed
        if status_data['message_sid']:
            message = WhatsAppMessage.query.filter_by(
                message_sid=status_data['message_sid']
            ).first()
            
            if message:
                # You could add a status field to track delivery status
                logger.info(f"Message {status_data['message_sid']} status: {status_data['message_status']}")
        
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        logger.error(f"Error processing status webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@webhook_bp.route('/whatsapp/send', methods=['POST'])
def send_whatsapp_message():
    """
    API endpoint to send WhatsApp messages programmatically.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        to_number = data.get('to')
        message_body = data.get('message')
        media_url = data.get('media_url')
        
        if not to_number or not message_body:
            return jsonify({'error': 'Missing required fields: to, message'}), 400
        
        # Validate phone number
        if not whatsapp_client.validate_phone_number(to_number):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Send the message
        result = whatsapp_client.send_message(to_number, message_body, media_url)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message_sid': result['message_sid'],
                'status': result.get('status'),
                'mock': result.get('mock', False)
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return jsonify({'error': str(e)}), 500

@webhook_bp.route('/whatsapp/send-sales-report', methods=['POST'])
def send_sales_report():
    """
    Send a formatted sales report via WhatsApp.
    """
    try:
        data = request.get_json() or {}
        to_number = data.get('to')
        merchant_id = data.get('merchant_id', 'TEST_MERCHANT_001')
        report_type = data.get('report_type', 'sales_summary')
        
        if not to_number:
            return jsonify({'error': 'Missing required field: to'}), 400
        
        # Get sales data
        from src.services.sales_processor import SalesProcessor
        sales_processor = SalesProcessor()
        
        # Refresh cache if needed
        if not sales_processor.is_cache_fresh(merchant_id):
            sales_processor.process_and_cache_sales_data(merchant_id)
        
        # Get best-selling items
        sales_data = {
            'best_selling_items': sales_processor.get_best_selling_items(merchant_id, limit=5)
        }
        
        # Format the message
        formatted_message = whatsapp_client.format_business_message(sales_data, report_type)
        
        # Send the message
        result = whatsapp_client.send_message(to_number, formatted_message)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message_sid': result['message_sid'],
                'report_type': report_type,
                'mock': result.get('mock', False)
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending sales report: {e}")
        return jsonify({'error': str(e)}), 500

def _validate_twilio_request():
    """
    Validate that the request is from Twilio using the request signature.
    """
    try:
        validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)
        
        # Get the URL that Twilio used to make the request
        url = request.url
        
        # Get the POST parameters
        params = request.form.to_dict()
        
        # Get the signature from the request headers
        signature = request.headers.get('X-Twilio-Signature', '')
        
        # Validate the request
        return validator.validate(url, params, signature)
        
    except Exception as e:
        logger.error(f"Error validating Twilio request: {e}")
        return False

