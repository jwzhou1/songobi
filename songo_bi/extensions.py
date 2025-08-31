# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Flask extensions initialization for Songo BI.
"""

from celery import Celery
from flask_appbuilder.security.sqla.manager import SecurityManager
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

# Database
db = SQLAlchemy()

# Cache manager
cache_manager = Cache()

# Security manager (will be initialized in app factory)
security_manager = None

# Celery for background tasks
celery_app = Celery("songo_bi")


def init_celery(app):
    """Initialize Celery with Flask app context."""
    
    class ContextTask(celery_app.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    celery_app.conf.update(app.config.get("CELERY_CONFIG", {}))
    return celery_app
