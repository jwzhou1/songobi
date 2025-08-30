# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
NetSuite integration views for Songo BI.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request, current_app
from flask_appbuilder.security.decorators import has_access_api

from songo_bi.extensions import db
from songo_bi.models.netsuite import (
    NetSuiteConnection, NetSuiteDataSource, NetSuiteQuery, NetSuiteRefreshLog
)
from songo_bi.services.netsuite import NetSuiteService

logger = logging.getLogger(__name__)

# Create blueprint
netsuite_bp = Blueprint("netsuite", __name__)

# Initialize NetSuite service
netsuite_service = NetSuiteService()


@netsuite_bp.route("/connections", methods=["POST"])
@has_access_api
def create_connection():
    """Create NetSuite connection."""
    try:
        data = request.get_json()
        
        connection = NetSuiteConnection(
            name=data.get("name"),
            account_id=data.get("account_id"),
            consumer_key=data.get("consumer_key"),
            consumer_secret=data.get("consumer_secret"),
            token_id=data.get("token_id"),
            token_secret=data.get("token_secret"),
            description=data.get("description", ""),
            auto_refresh=data.get("auto_refresh", True),
            refresh_interval=data.get("refresh_interval", 1800)
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "id": connection.id,
                "name": connection.name,
                "account_id": connection.account_id
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create NetSuite connection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@netsuite_bp.route("/data-sources", methods=["POST"])
@has_access_api
def create_data_source():
    """Create NetSuite data source."""
    try:
        data = request.get_json()
        
        data_source = NetSuiteDataSource(
            name=data.get("name"),
            connection_id=data.get("connection_id"),
            record_type=data.get("record_type"),
            fields=data.get("fields", []),
            filters=data.get("filters", {}),
            auto_refresh=data.get("auto_refresh", True),
            cache_timeout=data.get("cache_timeout", 3600),
            max_records=data.get("max_records", 10000)
        )
        
        db.session.add(data_source)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "id": data_source.id,
                "name": data_source.name,
                "record_type": data_source.record_type
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create NetSuite data source: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@netsuite_bp.route("/data-sources/<int:data_source_id>/refresh", methods=["POST"])
@has_access_api
def refresh_data_source(data_source_id: int):
    """Refresh NetSuite data source."""
    try:
        success, error = netsuite_service.refresh_data_source(data_source_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Data source refresh initiated"
            })
        else:
            return jsonify({
                "success": False,
                "error": error
            }), 400
            
    except Exception as e:
        logger.error(f"Failed to refresh data source: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@netsuite_bp.route("/queries", methods=["POST"])
@has_access_api
def create_query():
    """Create NetSuite query."""
    try:
        data = request.get_json()
        
        query = NetSuiteQuery(
            name=data.get("name"),
            connection_id=data.get("connection_id"),
            data_source_id=data.get("data_source_id"),
            query_type=data.get("query_type"),
            query_config=data.get("query_config", {}),
            auto_execute=data.get("auto_execute", False),
            schedule_cron=data.get("schedule_cron")
        )
        
        db.session.add(query)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "id": query.id,
                "name": query.name,
                "query_type": query.query_type
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create NetSuite query: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@netsuite_bp.route("/connections/<int:connection_id>/schema", methods=["GET"])
@has_access_api
def get_schema(connection_id: int):
    """Get NetSuite schema information."""
    try:
        schema = netsuite_service.get_netsuite_schema(connection_id)
        
        return jsonify({
            "success": True,
            "data": schema
        })
        
    except Exception as e:
        logger.error(f"Failed to get NetSuite schema: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@netsuite_bp.route("/refresh-logs", methods=["GET"])
@has_access_api
def get_refresh_logs():
    """Get NetSuite refresh logs."""
    try:
        connection_id = request.args.get("connection_id", type=int)
        limit = request.args.get("limit", 50, type=int)
        
        query = NetSuiteRefreshLog.query
        
        if connection_id:
            query = query.filter_by(connection_id=connection_id)
        
        logs = query.order_by(NetSuiteRefreshLog.start_time.desc()).limit(limit).all()
        
        log_data = [
            {
                "id": log.id,
                "connection_id": log.connection_id,
                "query_id": log.query_id,
                "refresh_type": log.refresh_type,
                "status": log.status,
                "start_time": log.start_time.isoformat(),
                "end_time": log.end_time.isoformat() if log.end_time else None,
                "duration": log.duration,
                "records_processed": log.records_processed,
                "error_message": log.error_message
            }
            for log in logs
        ]
        
        return jsonify({
            "success": True,
            "data": log_data,
            "count": len(log_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get refresh logs: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@netsuite_bp.route("/data-sources", methods=["GET"])
@has_access_api
def get_data_sources():
    """Get NetSuite data sources."""
    try:
        connection_id = request.args.get("connection_id", type=int)
        
        query = NetSuiteDataSource.query
        
        if connection_id:
            query = query.filter_by(connection_id=connection_id)
        
        data_sources = query.all()
        
        data_source_data = [
            {
                "id": ds.id,
                "name": ds.name,
                "connection_id": ds.connection_id,
                "record_type": ds.record_type,
                "fields": ds.fields,
                "filters": ds.filters,
                "auto_refresh": ds.auto_refresh,
                "last_refresh": ds.last_refresh.isoformat() if ds.last_refresh else None,
                "refresh_status": ds.refresh_status,
                "refresh_error": ds.refresh_error
            }
            for ds in data_sources
        ]
        
        return jsonify({
            "success": True,
            "data": data_source_data,
            "count": len(data_source_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get data sources: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@netsuite_bp.route("/queries", methods=["GET"])
@has_access_api
def get_queries():
    """Get NetSuite queries."""
    try:
        connection_id = request.args.get("connection_id", type=int)
        data_source_id = request.args.get("data_source_id", type=int)
        
        query = NetSuiteQuery.query
        
        if connection_id:
            query = query.filter_by(connection_id=connection_id)
        
        if data_source_id:
            query = query.filter_by(data_source_id=data_source_id)
        
        queries = query.all()
        
        query_data = [
            {
                "id": q.id,
                "name": q.name,
                "connection_id": q.connection_id,
                "data_source_id": q.data_source_id,
                "query_type": q.query_type,
                "query_config": q.query_config,
                "is_active": q.is_active,
                "auto_execute": q.auto_execute,
                "last_execution": q.last_execution.isoformat() if q.last_execution else None,
                "execution_status": q.execution_status,
                "result_count": q.result_count,
                "execution_time": q.execution_time
            }
            for q in queries
        ]
        
        return jsonify({
            "success": True,
            "data": query_data,
            "count": len(query_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get NetSuite queries: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
