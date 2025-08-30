# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Core database models for Songo BI.
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


class User(Model, AuditMixin):
    """User model extending Flask-AppBuilder's User."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    active = Column(Boolean, default=True)
    
    # Additional Songo BI specific fields
    preferences = Column(JSON, default=dict)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    
    # Relationships
    dashboards = relationship("Dashboard", back_populates="owner")
    queries = relationship("Query", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Database(Model, AuditMixin):
    """Database connection model."""
    
    __tablename__ = "databases"
    
    id = Column(Integer, primary_key=True)
    database_name = Column(String(250), unique=True, nullable=False)
    sqlalchemy_uri = Column(String(1024), nullable=False)
    password = Column(String(1024))
    cache_timeout = Column(Integer)
    extra = Column(Text)
    expose_in_sqllab = Column(Boolean, default=True)
    allow_run_async = Column(Boolean, default=False)
    allow_csv_upload = Column(Boolean, default=False)
    allow_ctas = Column(Boolean, default=False)
    allow_cvas = Column(Boolean, default=False)
    allow_dml = Column(Boolean, default=False)
    force_ctas_schema = Column(String(250))
    
    # Relationships
    tables = relationship("Table", back_populates="database")
    queries = relationship("Query", back_populates="database")
    
    def __repr__(self):
        return f"<Database {self.database_name}>"


class Table(Model, AuditMixin):
    """Table model for database tables."""
    
    __tablename__ = "tables"
    
    id = Column(Integer, primary_key=True)
    table_name = Column(String(250), nullable=False)
    main_dttm_col = Column(String(250))
    default_endpoint = Column(Text)
    database_id = Column(Integer, ForeignKey("databases.id"), nullable=False)
    offset = Column(Integer, default=0)
    description = Column(Text)
    is_sqllab_view = Column(Boolean, default=False)
    cache_timeout = Column(Integer)
    schema = Column(String(255))
    sql = Column(Text)
    params = Column(Text)
    perm = Column(String(1000))
    filter_select_enabled = Column(Boolean, default=True)
    fetch_values_predicate = Column(String(1000))
    is_managed_externally = Column(Boolean, nullable=False, default=False)
    external_url = Column(Text)
    
    # Relationships
    database = relationship("Database", back_populates="tables")
    columns = relationship("Column", back_populates="table")
    slices = relationship("Slice", back_populates="datasource")
    
    def __repr__(self):
        return f"<Table {self.table_name}>"


class Column(Model, AuditMixin):
    """Column model for table columns."""
    
    __tablename__ = "table_columns"
    
    id = Column(Integer, primary_key=True)
    column_name = Column(String(255), nullable=False)
    verbose_name = Column(String(1024))
    is_dttm = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    type = Column(String(32))
    groupby = Column(Boolean, default=True)
    filterable = Column(Boolean, default=True)
    description = Column(Text)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    database_expression = Column(Text)
    python_date_format = Column(String(255))
    
    # Relationships
    table = relationship("Table", back_populates="columns")
    
    def __repr__(self):
        return f"<Column {self.column_name}>"


class Query(Model, AuditMixin):
    """SQL query model."""
    
    __tablename__ = "query"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(String(11), unique=True, nullable=False)
    database_id = Column(Integer, ForeignKey("databases.id"), nullable=False)
    tmp_table_name = Column(String(256))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(16), default="success")
    error_message = Column(Text)
    results_key = Column(String(64))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    sql = Column(Text)
    executed_sql = Column(Text)
    limit = Column(Integer)
    select_sql = Column(Text)
    progress = Column(Integer, default=0)
    rows = Column(Integer)
    select_as_cta = Column(Boolean)
    select_as_cta_used = Column(Boolean, default=False)
    
    # Relationships
    database = relationship("Database", back_populates="queries")
    user = relationship("User", back_populates="queries")
    
    def __repr__(self):
        return f"<Query {self.id}>"
