# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
NetSuite integration models for Songo BI.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.orm import relationship

from songo_bi.extensions import db


class NetSuiteConnection(Model, AuditMixin):
    """NetSuite connection configuration."""
    
    __tablename__ = "netsuite_connections"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    account_id = Column(String(100), nullable=False)
    consumer_key = Column(String(500), nullable=False)
    consumer_secret = Column(String(500), nullable=False)
    token_id = Column(String(500), nullable=False)
    token_secret = Column(String(500), nullable=False)
    
    # Connection settings
    is_active = Column(Boolean, default=True)
    auto_refresh = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=1800)  # 30 minutes
    timeout = Column(Integer, default=60)
    
    # Additional configuration
    extra_config = Column(JSON, default=dict)
    description = Column(Text)
    
    # Relationships
    data_sources = relationship("NetSuiteDataSource", back_populates="connection")
    queries = relationship("NetSuiteQuery", back_populates="connection")
    refresh_logs = relationship("NetSuiteRefreshLog", back_populates="connection")
    
    def __repr__(self):
        return f"<NetSuiteConnection {self.name}>"
    
    @property
    def connection_config(self) -> Dict[str, Any]:
        """Get connection configuration dictionary."""
        return {
            "account_id": self.account_id,
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
            "token_id": self.token_id,
            "token_secret": self.token_secret,
            "timeout": self.timeout,
            **self.extra_config
        }


class NetSuiteDataSource(Model, AuditMixin):
    """NetSuite data source configuration."""
    
    __tablename__ = "netsuite_data_sources"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    connection_id = Column(Integer, ForeignKey("netsuite_connections.id"), nullable=False)
    
    # Data source configuration
    record_type = Column(String(100), nullable=False)  # e.g., 'customer', 'transaction', 'item'
    fields = Column(JSON, default=list)  # List of fields to retrieve
    filters = Column(JSON, default=dict)  # NetSuite search filters
    
    # Refresh settings
    auto_refresh = Column(Boolean, default=True)
    last_refresh = Column(DateTime)
    refresh_status = Column(String(50), default="pending")
    refresh_error = Column(Text)
    
    # Data settings
    cache_timeout = Column(Integer, default=3600)
    max_records = Column(Integer, default=10000)
    
    # Relationships
    connection = relationship("NetSuiteConnection", back_populates="data_sources")
    queries = relationship("NetSuiteQuery", back_populates="data_source")
    
    def __repr__(self):
        return f"<NetSuiteDataSource {self.name}>"


class NetSuiteQuery(Model, AuditMixin):
    """NetSuite query configuration and results."""
    
    __tablename__ = "netsuite_queries"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    connection_id = Column(Integer, ForeignKey("netsuite_connections.id"), nullable=False)
    data_source_id = Column(Integer, ForeignKey("netsuite_data_sources.id"))
    
    # Query configuration
    query_type = Column(String(50), nullable=False)  # 'search', 'saved_search', 'custom'
    query_config = Column(JSON, nullable=False)
    
    # Execution settings
    is_active = Column(Boolean, default=True)
    auto_execute = Column(Boolean, default=False)
    schedule_cron = Column(String(100))  # Cron expression for scheduling
    
    # Results metadata
    last_execution = Column(DateTime)
    execution_status = Column(String(50), default="pending")
    execution_error = Column(Text)
    result_count = Column(Integer, default=0)
    execution_time = Column(Integer)  # milliseconds
    
    # Data storage
    result_data = Column(JSON)  # Store small result sets directly
    result_file_path = Column(String(500))  # Path to larger result files
    
    # Relationships
    connection = relationship("NetSuiteConnection", back_populates="queries")
    data_source = relationship("NetSuiteDataSource", back_populates="queries")
    refresh_logs = relationship("NetSuiteRefreshLog", back_populates="query")
    
    def __repr__(self):
        return f"<NetSuiteQuery {self.name}>"


class NetSuiteRefreshLog(Model, AuditMixin):
    """Log of NetSuite data refresh operations."""
    
    __tablename__ = "netsuite_refresh_logs"
    
    id = Column(Integer, primary_key=True)
    connection_id = Column(Integer, ForeignKey("netsuite_connections.id"), nullable=False)
    query_id = Column(Integer, ForeignKey("netsuite_queries.id"))
    
    # Refresh details
    refresh_type = Column(String(50), nullable=False)  # 'manual', 'scheduled', 'auto'
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(50), default="running")  # 'running', 'success', 'failed'
    
    # Results
    records_processed = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_deleted = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Performance metrics
    execution_time = Column(Integer)  # milliseconds
    memory_usage = Column(Integer)  # bytes
    
    # Relationships
    connection = relationship("NetSuiteConnection", back_populates="refresh_logs")
    query = relationship("NetSuiteQuery", back_populates="refresh_logs")
    
    def __repr__(self):
        return f"<NetSuiteRefreshLog {self.id} - {self.status}>"
    
    @property
    def duration(self) -> Optional[int]:
        """Calculate refresh duration in seconds."""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None
