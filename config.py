import os
from datetime import timedelta

class Config:
    """Configuration settings for the application."""
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tariffs.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }
    
    # Hapag-Lloyd URL
    BASE_URL = "https://www.hapag-lloyd.com/en/online-business/quotation/detention-demurrage.html"
    
    # Download directory for PDFs
    DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
    
    # OpenAI API configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Debug mode
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', 't', '1']
