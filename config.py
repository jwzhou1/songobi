# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Songo BI Configuration
Simple development configuration
"""

import os
from datetime import timedelta

# Base configuration
class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings - using SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///songo_bi.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cache settings
    CACHE_TYPE = 'simple'
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Flask-AppBuilder settings
    APP_NAME = "Songo BI"
    APP_THEME = ""
    
    # Authentication
    AUTH_TYPE = 1  # Database authentication
    AUTH_ROLE_ADMIN = 'Admin'
    AUTH_ROLE_PUBLIC = 'Public'
    
    # Default admin user
    ADMIN_USER = 'admin'
    ADMIN_PASSWORD = 'admin'
    ADMIN_EMAIL = 'admin@songobi.com'
    
    # API settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # NetSuite settings (optional)
    NETSUITE_ACCOUNT_ID = os.environ.get('NETSUITE_ACCOUNT_ID', '')
    NETSUITE_CONSUMER_KEY = os.environ.get('NETSUITE_CONSUMER_KEY', '')
    NETSUITE_CONSUMER_SECRET = os.environ.get('NETSUITE_CONSUMER_SECRET', '')
    NETSUITE_TOKEN_ID = os.environ.get('NETSUITE_TOKEN_ID', '')
    NETSUITE_TOKEN_SECRET = os.environ.get('NETSUITE_TOKEN_SECRET', '')
    
    # Development settings
    DEBUG = True
    TESTING = False
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
