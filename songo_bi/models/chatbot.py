# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Chatbot and AI models for Songo BI.
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


class ChatSession(Model, AuditMixin):
    """Chat session model for tracking user conversations."""
    
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session metadata
    title = Column(String(250))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Session settings
    model_name = Column(String(100), default="gpt-4")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    
    # Context and state
    context_data = Column(JSON, default=dict)  # Dashboard context, data context, etc.
    session_state = Column(JSON, default=dict)  # Current conversation state
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    insights = relationship("AIInsight", back_populates="session")
    
    def __repr__(self):
        return f"<ChatSession {self.session_id}>"


class ChatMessage(Model, AuditMixin):
    """Individual chat message model."""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # 'text', 'chart', 'data', 'error'
    
    # Message metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    token_count = Column(Integer)
    processing_time = Column(Float)  # seconds
    
    # AI response metadata
    model_used = Column(String(100))
    temperature_used = Column(Float)
    finish_reason = Column(String(50))
    
    # Associated data
    chart_config = Column(JSON)  # Chart configuration if message generated a chart
    query_sql = Column(Text)  # SQL query if message involved data querying
    data_preview = Column(JSON)  # Preview of data results
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.role}>"


class ChatContext(Model, AuditMixin):
    """Context information for chat sessions."""
    
    __tablename__ = "chat_contexts"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Context type and data
    context_type = Column(String(50), nullable=False)  # 'dashboard', 'chart', 'data', 'query'
    context_id = Column(String(100))  # ID of the referenced object
    context_data = Column(JSON, nullable=False)
    
    # Context metadata
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority contexts are more relevant
    
    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    def __repr__(self):
        return f"<ChatContext {self.context_type}:{self.context_id}>"


class AIInsight(Model, AuditMixin):
    """AI-generated insights and recommendations."""
    
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    
    # Insight metadata
    insight_type = Column(String(50), nullable=False)  # 'trend', 'anomaly', 'recommendation', 'summary'
    title = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    
    # Insight data
    data_source = Column(String(100))  # Source of the data analyzed
    analysis_config = Column(JSON)  # Configuration used for analysis
    insight_data = Column(JSON, nullable=False)  # The actual insight data
    confidence_score = Column(Float)  # AI confidence in the insight (0-1)
    
    # Status and lifecycle
    status = Column(String(50), default="active")  # 'active', 'dismissed', 'acted_upon'
    is_featured = Column(Boolean, default=False)  # Whether to highlight this insight
    
    # User interaction
    user_feedback = Column(String(20))  # 'helpful', 'not_helpful', 'irrelevant'
    user_notes = Column(Text)
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # When this insight becomes stale
    
    # Relationships
    session = relationship("ChatSession", back_populates="insights")
    
    def __repr__(self):
        return f"<AIInsight {self.insight_type}: {self.title}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the insight has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
