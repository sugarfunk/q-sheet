"""
F3 Q-Sheet Configuration
Load settings from environment variables with sensible defaults
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Flask Configuration
class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'qsheet.db'))

    # Application Settings
    REGION_NAME = os.getenv('REGION_NAME', 'F3 Cherokee')
    SIGNUP_WINDOW_DAYS = int(os.getenv('SIGNUP_WINDOW_DAYS', '90'))
    REMINDER_DAYS_BEFORE = int(os.getenv('REMINDER_DAYS_BEFORE', '2'))

    # Passwords (will also be stored in DB, but env vars take precedence)
    SIGNUP_PASSWORD = os.getenv('SIGNUP_PASSWORD', 'f3cherokee')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

    # SMTP Configuration
    SMTP_ENABLED = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'F3 Q-Sheet')

    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False


# Select config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}

def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'production')
    return config.get(env, config['default'])
