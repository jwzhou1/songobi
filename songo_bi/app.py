# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Main Flask application factory for Songo BI.
"""

import logging
import os
from typing import Any, Dict, Optional

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_compress import Compress
from flask_cors import CORS
from flask_migrate import Migrate
from flask_talisman import Talisman

from songo_bi.config import get_config
from songo_bi.extensions import (
    cache_manager,
    celery_app,
    db,
    security_manager,
)
from songo_bi.utils.logging import configure_logging


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration name to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Configure logging
    configure_logging(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize AppBuilder
    init_appbuilder(app)
    
    # Configure security
    configure_security(app)
    
    return app


def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    
    # Database
    db.init_app(app)
    
    # Migration
    Migrate(app, db)
    
    # Caching
    cache_manager.init_app(app)
    
    # Compression
    Compress(app)
    
    # CORS
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/songo/*": {"origins": "*"}
    })
    
    # Security headers
    Talisman(
        app,
        force_https=app.config.get("TALISMAN_ENABLED", True),
        content_security_policy=app.config.get("CONTENT_SECURITY_POLICY", {}),
    )
    
    # Celery
    celery_app.conf.update(app.config)


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    
    from songo_bi.views.api import api_bp
    from songo_bi.views.core import core_bp
    from songo_bi.views.dashboard import dashboard_bp
    from songo_bi.views.netsuite import netsuite_bp
    from songo_bi.views.chatbot import chatbot_bp
    
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(core_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(netsuite_bp, url_prefix="/netsuite")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")


def init_appbuilder(app: Flask) -> None:
    """Initialize Flask-AppBuilder."""
    
    from songo_bi.security import SongoSecurityManager
    
    # Initialize AppBuilder with custom security manager
    appbuilder = AppBuilder(
        app,
        db.session,
        security_manager_class=SongoSecurityManager,
        base_template="songo_bi/base.html",
        indexview=None,
    )
    
    # Import views to register them
    from songo_bi import views  # noqa: F401
    
    app.appbuilder = appbuilder


def configure_security(app: Flask) -> None:
    """Configure application security settings."""
    
    # Set up security manager
    security_manager.init_app(app)
    
    # Configure session settings
    app.config.update(
        SESSION_COOKIE_SECURE=app.config.get("SESSION_COOKIE_SECURE", True),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=app.config.get("PERMANENT_SESSION_LIFETIME", 3600),
    )


# Create application instance for development
if __name__ == "__main__":
    app = create_app("development")
    app.run(debug=True, host="0.0.0.0", port=8088)
