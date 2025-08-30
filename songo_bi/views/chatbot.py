# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Chatbot API views for Songo BI.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request, current_app
from flask_appbuilder.security.decorators import has_access_api

from songo_bi.extensions import db
from songo_bi.models.chatbot import ChatSession, ChatMessage, AIInsight
from songo_bi.services.chatbot import ChatbotService

logger = logging.getLogger(__name__)

# Create blueprint
chatbot_bp = Blueprint("chatbot", __name__)

# Initialize chatbot service
def get_chatbot_service():
    """Get chatbot service instance."""
    api_key = current_app.config.get("OPENAI_API_KEY")
    model = current_app.config.get("OPENAI_MODEL", "gpt-4")
    
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    
    return ChatbotService(api_key, model)


@chatbot_bp.route("/sessions", methods=["POST"])
@has_access_api
def create_chat_session():
    """Create new chat session."""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        context = data.get("context", {})
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID is required"
            }), 400
        
        chatbot_service = get_chatbot_service()
        session = chatbot_service.create_session(user_id, context)
        
        return jsonify({
            "success": True,
            "data": {
                "session_id": session.session_id,
                "id": session.id,
                "title": session.title,
                "started_at": session.started_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@chatbot_bp.route("/sessions/<int:session_id>/messages", methods=["POST"])
@has_access_api
def send_message(session_id: int):
    """Send message to chatbot."""
    try:
        data = request.get_json()
        message = data.get("message")
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        chatbot_service = get_chatbot_service()
        success, response, additional_data = chatbot_service.send_message(session_id, message)
        
        if success:
            return jsonify({
                "success": True,
                "data": {
                    "response": response,
                    "additional_data": additional_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": response
            }), 400
            
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@chatbot_bp.route("/sessions/<int:session_id>/messages", methods=["GET"])
@has_access_api
def get_messages(session_id: int):
    """Get chat session messages."""
    try:
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({
                "success": False,
                "error": "Session not found"
            }), 404
        
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        
        message_data = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "content_type": msg.content_type,
                "timestamp": msg.timestamp.isoformat(),
                "chart_config": msg.chart_config,
                "query_sql": msg.query_sql,
                "data_preview": msg.data_preview
            }
            for msg in messages
        ]
        
        return jsonify({
            "success": True,
            "data": message_data,
            "count": len(message_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@chatbot_bp.route("/sessions/<int:session_id>", methods=["GET"])
@has_access_api
def get_session(session_id: int):
    """Get chat session details."""
    try:
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({
                "success": False,
                "error": "Session not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": {
                "id": session.id,
                "session_id": session.session_id,
                "title": session.title,
                "description": session.description,
                "is_active": session.is_active,
                "started_at": session.started_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "context_data": session.context_data
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@chatbot_bp.route("/sessions", methods=["GET"])
@has_access_api
def get_user_sessions():
    """Get user's chat sessions."""
    try:
        user_id = request.args.get("user_id", type=int)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID is required"
            }), 400
        
        sessions = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.last_activity.desc()).all()
        
        session_data = [
            {
                "id": session.id,
                "session_id": session.session_id,
                "title": session.title,
                "is_active": session.is_active,
                "started_at": session.started_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
            for session in sessions
        ]
        
        return jsonify({
            "success": True,
            "data": session_data,
            "count": len(session_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@chatbot_bp.route("/insights", methods=["GET"])
@has_access_api
def get_ai_insights():
    """Get AI-generated insights."""
    try:
        session_id = request.args.get("session_id", type=int)
        insight_type = request.args.get("type")
        
        query = AIInsight.query
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        if insight_type:
            query = query.filter_by(insight_type=insight_type)
        
        insights = query.filter_by(status="active").order_by(AIInsight.generated_at.desc()).all()
        
        insight_data = [
            {
                "id": insight.id,
                "insight_type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "confidence_score": insight.confidence_score,
                "is_featured": insight.is_featured,
                "generated_at": insight.generated_at.isoformat(),
                "insight_data": insight.insight_data
            }
            for insight in insights
        ]
        
        return jsonify({
            "success": True,
            "data": insight_data,
            "count": len(insight_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get AI insights: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@chatbot_bp.route("/generate-dashboard", methods=["POST"])
@has_access_api
def generate_ai_dashboard():
    """Generate dashboard using AI."""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        prompt = data.get("prompt")
        data_sources = data.get("data_sources", [])
        
        if not all([user_id, prompt]):
            return jsonify({
                "success": False,
                "error": "User ID and prompt are required"
            }), 400
        
        success, dashboard, error = dashboard_service.generate_ai_dashboard(
            user_id=user_id,
            prompt=prompt,
            data_sources=data_sources
        )
        
        if success:
            return jsonify({
                "success": True,
                "data": {
                    "id": dashboard.id,
                    "title": dashboard.dashboard_title,
                    "description": dashboard.description,
                    "ai_generated": dashboard.ai_generated,
                    "ai_confidence": dashboard.ai_confidence
                }
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": error
            }), 400
            
    except Exception as e:
        logger.error(f"Failed to generate AI dashboard: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
