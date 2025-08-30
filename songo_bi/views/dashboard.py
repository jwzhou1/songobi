# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Dashboard views for Songo BI.
"""

import logging
from flask import Blueprint, render_template, request, jsonify
from flask_appbuilder.security.decorators import has_access

from songo_bi.services.dashboard import DashboardService

logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint("dashboard", __name__)

# Initialize dashboard service
dashboard_service = DashboardService()


@dashboard_bp.route("/")
@has_access
def dashboard_list():
    """Dashboard list view."""
    return render_template("songo_bi/dashboard_list.html")


@dashboard_bp.route("/<int:dashboard_id>")
@has_access
def dashboard_view(dashboard_id: int):
    """Individual dashboard view."""
    return render_template("songo_bi/dashboard.html", dashboard_id=dashboard_id)


@dashboard_bp.route("/new")
@has_access
def new_dashboard():
    """New dashboard creation view."""
    return render_template("songo_bi/dashboard_new.html")


@dashboard_bp.route("/sql")
@has_access
def sql_lab():
    """SQL Lab view."""
    return render_template("songo_bi/sql_lab.html")


@dashboard_bp.route("/explore")
@has_access
def explore():
    """Data exploration view."""
    return render_template("songo_bi/explore.html")
