"""
Twilio WhatsApp client for sending messages and managing WhatsApp Business API.
"""

import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from typing import Optional, Dict, List
from src.config import Config

logger = logging.getLogger(__name__)

class WhatsAppClient:
    """Client for sending WhatsApp messages via Twilio."""
    
    def __init__(self, account_sid: str = None, auth_token: str = None, whatsapp_number: str = None):
        """
        Initialize the WhatsApp client.
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            whatsapp_number: Twilio WhatsApp number (e.g., 'whatsapp:+14155238886')
        """
        self.account_sid = account_sid or Config.TWILIO_ACCOUNT_SID
        self.auth_token = auth_token or Config.TWILIO_AUTH_TOKEN
        self.whatsapp_number = whatsapp_number or Config.TWILIO_WHATSAPP_NUMBER
        
        if not self.account_sid or not self.auth_token:
            logger.warning("Twilio credentials not configured. WhatsApp sending will be simulated.")
            self.client = None
            self.use_mock = True
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.use_mock = False
                logger.info("Twilio WhatsApp client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
                self.use_mock = True
    
    def send_message(self, to_number: str, message_body: str, media_url: str = None) -> Dict:
        """
        Send a WhatsApp message.
        
        Args:
            to_number: Recipient's WhatsApp number (e.g., 'whatsapp:+1234567890')
            message_body: Message text content
            media_url: Optional URL for media attachment
            
        Returns:
            Dictionary with send result
        """
        try:
            if self.use_mock:
                return self._send_mock_message(to_number, message_body, media_url)
            
            # Ensure the to_number has the whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            # Prepare message parameters
            message_params = {
                'body': message_body,
                'from_': self.whatsapp_number,
                'to': to_number
            }
            
            # Add media if provided
            if media_url:
                message_params['media_url'] = [media_url]
            
            # Send the message
            message = self.client.messages.create(**message_params)
            
            logger.info(f"WhatsApp message sent successfully. SID: {message.sid}")
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': to_number,
                'from': self.whatsapp_number,
                'body': message_body
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending WhatsApp message: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': getattr(e, 'code', None),
                'to': to_number,
                'body': message_body
            }
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {e}")
            return {
                'success': False,
                'error': str(e),
                'to': to_number,
                'body': message_body
            }
    
    def _send_mock_message(self, to_number: str, message_body: str, media_url: str = None) -> Dict:
        """Send a mock message for testing purposes."""
        logger.info(f"MOCK: Sending WhatsApp message to {to_number}: {message_body}")
        
        if media_url:
            logger.info(f"MOCK: With media: {media_url}")
        
        return {
            'success': True,
            'message_sid': f'MOCK_MSG_{hash(message_body) % 10000}',
            'status': 'sent',
            'to': to_number,
            'from': self.whatsapp_number,
            'body': message_body,
            'mock': True
        }
    
    def send_template_message(self, to_number: str, template_name: str, template_params: List[str] = None) -> Dict:
        """
        Send a WhatsApp template message.
        
        Args:
            to_number: Recipient's WhatsApp number
            template_name: Name of the approved template
            template_params: Parameters for the template
            
        Returns:
            Dictionary with send result
        """
        try:
            if self.use_mock:
                logger.info(f"MOCK: Sending template '{template_name}' to {to_number}")
                return {
                    'success': True,
                    'message_sid': f'MOCK_TEMPLATE_{hash(template_name) % 10000}',
                    'status': 'sent',
                    'template': template_name,
                    'mock': True
                }
            
            # Ensure the to_number has the whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            # For template messages, you would typically use Twilio's Content API
            # This is a simplified implementation
            message = self.client.messages.create(
                content_sid=template_name,  # This would be the actual template SID
                from_=self.whatsapp_number,
                to=to_number
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'template': template_name
            }
            
        except Exception as e:
            logger.error(f"Error sending template message: {e}")
            return {
                'success': False,
                'error': str(e),
                'template': template_name
            }
    
    def get_message_status(self, message_sid: str) -> Dict:
        """
        Get the status of a sent message.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dictionary with message status
        """
        try:
            if self.use_mock:
                return {
                    'success': True,
                    'message_sid': message_sid,
                    'status': 'delivered',
                    'mock': True
                }
            
            message = self.client.messages(message_sid).fetch()
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'date_updated': message.date_updated.isoformat() if message.date_updated else None
            }
            
        except Exception as e:
            logger.error(f"Error getting message status: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_sid': message_sid
            }
    
    def format_business_message(self, data: Dict, message_type: str = 'sales_summary') -> str:
        """
        Format business data into a WhatsApp-friendly message.
        
        Args:
            data: Business data to format
            message_type: Type of message to format
            
        Returns:
            Formatted message string
        """
        if message_type == 'sales_summary':
            return self._format_sales_summary(data)
        elif message_type == 'best_selling':
            return self._format_best_selling(data)
        elif message_type == 'revenue_report':
            return self._format_revenue_report(data)
        else:
            return str(data)
    
    def _format_sales_summary(self, data: Dict) -> str:
        """Format sales summary data."""
        items = data.get('best_selling_items', [])
        if not items:
            return "No sales data available."
        
        message_lines = ["📊 *Sales Summary*\\n"]
        
        for i, item in enumerate(items[:5], 1):
            emoji = "☕" if item.get('category') == 'Coffee' else "🥐"
            message_lines.append(
                f"{emoji} {i}. *{item['item_name']}*\\n"
                f"   Sold: {item['quantity_sold']} | Revenue: ${item['total_revenue']:.2f}\\n"
            )
        
        total_items = sum(item['quantity_sold'] for item in items)
        total_revenue = sum(item['total_revenue'] for item in items)
        
        message_lines.append(f"\\n📈 *Total*: {total_items} items | ${total_revenue:.2f}")
        
        return "\\n".join(message_lines)
    
    def _format_best_selling(self, data: Dict) -> str:
        """Format best-selling items data."""
        items = data.get('best_selling_items', [])
        if not items:
            return "No sales data available."
        
        top_item = items[0]
        emoji = "☕" if top_item.get('category') == 'Coffee' else "🥐"
        
        message = f"{emoji} *Best Seller*: {top_item['item_name']}\\n"
        message += f"Sold: {top_item['quantity_sold']} units\\n"
        message += f"Revenue: ${top_item['total_revenue']:.2f}"
        
        if len(items) > 1:
            second_item = items[1]
            emoji2 = "☕" if second_item.get('category') == 'Coffee' else "🥐"
            message += f"\\n\\n{emoji2} *Runner-up*: {second_item['item_name']}\\n"
            message += f"Sold: {second_item['quantity_sold']} units"
        
        return message
    
    def _format_revenue_report(self, data: Dict) -> str:
        """Format revenue report data."""
        items = data.get('best_selling_items', [])
        if not items:
            return "No revenue data available."
        
        total_revenue = sum(item['total_revenue'] for item in items)
        total_items = sum(item['quantity_sold'] for item in items)
        avg_price = total_revenue / total_items if total_items > 0 else 0
        
        message = f"💰 *Revenue Report*\\n\\n"
        message += f"Total Revenue: ${total_revenue:.2f}\\n"
        message += f"Items Sold: {total_items}\\n"
        message += f"Average Price: ${avg_price:.2f}\\n\\n"
        
        # Top revenue generators
        message += "*Top Revenue Generators:*\\n"
        for i, item in enumerate(items[:3], 1):
            emoji = "☕" if item.get('category') == 'Coffee' else "🥐"
            message += f"{emoji} {i}. {item['item_name']}: ${item['total_revenue']:.2f}\\n"
        
        return message
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate a phone number format for WhatsApp.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove whatsapp: prefix if present
        if phone_number.startswith('whatsapp:'):
            phone_number = phone_number[9:]
        
        # Basic validation - should start with + and contain only digits
        if not phone_number.startswith('+'):
            return False
        
        # Remove + and check if remaining characters are digits
        digits_only = phone_number[1:]
        if not digits_only.isdigit():
            return False
        
        # Check length (international numbers are typically 10-15 digits)
        if len(digits_only) < 10 or len(digits_only) > 15:
            return False
        
        return True

