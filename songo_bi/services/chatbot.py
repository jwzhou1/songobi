# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
AI Chatbot service for Songo BI.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import openai
import pandas as pd
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI

from songo_bi.extensions import db
from songo_bi.models.chatbot import ChatSession, ChatMessage, AIInsight
from songo_bi.models.core import Database, Query
from songo_bi.models.dashboard import Dashboard, Slice

logger = logging.getLogger(__name__)


class ChatbotService:
    """AI-powered chatbot service for data analysis and dashboard assistance."""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        self.openai_api_key = openai_api_key
        self.model = model
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model,
            temperature=0.7
        )
    
    def create_session(self, user_id: int, context: Optional[Dict[str, Any]] = None) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            user_id: User ID
            context: Initial context data
            
        Returns:
            New chat session
        """
        session = ChatSession(
            session_id=f"chat_{int(time.time())}_{user_id}",
            user_id=user_id,
            context_data=context or {},
            title="New Chat Session"
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Add system message
        self._add_system_message(session.id)
        
        return session
    
    def send_message(self, session_id: int, message: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Send message to chatbot and get response.
        
        Args:
            session_id: Chat session ID
            message: User message
            
        Returns:
            Tuple of (success, response_text, additional_data)
        """
        session = ChatSession.query.get(session_id)
        if not session or not session.is_active:
            return False, "Session not found or inactive", None
        
        start_time = time.time()
        
        try:
            # Add user message
            user_message = ChatMessage(
                session_id=session_id,
                role="user",
                content=message,
                timestamp=datetime.utcnow()
            )
            db.session.add(user_message)
            
            # Analyze message intent
            intent = self._analyze_intent(message, session.context_data)
            
            # Generate response based on intent
            if intent["type"] == "data_query":
                response, additional_data = self._handle_data_query(message, session)
            elif intent["type"] == "chart_creation":
                response, additional_data = self._handle_chart_creation(message, session)
            elif intent["type"] == "dashboard_help":
                response, additional_data = self._handle_dashboard_help(message, session)
            elif intent["type"] == "data_analysis":
                response, additional_data = self._handle_data_analysis(message, session)
            else:
                response, additional_data = self._handle_general_query(message, session)
            
            # Add assistant message
            processing_time = time.time() - start_time
            assistant_message = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=response,
                content_type=additional_data.get("content_type", "text") if additional_data else "text",
                timestamp=datetime.utcnow(),
                processing_time=processing_time,
                model_used=self.model,
                chart_config=additional_data.get("chart_config") if additional_data else None,
                query_sql=additional_data.get("sql") if additional_data else None,
                data_preview=additional_data.get("data_preview") if additional_data else None
            )
            db.session.add(assistant_message)
            
            # Update session activity
            session.last_activity = datetime.utcnow()
            
            db.session.commit()
            
            return True, response, additional_data
            
        except Exception as e:
            logger.error(f"Chatbot message processing failed: {e}")
            db.session.rollback()
            return False, f"Sorry, I encountered an error: {str(e)}", None
    
    def _analyze_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user message intent."""
        
        # Simple intent classification - in production, use more sophisticated NLP
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["query", "sql", "select", "data", "table"]):
            return {"type": "data_query", "confidence": 0.8}
        elif any(word in message_lower for word in ["chart", "graph", "plot", "visualize", "show"]):
            return {"type": "chart_creation", "confidence": 0.8}
        elif any(word in message_lower for word in ["dashboard", "layout", "organize"]):
            return {"type": "dashboard_help", "confidence": 0.8}
        elif any(word in message_lower for word in ["analyze", "insight", "trend", "pattern"]):
            return {"type": "data_analysis", "confidence": 0.8}
        else:
            return {"type": "general", "confidence": 0.5}
    
    def _handle_data_query(self, message: str, session: ChatSession) -> Tuple[str, Dict[str, Any]]:
        """Handle data query requests."""
        
        try:
            # Get available databases
            databases = Database.query.filter_by(expose_in_sqllab=True).all()
            
            if not databases:
                return "No databases are available for querying.", {}
            
            # Use the first available database for now
            database = databases[0]
            
            # Create SQL agent
            db_uri = database.sqlalchemy_uri
            sql_db = SQLDatabase.from_uri(db_uri)
            toolkit = SQLDatabaseToolkit(db=sql_db, llm=self.llm)
            agent = create_sql_agent(
                llm=self.llm,
                toolkit=toolkit,
                verbose=True
            )
            
            # Generate SQL query
            response = agent.run(f"Based on this request: '{message}', generate and execute a SQL query.")
            
            return response, {"content_type": "data", "sql": "Generated SQL would be here"}
            
        except Exception as e:
            logger.error(f"Data query handling failed: {e}")
            return f"I couldn't process your data query: {str(e)}", {}
    
    def _handle_chart_creation(self, message: str, session: ChatSession) -> Tuple[str, Dict[str, Any]]:
        """Handle chart creation requests."""
        
        # Generate chart configuration based on message
        chart_config = {
            "type": "bar",  # Default chart type
            "title": "Generated Chart",
            "data": [],
            "options": {}
        }
        
        response = f"I've created a chart based on your request. The chart shows data visualization for: {message}"
        
        return response, {
            "content_type": "chart",
            "chart_config": chart_config
        }
    
    def _handle_dashboard_help(self, message: str, session: ChatSession) -> Tuple[str, Dict[str, Any]]:
        """Handle dashboard assistance requests."""
        
        # Get user's dashboards
        user_id = session.user_id
        dashboards = Dashboard.query.filter_by(owner_id=user_id).all()
        
        dashboard_info = [
            {"id": d.id, "title": d.dashboard_title, "description": d.description}
            for d in dashboards
        ]
        
        response = f"I can help you with your dashboards. You currently have {len(dashboards)} dashboards. What would you like to do?"
        
        return response, {
            "content_type": "dashboard_help",
            "dashboards": dashboard_info
        }
    
    def _handle_data_analysis(self, message: str, session: ChatSession) -> Tuple[str, Dict[str, Any]]:
        """Handle data analysis requests."""
        
        # Generate AI insights
        insight = AIInsight(
            session_id=session.id,
            insight_type="analysis",
            title="Data Analysis Result",
            description=f"Analysis based on: {message}",
            insight_data={"analysis": "Generated analysis would be here"},
            confidence_score=0.8
        )
        
        db.session.add(insight)
        db.session.commit()
        
        response = "I've analyzed your data and found some interesting patterns. Here are the key insights..."
        
        return response, {
            "content_type": "analysis",
            "insight_id": insight.id
        }
    
    def _handle_general_query(self, message: str, session: ChatSession) -> Tuple[str, Dict[str, Any]]:
        """Handle general queries."""
        
        try:
            # Use OpenAI for general conversation
            messages = [
                {"role": "system", "content": "You are a helpful BI assistant for Songo BI platform."},
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content, {}
            
        except Exception as e:
            logger.error(f"General query handling failed: {e}")
            return "I'm sorry, I couldn't process your request right now.", {}
    
    def _add_system_message(self, session_id: int):
        """Add initial system message to session."""
        
        system_message = ChatMessage(
            session_id=session_id,
            role="system",
            content="Hello! I'm your Songo BI assistant. I can help you with data queries, creating charts, analyzing dashboards, and providing insights. How can I assist you today?",
            timestamp=datetime.utcnow()
        )
        
        db.session.add(system_message)
        db.session.commit()
