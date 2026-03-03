import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False

    # SendCloud Configuration
    SENDCLOUD_APP_KEY = os.getenv('SENDCLOUD_APP_KEY', '')

    # Third-party logging (Logtail / Better Stack)
    LOGTAIL_SOURCE_TOKEN = os.getenv('LOGTAIL_SOURCE_TOKEN', '')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
