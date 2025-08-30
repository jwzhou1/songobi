# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
API views for Songo BI.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request, current_app
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access_api
from marshmallow import Schema, fields

from songo_bi.extensions import db
from songo_bi.models.core import Database, Table, Query
from songo_bi.models.dashboard import Dashboard, Slice
from songo_bi.models.netsuite import NetSuiteConnection, NetSuiteQuery
from songo_bi.models.chatbot import ChatSession, ChatMessage
from songo_bi.services.dashboard import DashboardService
from songo_bi.services.netsuite import NetSuiteService
from songo_bi.services.chatbot import ChatbotService
from songo_bi.services.data import DataService

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint("api", __name__)

# Initialize services
dashboard_service = DashboardService()
netsuite_service = NetSuiteService()
data_service = DataService()


# Schemas for API serialization
class DashboardSchema(Schema):
    id = fields.Integer()
    dashboard_title = fields.String()
    description = fields.String()
    published = fields.Boolean()
    owner_id = fields.Integer()
    created_on = fields.DateTime()
    changed_on = fields.DateTime()


class ChartSchema(Schema):
    id = fields.Integer()
    slice_name = fields.String()
    viz_type = fields.String()
    description = fields.String()
    datasource_id = fields.Integer()


class NetSuiteConnectionSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    account_id = fields.String()
    is_active = fields.Boolean()
    auto_refresh = fields.Boolean()
    refresh_interval = fields.Integer()


# API Routes
@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    })


@api_bp.route("/dashboards", methods=["GET"])
@has_access_api
def get_dashboards():
    """Get list of dashboards."""
    try:
        user_id = request.args.get("user_id", type=int)
        dashboards = dashboard_service.get_dashboard_list(user_id)
        
        return jsonify({
            "success": True,
            "data": dashboards,
            "count": len(dashboards)
        })
        
    except Exception as e:
        logger.error(f"Failed to get dashboards: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/dashboards", methods=["POST"])
@has_access_api
def create_dashboard():
    """Create new dashboard."""
    try:
        data = request.get_json()
        
        dashboard = dashboard_service.create_dashboard(
            user_id=data.get("user_id"),
            title=data.get("title"),
            description=data.get("description", "")
        )
        
        return jsonify({
            "success": True,
            "data": {
                "id": dashboard.id,
                "title": dashboard.dashboard_title,
                "description": dashboard.description
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/dashboards/<int:dashboard_id>", methods=["GET"])
@has_access_api
def get_dashboard(dashboard_id: int):
    """Get dashboard by ID."""
    try:
        filters = request.args.get("filters")
        if filters:
            filters = eval(filters)  # In production, use proper JSON parsing
        
        dashboard_data = dashboard_service.get_dashboard_data(dashboard_id, filters)
        
        return jsonify({
            "success": True,
            "data": dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get dashboard {dashboard_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/charts", methods=["POST"])
@has_access_api
def create_chart():
    """Create new chart."""
    try:
        data = request.get_json()
        
        success, slice_obj, error = dashboard_service.create_chart(
            dashboard_id=data.get("dashboard_id"),
            chart_config=data.get("chart_config", {})
        )
        
        if success:
            return jsonify({
                "success": True,
                "data": {
                    "id": slice_obj.id,
                    "name": slice_obj.slice_name,
                    "viz_type": slice_obj.viz_type
                }
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": error
            }), 400
            
    except Exception as e:
        logger.error(f"Failed to create chart: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/netsuite/connections", methods=["GET"])
@has_access_api
def get_netsuite_connections():
    """Get NetSuite connections."""
    try:
        connections = NetSuiteConnection.query.filter_by(is_active=True).all()
        schema = NetSuiteConnectionSchema(many=True)
        
        return jsonify({
            "success": True,
            "data": schema.dump(connections)
        })
        
    except Exception as e:
        logger.error(f"Failed to get NetSuite connections: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/netsuite/connections/<int:connection_id>/test", methods=["POST"])
@has_access_api
def test_netsuite_connection(connection_id: int):
    """Test NetSuite connection."""
    try:
        success, error = netsuite_service.test_connection(connection_id)
        
        return jsonify({
            "success": success,
            "error": error
        })
        
    except Exception as e:
        logger.error(f"Failed to test NetSuite connection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/netsuite/queries/<int:query_id>/execute", methods=["POST"])
@has_access_api
def execute_netsuite_query(query_id: int):
    """Execute NetSuite query."""
    try:
        success, df, error = netsuite_service.execute_query(query_id)
        
        if success:
            return jsonify({
                "success": True,
                "data": df.to_dict("records") if df is not None else [],
                "rowcount": len(df) if df is not None else 0
            })
        else:
            return jsonify({
                "success": False,
                "error": error
            }), 400
            
    except Exception as e:
        logger.error(f"Failed to execute NetSuite query: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/sql/execute", methods=["POST"])
@has_access_api
def execute_sql():
    """Execute SQL query."""
    try:
        data = request.get_json()
        database_id = data.get("database_id")
        sql = data.get("sql")
        limit = data.get("limit", 1000)
        
        success, df, error = data_service.execute_sql(database_id, sql, limit)
        
        if success:
            return jsonify({
                "success": True,
                "data": df.to_dict("records") if df is not None else [],
                "columns": list(df.columns) if df is not None else [],
                "rowcount": len(df) if df is not None else 0
            })
        else:
            return jsonify({
                "success": False,
                "error": error
            }), 400
            
    except Exception as e:
        logger.error(f"Failed to execute SQL: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
