import os
import secrets

class Config:
    """Base configuration."""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    # Database
    DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flowrite.db')
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "2000 per day;500 per hour"
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL', 'memory://')
    
    # Logging
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
    LOG_LEVEL = 'INFO'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Production logging
    LOG_LEVEL = 'WARNING'  # Less verbose logging in production
    
    # Rate limiting with Redis in production
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Load configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 