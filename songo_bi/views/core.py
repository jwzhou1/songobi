# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Core views for Songo BI.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_appbuilder.security.decorators import has_access

logger = logging.getLogger(__name__)

# Create blueprint
core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def index():
    """Main application index."""
    return redirect("/dashboard/")


@core_bp.route("/app")
@has_access
def app_view():
    """Main application view."""
    return render_template("songo_bi/app.html")


@core_bp.route("/login")
def login():
    """Login page."""
    return render_template("songo_bi/login.html")


@core_bp.route("/about")
def about():
    """About page."""
    return render_template("songo_bi/about.html", 
                         version=current_app.config.get("VERSION", "0.1.0"))


@core_bp.route("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": current_app.config.get("VERSION", "0.1.0"),
        "timestamp": "2025-01-01T00:00:00Z"
    }
