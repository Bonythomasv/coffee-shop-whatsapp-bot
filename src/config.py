import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf#FGSgvasgf$5$WGT'
    
    # Database configuration
    # For development, use SQLite. For production, use PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Production PostgreSQL
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Development SQLite
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Twilio WhatsApp configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')  # Twilio sandbox number
    
    # Clover API configuration
    CLOVER_API_BASE_URL = os.environ.get('CLOVER_API_BASE_URL', 'https://sandbox.dev.clover.com')
    CLOVER_ACCESS_TOKEN = os.environ.get('CLOVER_ACCESS_TOKEN')
    CLOVER_MERCHANT_ID = os.environ.get('CLOVER_MERCHANT_ID')
    
    # LLM configuration
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')  # 'openai', 'together', 'xai'
    
    # OpenAI configuration (if using OpenAI)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')  # Updated to supported model
    
    # Together AI configuration (for Llama 3.1)
    TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY')
    TOGETHER_MODEL = os.environ.get('TOGETHER_MODEL', 'meta-llama/Llama-3.1-8B-Instruct-Turbo')
    
    # xAI configuration (for Grok)
    XAI_API_KEY = os.environ.get('XAI_API_KEY')
    XAI_MODEL = os.environ.get('XAI_MODEL', 'grok-3')
    
    # Cache configuration
    CACHE_EXPIRY_HOURS = int(os.environ.get('CACHE_EXPIRY_HOURS', 24))  # Cache data for 24 hours by default
    
    # CORS configuration
    CORS_ORIGINS = ['*']  # Allow all origins for development

