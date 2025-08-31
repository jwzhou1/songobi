# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Configuration settings for Songo BI application.
"""

import os
from datetime import timedelta
from typing import Any, Dict, Optional, Type


class Config:
    """Base configuration class."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///songo_bi.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine options - simplified for SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Redis settings
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Celery settings
    CELERY_CONFIG = {
        "broker_url": REDIS_URL,
        "result_backend": REDIS_URL,
        "worker_prefetch_multiplier": 1,
        "task_acks_late": True,
        "task_annotations": {
            "*": {"rate_limit": "100/s"}
        },
        "beat_schedule": {
            "netsuite-refresh": {
                "task": "songo_bi.tasks.netsuite.refresh_netsuite_data",
                "schedule": timedelta(minutes=30),
            },
        },
    }
    
    # Cache settings
    CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": REDIS_URL,
        "CACHE_DEFAULT_TIMEOUT": 300,
    }
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Flask-AppBuilder settings
    FAB_API_SWAGGER_UI = True
    FAB_ROLES = {
        "Admin": [[".*", ".*"]],
        "Alpha": [[".*", ".*"]],
        "Gamma": [[".*", "can_read"]],
        "Public": [[".*", "can_read"]],
    }
    
    # Songo BI specific settings
    SONGO_WEBSERVER_PORT = int(os.environ.get("SONGO_WEBSERVER_PORT", 8088))
    SONGO_WEBSERVER_ADDRESS = os.environ.get("SONGO_WEBSERVER_ADDRESS", "0.0.0.0")
    SONGO_WEBSERVER_TIMEOUT = int(os.environ.get("SONGO_WEBSERVER_TIMEOUT", 60))
    
    # NetSuite settings
    NETSUITE_ACCOUNT_ID = os.environ.get("NETSUITE_ACCOUNT_ID")
    NETSUITE_CONSUMER_KEY = os.environ.get("NETSUITE_CONSUMER_KEY")
    NETSUITE_CONSUMER_SECRET = os.environ.get("NETSUITE_CONSUMER_SECRET")
    NETSUITE_TOKEN_ID = os.environ.get("NETSUITE_TOKEN_ID")
    NETSUITE_TOKEN_SECRET = os.environ.get("NETSUITE_TOKEN_SECRET")
    NETSUITE_REFRESH_INTERVAL = int(os.environ.get("NETSUITE_REFRESH_INTERVAL", 1800))  # 30 minutes
    
    # AI/Chatbot settings
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")
    CHATBOT_MAX_TOKENS = int(os.environ.get("CHATBOT_MAX_TOKENS", 2000))
    CHATBOT_TEMPERATURE = float(os.environ.get("CHATBOT_TEMPERATURE", 0.7))
    
    # Feature flags
    FEATURE_FLAGS = {
        "ENABLE_NETSUITE": os.environ.get("ENABLE_NETSUITE", "true").lower() == "true",
        "ENABLE_CHATBOT": os.environ.get("ENABLE_CHATBOT", "true").lower() == "true",
        "ENABLE_AI_INSIGHTS": os.environ.get("ENABLE_AI_INSIGHTS", "true").lower() == "true",
        "ENABLE_AUTO_REFRESH": os.environ.get("ENABLE_AUTO_REFRESH", "true").lower() == "true",
    }
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    
    # Security headers
    TALISMAN_ENABLED = True
    CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline' 'unsafe-eval'",
        "style-src": "'self' 'unsafe-inline'",
        "img-src": "'self' data: https:",
        "font-src": "'self' data:",
        "connect-src": "'self'",
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Disable security features for development
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    TALISMAN_ENABLED = False
    
    # Enable debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Use simple cache for testing
    CACHE_CONFIG = {
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 300,
    }


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    TALISMAN_ENABLED = True
    
    # Production logging
    LOG_LEVEL = "WARNING"


class StagingConfig(ProductionConfig):
    """Staging configuration."""
    
    DEBUG = True
    LOG_LEVEL = "INFO"


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: Optional[str] = None) -> Type[Config]:
    """
    Get configuration class based on environment.
    
    Args:
        config_name: Configuration name to use
        
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")
    
    return config_map.get(config_name, DevelopmentConfig)
