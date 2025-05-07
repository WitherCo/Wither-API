import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration class for the API Gateway"""
    
    # Basic app configuration
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev_secret_key')
    
    # Database settings (SQLite for simplicity, can be changed to any DB)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///apigateway.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # API settings
    API_TITLE = 'API Gateway'
    API_VERSION = '1.0'
    
    # Rate limiting settings
    RATELIMIT_DEFAULT = '100 per hour'
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Webhook settings
    WEBHOOK_TIMEOUT = int(os.environ.get('WEBHOOK_TIMEOUT', 5))  # seconds
    
    # Bot integration settings
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
    BOT_API_BASE_URL = os.environ.get('BOT_API_BASE_URL', '')
