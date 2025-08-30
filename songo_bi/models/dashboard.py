# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Dashboard and visualization models for Songo BI.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON, Float
)
from sqlalchemy.orm import relationship

from songo_bi.extensions import db


class Dashboard(Model, AuditMixin):
    """Dashboard model for organizing charts and visualizations."""
    
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True)
    dashboard_title = Column(String(500), nullable=False)
    position_json = Column(Text)  # Layout configuration
    description = Column(Text)
    css = Column(Text)
    json_metadata = Column(Text)
    slug = Column(String(255), unique=True)
    
    # Ownership and permissions
    owner_id = Column(Integer, ForeignKey("users.id"))
    published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    # Dashboard settings
    auto_refresh_interval = Column(Integer)  # seconds
    cache_timeout = Column(Integer, default=3600)
    
    # AI integration
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)  # Original prompt if AI-generated
    ai_confidence = Column(Float)  # AI confidence score
    
    # Relationships
    owner = relationship("User", back_populates="dashboards")
    slices = relationship("Slice", secondary="dashboard_slices", back_populates="dashboards")
    
    def __repr__(self):
        return f"<Dashboard {self.dashboard_title}>"


class Slice(Model, AuditMixin):
    """Chart/slice model for individual visualizations."""
    
    __tablename__ = "slices"
    
    id = Column(Integer, primary_key=True)
    slice_name = Column(String(250), nullable=False)
    datasource_id = Column(Integer, ForeignKey("tables.id"))
    datasource_type = Column(String(200))
    datasource_name = Column(String(2000))
    viz_type = Column(String(250))
    params = Column(Text)
    description = Column(Text)
    cache_timeout = Column(Integer)
    perm = Column(String(2000))
    schema_perm = Column(String(1000))
    
    # Chart configuration
    query_context = Column(Text)  # Serialized query context
    form_data = Column(Text)  # Chart form configuration
    
    # AI integration
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)
    ai_suggestions = Column(JSON)  # AI suggestions for improvement
    
    # Relationships
    datasource = relationship("Table", back_populates="slices")
    dashboards = relationship("Dashboard", secondary="dashboard_slices", back_populates="slices")
    
    def __repr__(self):
        return f"<Slice {self.slice_name}>"


class Chart(Model, AuditMixin):
    """Enhanced chart model with additional Songo BI features."""
    
    __tablename__ = "charts"
    
    id = Column(Integer, primary_key=True)
    slice_id = Column(Integer, ForeignKey("slices.id"), nullable=False)
    
    # Chart metadata
    chart_type = Column(String(100), nullable=False)
    title = Column(String(250))
    subtitle = Column(String(500))
    
    # Visualization configuration
    viz_config = Column(JSON, nullable=False)
    color_scheme = Column(String(100))
    theme = Column(String(50), default="light")
    
    # Data configuration
    data_config = Column(JSON, nullable=False)
    refresh_frequency = Column(Integer)  # seconds
    last_refresh = Column(DateTime)
    
    # AI enhancements
    ai_insights = Column(JSON)  # AI-generated insights about the chart
    auto_insights = Column(Boolean, default=True)
    insight_last_generated = Column(DateTime)
    
    # Performance and caching
    render_time = Column(Float)  # milliseconds
    data_size = Column(Integer)  # bytes
    cache_key = Column(String(200))
    
    # Relationships
    slice = relationship("Slice")
    
    def __repr__(self):
        return f"<Chart {self.title or self.chart_type}>"


class Filter(Model, AuditMixin):
    """Dashboard and chart filter model."""
    
    __tablename__ = "filters"
    
    id = Column(Integer, primary_key=True)
    filter_name = Column(String(250), nullable=False)
    filter_type = Column(String(50), nullable=False)  # 'date', 'select', 'text', 'number'
    
    # Filter configuration
    config = Column(JSON, nullable=False)
    default_value = Column(Text)
    is_required = Column(Boolean, default=False)
    
    # Scope
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    slice_id = Column(Integer, ForeignKey("slices.id"))
    is_global = Column(Boolean, default=False)
    
    # Display settings
    display_order = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Filter {self.filter_name}>"


# Association table for dashboard-slice many-to-many relationship
dashboard_slices = db.Table(
    "dashboard_slices",
    Column("id", Integer, primary_key=True),
    Column("dashboard_id", Integer, ForeignKey("dashboards.id")),
    Column("slice_id", Integer, ForeignKey("slices.id")),
    Column("created_on", DateTime, default=datetime.utcnow),
    Column("changed_on", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)
