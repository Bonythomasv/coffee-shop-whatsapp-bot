from src.models.user import db
from datetime import datetime

class SalesCache(db.Model):
    __tablename__ = 'sales_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.String(100), nullable=False)
    item_id = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    quantity_sold = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for faster queries
    __table_args__ = (
        db.Index('idx_merchant_period', 'merchant_id', 'period_start', 'period_end'),
        db.Index('idx_item_merchant', 'item_id', 'merchant_id'),
    )

    def __repr__(self):
        return f'<SalesCache {self.item_name}: {self.quantity_sold} sold>'

    def to_dict(self):
        return {
            'id': self.id,
            'merchant_id': self.merchant_id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'category': self.category,
            'quantity_sold': self.quantity_sold,
            'total_revenue': self.total_revenue,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class WhatsAppMessage(db.Model):
    __tablename__ = 'whatsapp_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    message_sid = db.Column(db.String(100), unique=True, nullable=False)
    from_number = db.Column(db.String(50), nullable=False)
    to_number = db.Column(db.String(50), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    response_body = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    response_time_ms = db.Column(db.Integer, nullable=True)  # Time taken to process and respond in milliseconds
    
    def __repr__(self):
        return f'<WhatsAppMessage {self.message_sid}: {self.message_body[:50]}...>'

    def to_dict(self):
        return {
            'id': self.id,
            'message_sid': self.message_sid,
            'from_number': self.from_number,
            'to_number': self.to_number,
            'message_body': self.message_body,
            'response_body': self.response_body,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'processed': self.processed,
            'response_time_ms': self.response_time_ms
        }

