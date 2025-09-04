#!/usr/bin/env python3
"""
Enhanced Songo BI - Power BI capabilities with Metabase UI and LLM integration
"""

import os
import json
import random
import openai
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songo_bi_enhanced.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# OpenAI Configuration
openai.api_key = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key-here')

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Enhanced Models with Power BI-like capabilities
class People(db.Model):
    """Enhanced customer model with analytics fields."""
    __tablename__ = 'people'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    birth_date = db.Column(db.Date)
    source = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Power BI-like calculated fields
    @property
    def age(self):
        if self.birth_date:
            return (datetime.now().date() - self.birth_date).days // 365
        return None
    
    @property
    def customer_lifetime_value(self):
        total = db.session.query(func.sum(Orders.total)).filter(Orders.user_id == self.id).scalar()
        return total or 0.0
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'city': self.city,
            'state': self.state,
            'source': self.source,
            'age': self.age,
            'customer_lifetime_value': self.customer_lifetime_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Products(db.Model):
    """Enhanced product model with analytics."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    vendor = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total_sales(self):
        total = db.session.query(func.sum(Orders.total)).filter(Orders.product_id == self.id).scalar()
        return total or 0.0
    
    @property
    def units_sold(self):
        units = db.session.query(func.sum(Orders.quantity)).filter(Orders.product_id == self.id).scalar()
        return units or 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'vendor': self.vendor,
            'price': self.price,
            'rating': self.rating,
            'total_sales': self.total_sales,
            'units_sold': self.units_sold
        }

class Orders(db.Model):
    """Enhanced orders model."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('People', backref='orders')
    product = db.relationship('Products', backref='orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else None,
            'quantity': self.quantity,
            'total': self.total,
            'discount': self.discount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Reviews(db.Model):
    """Product reviews model."""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    reviewer = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Products', backref='reviews')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else None,
            'reviewer': self.reviewer,
            'rating': self.rating,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# LLM Service for Natural Language to SQL
class LLMService:
    """LLM service for natural language processing."""
    
    @staticmethod
    def get_database_schema():
        """Get database schema for LLM context."""
        schema = {
            "people": {
                "description": "Customer information table",
                "columns": ["id", "name", "email", "city", "state", "source", "birth_date", "created_at"],
                "sample_data": "Contains customer demographics and acquisition data"
            },
            "products": {
                "description": "Product catalog table", 
                "columns": ["id", "title", "category", "vendor", "price", "rating", "created_at"],
                "sample_data": "Contains product information, pricing, and ratings"
            },
            "orders": {
                "description": "Sales transactions table",
                "columns": ["id", "user_id", "product_id", "quantity", "total", "discount", "tax", "created_at"],
                "sample_data": "Contains all sales transactions and order details"
            },
            "reviews": {
                "description": "Product reviews and ratings",
                "columns": ["id", "product_id", "reviewer", "rating", "body", "created_at"],
                "sample_data": "Contains customer reviews and product ratings"
            }
        }
        return schema
    
    @staticmethod
    def natural_language_to_sql(question: str) -> dict:
        """Convert natural language question to SQL query."""
        schema = LLMService.get_database_schema()
        
        prompt = f"""
You are a SQL expert. Convert the following natural language question into a SQL query.

Database Schema:
{json.dumps(schema, indent=2)}

Question: {question}

Please provide:
1. A SQL query that answers the question
2. A brief explanation of what the query does
3. The expected result format

Respond in JSON format:
{{
    "sql": "SELECT ...",
    "explanation": "This query...",
    "result_type": "table|chart|metric"
}}
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            return {
                "sql": "SELECT 'Error generating SQL' as message",
                "explanation": f"Error: {str(e)}",
                "result_type": "error"
            }
    
    @staticmethod
    def generate_insights(data: dict) -> str:
        """Generate AI insights from data."""
        prompt = f"""
Analyze the following business data and provide 3-5 key insights:

Data Summary:
{json.dumps(data, indent=2)}

Please provide actionable business insights in a clear, concise format.
Focus on trends, opportunities, and recommendations.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"AI insights temporarily unavailable: {str(e)}"

# Dashboard and BI Models
class Dashboard(db.Model):
    """Enhanced dashboard model."""
    __tablename__ = 'dashboards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    config = db.Column(db.JSON, default=dict)  # Store dashboard configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'config': self.config,
            'created_at': self.created_at.isoformat()
        }

class DataSource(db.Model):
    """Enhanced data source model."""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    connection_string = db.Column(db.String(500))
    source_type = db.Column(db.String(50), default='database')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'created_at': self.created_at.isoformat()
        }

# Enhanced HTML Template with Power BI + Metabase UI (moved to top)
ENHANCED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Songo BI - Advanced Business Intelligence Platform</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8fafc;
            color: #2d3748;
            line-height: 1.6;
        }

        /* Power BI-inspired Navigation */
        .navbar {
            background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar h1 {
            font-size: 1.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .navbar-actions {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        .nav-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .nav-btn:hover {
            background: rgba(255,255,255,0.3);
        }

        /* Main Layout */
        .main-container {
            display: grid;
            grid-template-columns: 250px 1fr;
            min-height: calc(100vh - 80px);
        }

        /* Sidebar */
        .sidebar {
            background: white;
            border-right: 1px solid #e2e8f0;
            padding: 1.5rem;
            overflow-y: auto;
        }
        .sidebar-section {
            margin-bottom: 2rem;
        }
        .sidebar-title {
            font-weight: 600;
            color: #374151;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .sidebar-item {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .sidebar-item:hover {
            background: #f1f5f9;
        }
        .sidebar-item.active {
            background: #dbeafe;
            color: #1d4ed8;
            font-weight: 500;
        }

        /* Content Area */
        .content {
            padding: 2rem;
            overflow-y: auto;
        }

        /* Metric Cards */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        /* Dashboard Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        /* Chart Containers */
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
        }
        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #f1f5f9;
        }
        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a202c;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .chart-canvas {
            position: relative;
            height: 300px;
            margin: 1rem 0;
        }

        /* Buttons */
        .btn {
            background: #0078d4;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn:hover {
            background: #106ebe;
            transform: translateY(-1px);
        }
        .btn-secondary {
            background: #6b7280;
        }
        .btn-secondary:hover {
            background: #4b5563;
        }
        .btn-ai {
            background: #7c3aed;
        }
        .btn-ai:hover {
            background: #6d28d9;
        }

        /* Chart Builder Styles */
        .chart-type-btn {
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.8rem;
        }
        .chart-type-btn:hover {
            border-color: #0078d4;
            background: #f0f9ff;
        }
        .chart-type-btn.active {
            border-color: #0078d4;
            background: #dbeafe;
            color: #1d4ed8;
        }

        /* Import Data Styles */
        .upload-area {
            border: 2px dashed #d1d5db;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.2s;
            cursor: pointer;
        }
        .upload-area:hover {
            border-color: #0078d4;
            background: #f8fafc;
        }
        .upload-area.dragover {
            border-color: #0078d4;
            background: #dbeafe;
        }

        /* Dashboard Tabs */
        .dashboard-tabs {
            display: flex;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 2rem;
            overflow-x: auto;
        }
        .dashboard-tab {
            padding: 1rem 2rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .dashboard-tab:hover {
            background: #f8fafc;
        }
        .dashboard-tab.active {
            border-bottom-color: #0078d4;
            color: #0078d4;
            font-weight: 600;
        }

        /* Modal Styles */
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }
        .modal.show {
            display: flex;
        }
        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6b7280;
        }
        .modal-close:hover {
            color: #374151;
        }

        /* Form Styles */
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #374151;
        }
        .form-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 1rem;
        }
        .form-input:focus {
            outline: none;
            border-color: #0078d4;
            box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.1);
        }
        .form-select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: white;
            font-size: 1rem;
        }

        /* Data Table Enhancements */
        .data-table-container {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .data-table-header {
            background: #f8fafc;
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .data-table-actions {
            display: flex;
            gap: 0.5rem;
        }

        /* Responsive Design */
        @media (max-width: 1024px) {
            .main-container {
                grid-template-columns: 200px 1fr;
            }
            .sidebar {
                padding: 1rem;
            }
        }

        @media (max-width: 768px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            .sidebar {
                display: none;
            }
            .navbar {
                padding: 1rem;
            }
            .navbar h1 {
                font-size: 1.5rem;
            }
            .navbar-actions {
                gap: 0.5rem;
            }
            .nav-btn {
                padding: 0.5rem;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div>
            <h1><i class="fas fa-chart-line"></i> Songo BI Enhanced</h1>
        </div>
        <div class="navbar-actions">
            <button class="nav-btn" onclick="refreshAllData()">
                <i class="fas fa-sync-alt"></i> Refresh
            </button>
            <button class="nav-btn" onclick="exportDashboard()">
                <i class="fas fa-download"></i> Export
            </button>
            <button class="nav-btn" onclick="toggleAIChat()">
                <i class="fas fa-robot"></i> AI Assistant
            </button>
        </div>
    </nav>

    <div class="main-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <!-- Dashboard Section -->
            <div class="sidebar-section">
                <div class="sidebar-title">📊 Dashboards</div>
                <div class="sidebar-item active" onclick="showDashboard('main')">
                    <i class="fas fa-tachometer-alt"></i> Main Dashboard
                </div>
                <div class="sidebar-item" onclick="showDashboard('sales')">
                    <i class="fas fa-chart-line"></i> Sales Analytics
                </div>
                <div class="sidebar-item" onclick="showDashboard('customers')">
                    <i class="fas fa-users"></i> Customer Insights
                </div>
                <div class="sidebar-item" onclick="showDashboard('products')">
                    <i class="fas fa-box"></i> Product Performance
                </div>
                <div class="sidebar-item" onclick="showDashboard('financial')">
                    <i class="fas fa-dollar-sign"></i> Financial Overview
                </div>
                <div class="sidebar-item" onclick="createNewDashboard()">
                    <i class="fas fa-plus"></i> New Dashboard
                </div>
            </div>

            <!-- Data Section -->
            <div class="sidebar-section">
                <div class="sidebar-title">💾 Data</div>
                <div class="sidebar-item" onclick="showView('data-sources')">
                    <i class="fas fa-database"></i> Data Sources
                </div>
                <div class="sidebar-item" onclick="showView('import-data')">
                    <i class="fas fa-upload"></i> Import Data
                </div>
                <div class="sidebar-item" onclick="showView('data-explorer')">
                    <i class="fas fa-search"></i> Browse Data
                </div>
            </div>

            <!-- Analytics Tools -->
            <div class="sidebar-section">
                <div class="sidebar-title">🔧 Analytics Tools</div>
                <div class="sidebar-item" onclick="showView('chart-builder')">
                    <i class="fas fa-chart-bar"></i> Chart Builder
                </div>
                <div class="sidebar-item" onclick="showView('sql-lab')">
                    <i class="fas fa-code"></i> SQL Lab
                </div>
                <div class="sidebar-item" onclick="showView('natural-query')">
                    <i class="fas fa-comments"></i> Ask Questions
                </div>
            </div>

            <!-- AI Features -->
            <div class="sidebar-section">
                <div class="sidebar-title">🤖 AI Assistant</div>
                <div class="sidebar-item" onclick="showView('ai-insights')">
                    <i class="fas fa-brain"></i> AI Insights
                </div>
                <div class="sidebar-item" onclick="toggleAIChat()">
                    <i class="fas fa-robot"></i> Chat Assistant
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="content">
            <!-- Overview Dashboard -->
            <div id="overview-view" class="view-content">
                <!-- Key Metrics -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value" id="total-revenue">Loading...</div>
                        <div class="metric-label"><i class="fas fa-dollar-sign"></i> Total Revenue</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="total-orders">Loading...</div>
                        <div class="metric-label"><i class="fas fa-shopping-cart"></i> Total Orders</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="total-customers">Loading...</div>
                        <div class="metric-label"><i class="fas fa-users"></i> Total Customers</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="avg-order-value">Loading...</div>
                        <div class="metric-label"><i class="fas fa-chart-bar"></i> Avg Order Value</div>
                    </div>
                </div>

                <!-- Charts Grid -->
                <div class="dashboard-grid">
                    <!-- Monthly Revenue Trend -->
                    <div class="chart-container" style="grid-column: span 2;">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-chart-line"></i> Monthly Revenue Trend
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('monthly-revenue')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="monthly-revenue-chart"></canvas>
                        </div>
                    </div>

                    <!-- Sales by Category -->
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-pie-chart"></i> Sales by Category
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('category-sales')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="category-sales-chart"></canvas>
                        </div>
                    </div>

                    <!-- Customer Acquisition -->
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-user-plus"></i> Customer Sources
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('customer-sources')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="customer-sources-chart"></canvas>
                        </div>
                    </div>

                    <!-- Top Products -->
                    <div class="chart-container" style="grid-column: span 2;">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-trophy"></i> Top Selling Products
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('top-products')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="top-products-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI Insights View -->
            <div id="ai-insights-view" class="view-content" style="display: none;">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">
                            <i class="fas fa-brain"></i> AI-Generated Business Insights
                        </h3>
                        <button class="btn btn-ai" onclick="generateInsights()">
                            <i class="fas fa-magic"></i> Generate New Insights
                        </button>
                    </div>
                    <div id="ai-insights-content">
                        <div style="text-align: center; padding: 3rem; color: #6b7280;">
                            <i class="fas fa-brain" style="font-size: 3rem; margin-bottom: 1rem; color: #7c3aed;"></i>
                            <h3>AI Business Intelligence</h3>
                            <p>Click "Generate New Insights" to get AI-powered analysis of your business data</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Import Data View -->
            <div id="import-data-view" class="view-content" style="display: none;">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">
                            <i class="fas fa-upload"></i> Import Data
                        </h3>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem;">
                        <!-- CSV Upload -->
                        <div style="border: 2px dashed #d1d5db; border-radius: 12px; padding: 2rem; text-align: center; transition: all 0.2s;"
                             onmouseover="this.style.borderColor='#0078d4'" onmouseout="this.style.borderColor='#d1d5db'">
                            <i class="fas fa-file-csv" style="font-size: 3rem; color: #059669; margin-bottom: 1rem;"></i>
                            <h4>Upload CSV File</h4>
                            <p style="color: #6b7280; margin: 1rem 0;">Drag and drop your CSV file or click to browse</p>
                            <input type="file" id="csv-upload" accept=".csv" style="display: none;" onchange="handleCSVUpload(event)">
                            <button class="btn" onclick="document.getElementById('csv-upload').click()">
                                <i class="fas fa-upload"></i> Choose File
                            </button>
                        </div>

                        <!-- Database Connection -->
                        <div style="border: 2px dashed #d1d5db; border-radius: 12px; padding: 2rem; text-align: center; transition: all 0.2s;"
                             onmouseover="this.style.borderColor='#0078d4'" onmouseout="this.style.borderColor='#d1d5db'">
                            <i class="fas fa-database" style="font-size: 3rem; color: #7c3aed; margin-bottom: 1rem;"></i>
                            <h4>Connect Database</h4>
                            <p style="color: #6b7280; margin: 1rem 0;">Connect to MySQL, PostgreSQL, SQL Server, etc.</p>
                            <button class="btn btn-secondary" onclick="showDatabaseConnectionModal()">
                                <i class="fas fa-plug"></i> Add Connection
                            </button>
                        </div>

                        <!-- API Integration -->
                        <div style="border: 2px dashed #d1d5db; border-radius: 12px; padding: 2rem; text-align: center; transition: all 0.2s;"
                             onmouseover="this.style.borderColor='#0078d4'" onmouseout="this.style.borderColor='#d1d5db'">
                            <i class="fas fa-cloud" style="font-size: 3rem; color: #dc2626; margin-bottom: 1rem;"></i>
                            <h4>API Integration</h4>
                            <p style="color: #6b7280; margin: 1rem 0;">Connect to REST APIs, Google Sheets, etc.</p>
                            <button class="btn btn-secondary" onclick="showAPIConnectionModal()">
                                <i class="fas fa-link"></i> Add API
                            </button>
                        </div>
                    </div>

                    <!-- Recent Imports -->
                    <div style="margin-top: 3rem;">
                        <h4 style="margin-bottom: 1rem;"><i class="fas fa-history"></i> Recent Imports</h4>
                        <div id="recent-imports" style="background: #f8fafc; padding: 1rem; border-radius: 8px;">
                            <p style="color: #6b7280; text-align: center;">No recent imports</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chart Builder View -->
            <div id="chart-builder-view" class="view-content" style="display: none;">
                <div style="display: grid; grid-template-columns: 300px 1fr; gap: 1rem; height: calc(100vh - 200px);">
                    <!-- Chart Builder Sidebar -->
                    <div style="background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0; overflow-y: auto;">
                        <h4 style="margin-bottom: 1rem;"><i class="fas fa-chart-bar"></i> Chart Builder</h4>

                        <!-- Data Source Selection -->
                        <div style="margin-bottom: 2rem;">
                            <label style="display: block; font-weight: 600; margin-bottom: 0.5rem;">Data Source</label>
                            <select id="chart-data-source" style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 6px;">
                                <option value="orders">Orders</option>
                                <option value="products">Products</option>
                                <option value="people">Customers</option>
                                <option value="reviews">Reviews</option>
                            </select>
                        </div>

                        <!-- Chart Type Selection -->
                        <div style="margin-bottom: 2rem;">
                            <label style="display: block; font-weight: 600; margin-bottom: 0.5rem;">Chart Type</label>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
                                <button class="chart-type-btn active" data-type="bar" onclick="selectChartType('bar')">
                                    <i class="fas fa-chart-bar"></i> Bar
                                </button>
                                <button class="chart-type-btn" data-type="line" onclick="selectChartType('line')">
                                    <i class="fas fa-chart-line"></i> Line
                                </button>
                                <button class="chart-type-btn" data-type="pie" onclick="selectChartType('pie')">
                                    <i class="fas fa-chart-pie"></i> Pie
                                </button>
                                <button class="chart-type-btn" data-type="area" onclick="selectChartType('area')">
                                    <i class="fas fa-chart-area"></i> Area
                                </button>
                            </div>
                        </div>

                        <!-- Field Selection -->
                        <div style="margin-bottom: 2rem;">
                            <label style="display: block; font-weight: 600; margin-bottom: 0.5rem;">X-Axis</label>
                            <select id="chart-x-axis" style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 6px;">
                                <option value="created_at">Date</option>
                                <option value="category">Category</option>
                                <option value="state">State</option>
                            </select>
                        </div>

                        <div style="margin-bottom: 2rem;">
                            <label style="display: block; font-weight: 600; margin-bottom: 0.5rem;">Y-Axis</label>
                            <select id="chart-y-axis" style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 6px;">
                                <option value="total">Total Revenue</option>
                                <option value="count">Count</option>
                                <option value="quantity">Quantity</option>
                            </select>
                        </div>

                        <!-- Actions -->
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            <button class="btn" onclick="buildChart()">
                                <i class="fas fa-play"></i> Build Chart
                            </button>
                            <button class="btn btn-secondary" onclick="saveChart()">
                                <i class="fas fa-save"></i> Save Chart
                            </button>
                        </div>
                    </div>

                    <!-- Chart Preview Area -->
                    <div style="background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0;">
                        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
                            <h4><i class="fas fa-eye"></i> Chart Preview</h4>
                            <button class="btn btn-secondary" onclick="addChartToDashboard()">
                                <i class="fas fa-plus"></i> Add to Dashboard
                            </button>
                        </div>
                        <div style="height: 400px; display: flex; align-items: center; justify-content: center; border: 2px dashed #e2e8f0; border-radius: 8px;">
                            <canvas id="chart-builder-canvas" style="max-width: 100%; max-height: 100%;"></canvas>
                            <div id="chart-placeholder" style="color: #6b7280; text-align: center;">
                                <i class="fas fa-chart-bar" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                                <p>Select data and chart type to build your visualization</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Natural Language Query View -->
            <div id="natural-query-view" class="view-content" style="display: none;">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">
                            <i class="fas fa-comments"></i> Ask Questions in Natural Language
                        </h3>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <textarea id="nl-query-input" style="width: 100%; padding: 1rem; border: 1px solid #d1d5db; border-radius: 8px; resize: none;" rows="3"
                                  placeholder="Ask questions like: 'What are the top 5 products by revenue?' or 'Show me customers from California'"></textarea>
                        <button class="btn btn-ai" onclick="processNaturalLanguageQuery()" style="margin-top: 0.5rem;">
                            <i class="fas fa-search"></i> Ask Question
                        </button>
                    </div>
                    <div id="nl-query-result" style="display: none;">
                        Processing your question...
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Database Connection Modal -->
    <div id="database-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-database"></i> Add Database Connection</h3>
                <button class="modal-close" onclick="closeModal('database-modal')">&times;</button>
            </div>
            <form onsubmit="addDatabaseConnection(event)">
                <div class="form-group">
                    <label class="form-label">Database Type</label>
                    <select class="form-select" required>
                        <option value="">Select database type</option>
                        <option value="mysql">MySQL</option>
                        <option value="postgresql">PostgreSQL</option>
                        <option value="sqlserver">SQL Server</option>
                        <option value="oracle">Oracle</option>
                        <option value="sqlite">SQLite</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Connection Name</label>
                    <input type="text" class="form-input" placeholder="My Database" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Host</label>
                    <input type="text" class="form-input" placeholder="localhost">
                </div>
                <div class="form-group">
                    <label class="form-label">Port</label>
                    <input type="number" class="form-input" placeholder="3306">
                </div>
                <div class="form-group">
                    <label class="form-label">Database Name</label>
                    <input type="text" class="form-input" placeholder="my_database" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-input" placeholder="username" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-input" placeholder="password">
                </div>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('database-modal')">Cancel</button>
                    <button type="submit" class="btn">Test & Save Connection</button>
                </div>
            </form>
        </div>
    </div>

    <!-- API Connection Modal -->
    <div id="api-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-cloud"></i> Add API Connection</h3>
                <button class="modal-close" onclick="closeModal('api-modal')">&times;</button>
            </div>
            <form onsubmit="addAPIConnection(event)">
                <div class="form-group">
                    <label class="form-label">API Type</label>
                    <select class="form-select" required>
                        <option value="">Select API type</option>
                        <option value="rest">REST API</option>
                        <option value="graphql">GraphQL</option>
                        <option value="google-sheets">Google Sheets</option>
                        <option value="salesforce">Salesforce</option>
                        <option value="hubspot">HubSpot</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Connection Name</label>
                    <input type="text" class="form-input" placeholder="My API" required>
                </div>
                <div class="form-group">
                    <label class="form-label">API URL</label>
                    <input type="url" class="form-input" placeholder="https://api.example.com" required>
                </div>
                <div class="form-group">
                    <label class="form-label">API Key</label>
                    <input type="password" class="form-input" placeholder="Your API key">
                </div>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('api-modal')">Cancel</button>
                    <button type="submit" class="btn">Test & Save Connection</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Global variables
        let charts = {};
        let currentView = 'overview';
        let currentDashboard = 'main';
        let chartBuilderChart = null;
        let dashboards = {
            'main': { name: 'Main Dashboard', charts: [] },
            'sales': { name: 'Sales Analytics', charts: [] },
            'customers': { name: 'Customer Insights', charts: [] },
            'products': { name: 'Product Performance', charts: [] },
            'financial': { name: 'Financial Overview', charts: [] }
        };

        // Initialize application
        window.onload = function() {
            loadMetrics();
            initializeCharts();
            showDashboard('main');
            setupDragAndDrop();
        };

        // View Management
        function showView(viewName) {
            // Hide all views
            document.querySelectorAll('.view-content').forEach(view => {
                view.style.display = 'none';
            });

            // Remove active class from sidebar items
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
            });

            // Show selected view
            const viewElement = document.getElementById(viewName + '-view');
            if (viewElement) {
                viewElement.style.display = 'block';
            }

            // Add active class to clicked sidebar item
            if (event && event.target) {
                event.target.classList.add('active');
            }
            currentView = viewName;

            // Load view-specific data
            switch(viewName) {
                case 'overview':
                    loadMetrics();
                    initializeCharts();
                    break;
                case 'ai-insights':
                    // AI insights view is loaded on demand
                    break;
                case 'natural-query':
                    // Natural query view is interactive
                    break;
            }
        }

        // Load Key Metrics
        function loadMetrics() {
            fetch('/api/analytics/sales-summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-revenue').textContent = '$' + data.total_revenue.toLocaleString();
                    document.getElementById('total-orders').textContent = data.total_orders.toLocaleString();
                    document.getElementById('avg-order-value').textContent = '$' + data.avg_order_value.toFixed(2);
                })
                .catch(error => {
                    console.error('Error loading metrics:', error);
                    document.getElementById('total-revenue').textContent = 'Error';
                });

            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-customers').textContent = data.data_counts.customers.toLocaleString();
                })
                .catch(error => {
                    console.error('Error loading customer count:', error);
                    document.getElementById('total-customers').textContent = 'Error';
                });
        }
    </script>
</body>
</html>
"""

# Enhanced API Routes with Power BI capabilities
@app.route('/')
def index():
    """Main dashboard page with Power BI-like interface."""
    return render_template_string(ENHANCED_TEMPLATE)

@app.route('/api/status')
def get_status():
    """Get system status and data counts."""
    return jsonify({
        'status': 'running',
        'version': '0.2.0',
        'database': 'sqlite',
        'features': ['power-bi-charts', 'ai-insights', 'natural-language-queries', 'real-time-analytics'],
        'data_counts': {
            'customers': People.query.count(),
            'products': Products.query.count(),
            'orders': Orders.query.count(),
            'reviews': Reviews.query.count()
        }
    })

@app.route('/api/analytics/sales-summary')
def get_sales_summary():
    """Enhanced sales analytics with Power BI-like metrics."""
    # Total revenue and orders
    total_revenue = db.session.query(func.sum(Orders.total)).scalar() or 0
    total_orders = Orders.query.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # Revenue by month (last 12 months)
    monthly_revenue = db.session.query(
        func.strftime('%Y-%m', Orders.created_at).label('month'),
        func.sum(Orders.total).label('revenue'),
        func.count(Orders.id).label('order_count')
    ).filter(
        Orders.created_at >= datetime.now() - timedelta(days=365)
    ).group_by(func.strftime('%Y-%m', Orders.created_at)).all()

    # Top selling products
    top_products = db.session.query(
        Products.title,
        func.sum(Orders.quantity).label('total_sold'),
        func.sum(Orders.total).label('revenue')
    ).join(Orders).group_by(Products.id, Products.title).order_by(
        func.sum(Orders.total).desc()
    ).limit(10).all()

    # Sales by category
    category_sales = db.session.query(
        Products.category,
        func.sum(Orders.total).label('revenue'),
        func.count(Orders.id).label('order_count')
    ).join(Orders).group_by(Products.category).all()

    return jsonify({
        'total_revenue': round(total_revenue, 2),
        'total_orders': total_orders,
        'avg_order_value': round(avg_order_value, 2),
        'monthly_revenue': [
            {
                'month': item.month,
                'revenue': round(item.revenue, 2),
                'order_count': item.order_count
            }
            for item in monthly_revenue
        ],
        'top_products': [
            {
                'name': product.title,
                'units_sold': int(product.total_sold),
                'revenue': round(product.revenue, 2)
            }
            for product in top_products
        ],
        'category_sales': [
            {
                'category': item.category,
                'revenue': round(item.revenue, 2),
                'order_count': item.order_count
            }
            for item in category_sales
        ]
    })

@app.route('/api/analytics/customer-insights')
def get_customer_insights():
    """Enhanced customer analytics."""
    # Customer acquisition by source
    customers_by_source = db.session.query(
        People.source,
        func.count(People.id).label('count'),
        func.avg(func.julianday('now') - func.julianday(People.birth_date)).label('avg_age')
    ).group_by(People.source).all()

    # Customer lifetime value distribution
    clv_data = db.session.query(
        People.id,
        People.name,
        func.sum(Orders.total).label('clv')
    ).join(Orders).group_by(People.id, People.name).order_by(
        func.sum(Orders.total).desc()
    ).limit(20).all()

    # Geographic distribution
    geographic_data = db.session.query(
        People.state,
        func.count(People.id).label('customer_count'),
        func.sum(Orders.total).label('total_revenue')
    ).join(Orders).group_by(People.state).order_by(
        func.sum(Orders.total).desc()
    ).limit(15).all()

    return jsonify({
        'by_source': [
            {
                'source': item.source,
                'count': item.count,
                'avg_age': round(item.avg_age / 365, 1) if item.avg_age else 0
            }
            for item in customers_by_source
        ],
        'top_customers': [
            {
                'name': item.name,
                'clv': round(item.clv, 2)
            }
            for item in clv_data
        ],
        'geographic': [
            {
                'state': item.state,
                'customers': item.customer_count,
                'revenue': round(item.total_revenue, 2)
            }
            for item in geographic_data
        ]
    })

@app.route('/api/llm/query', methods=['POST'])
def natural_language_query():
    """Process natural language queries using LLM."""
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    # Generate SQL using LLM
    llm_result = LLMService.natural_language_to_sql(question)

    try:
        # Execute the generated SQL
        result = db.session.execute(text(llm_result['sql']))
        rows = result.fetchall()
        columns = result.keys()

        # Convert to list of dictionaries
        data_result = [dict(zip(columns, row)) for row in rows]

        return jsonify({
            'question': question,
            'sql': llm_result['sql'],
            'explanation': llm_result['explanation'],
            'result_type': llm_result['result_type'],
            'data': data_result,
            'row_count': len(data_result)
        })

    except Exception as e:
        return jsonify({
            'question': question,
            'sql': llm_result['sql'],
            'explanation': llm_result['explanation'],
            'error': str(e),
            'result_type': 'error'
        }), 500

@app.route('/api/llm/insights')
def get_ai_insights():
    """Generate AI insights from current data."""
    # Gather key metrics for insight generation
    total_revenue = db.session.query(func.sum(Orders.total)).scalar() or 0
    total_customers = People.query.count()
    total_products = Products.query.count()
    avg_rating = db.session.query(func.avg(Reviews.rating)).scalar() or 0

    # Top category by revenue
    top_category = db.session.query(
        Products.category,
        func.sum(Orders.total).label('revenue')
    ).join(Orders).group_by(Products.category).order_by(
        func.sum(Orders.total).desc()
    ).first()

    data_summary = {
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'total_products': total_products,
        'avg_product_rating': round(avg_rating, 2),
        'top_category': top_category.category if top_category else 'N/A',
        'top_category_revenue': round(top_category.revenue, 2) if top_category else 0
    }

    insights = LLMService.generate_insights(data_summary)

    return jsonify({
        'insights': insights,
        'data_summary': data_summary,
        'generated_at': datetime.now().isoformat()
    })

# Enhanced HTML Template with Power BI + Metabase UI
ENHANCED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Songo BI - Advanced Business Intelligence Platform</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8fafc;
            color: #2d3748;
            line-height: 1.6;
        }

        /* Power BI-inspired Navigation */
        .navbar {
            background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar h1 {
            font-size: 1.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .navbar-actions {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        .nav-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .nav-btn:hover {
            background: rgba(255,255,255,0.3);
        }

        /* Main Layout */
        .main-container {
            display: grid;
            grid-template-columns: 250px 1fr;
            min-height: calc(100vh - 80px);
        }

        /* Sidebar */
        .sidebar {
            background: white;
            border-right: 1px solid #e2e8f0;
            padding: 1.5rem;
            overflow-y: auto;
        }
        .sidebar-section {
            margin-bottom: 2rem;
        }
        .sidebar-title {
            font-weight: 600;
            color: #374151;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .sidebar-item {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .sidebar-item:hover {
            background: #f1f5f9;
        }
        .sidebar-item.active {
            background: #dbeafe;
            color: #1d4ed8;
            font-weight: 500;
        }

        /* Content Area */
        .content {
            padding: 2rem;
            overflow-y: auto;
        }

        /* AI Chat Interface */
        .ai-chat-container {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
            z-index: 1000;
            transform: translateY(100%);
            transition: transform 0.3s ease;
        }
        .ai-chat-container.open {
            transform: translateY(0);
        }
        .ai-chat-header {
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            color: white;
            padding: 1rem;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ai-chat-body {
            padding: 1rem;
            max-height: 400px;
            overflow-y: auto;
        }
        .ai-chat-input {
            padding: 1rem;
            border-top: 1px solid #e2e8f0;
        }
        .ai-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            resize: none;
        }
        .ai-send-btn {
            background: #7c3aed;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 0.5rem;
            width: 100%;
        }

        /* Chat Toggle Button */
        .ai-toggle {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.3);
            font-size: 1.5rem;
            transition: all 0.3s;
        }
        .ai-toggle:hover {
            transform: scale(1.1);
        }
        .ai-toggle.hidden {
            display: none;
        }

        /* Dashboard Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        /* Chart Containers */
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
        }
        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #f1f5f9;
        }
        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a202c;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .chart-canvas {
            position: relative;
            height: 300px;
            margin: 1rem 0;
        }

        /* Metric Cards */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        /* Buttons */
        .btn {
            background: #0078d4;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn:hover {
            background: #106ebe;
            transform: translateY(-1px);
        }
        .btn-secondary {
            background: #6b7280;
        }
        .btn-secondary:hover {
            background: #4b5563;
        }
        .btn-ai {
            background: #7c3aed;
        }
        .btn-ai:hover {
            background: #6d28d9;
        }

        /* Loading States */
        .loading {
            text-align: center;
            color: #6b7280;
            font-style: italic;
            padding: 2rem;
        }

        /* Data Tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .data-table th, .data-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        .data-table th {
            background: #f8fafc;
            font-weight: 600;
            color: #374151;
        }
        .data-table tr:hover {
            background: #f8fafc;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            .sidebar {
                display: none;
            }
            .ai-chat-container {
                width: calc(100vw - 2rem);
                right: 1rem;
                left: 1rem;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div>
            <h1><i class="fas fa-chart-line"></i> Songo BI</h1>
        </div>
        <div class="navbar-actions">
            <button class="nav-btn" onclick="refreshAllData()">
                <i class="fas fa-sync-alt"></i> Refresh
            </button>
            <button class="nav-btn" onclick="exportDashboard()">
                <i class="fas fa-download"></i> Export
            </button>
            <button class="nav-btn" onclick="toggleAIChat()">
                <i class="fas fa-robot"></i> AI Assistant
            </button>
        </div>
    </nav>

    <div class="main-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-title">📊 Analytics</div>
                <div class="sidebar-item active" onclick="showView('overview')">
                    <i class="fas fa-tachometer-alt"></i> Overview
                </div>
                <div class="sidebar-item" onclick="showView('sales')">
                    <i class="fas fa-chart-line"></i> Sales Analytics
                </div>
                <div class="sidebar-item" onclick="showView('customers')">
                    <i class="fas fa-users"></i> Customer Insights
                </div>
                <div class="sidebar-item" onclick="showView('products')">
                    <i class="fas fa-box"></i> Product Performance
                </div>
            </div>

            <div class="sidebar-section">
                <div class="sidebar-title">🤖 AI Features</div>
                <div class="sidebar-item" onclick="showView('ai-insights')">
                    <i class="fas fa-brain"></i> AI Insights
                </div>
                <div class="sidebar-item" onclick="showView('natural-query')">
                    <i class="fas fa-comments"></i> Ask Questions
                </div>
            </div>

            <div class="sidebar-section">
                <div class="sidebar-title">🔧 Tools</div>
                <div class="sidebar-item" onclick="showView('sql-lab')">
                    <i class="fas fa-database"></i> SQL Lab
                </div>
                <div class="sidebar-item" onclick="showView('data-explorer')">
                    <i class="fas fa-search"></i> Data Explorer
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="content">
            <!-- Overview Dashboard -->
            <div id="overview-view" class="view-content">
                <!-- Key Metrics -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value" id="total-revenue">$0</div>
                        <div class="metric-label"><i class="fas fa-dollar-sign"></i> Total Revenue</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="total-orders">0</div>
                        <div class="metric-label"><i class="fas fa-shopping-cart"></i> Total Orders</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="total-customers">0</div>
                        <div class="metric-label"><i class="fas fa-users"></i> Total Customers</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="avg-order-value">$0</div>
                        <div class="metric-label"><i class="fas fa-chart-bar"></i> Avg Order Value</div>
                    </div>
                </div>

                <!-- Charts Grid -->
                <div class="dashboard-grid">
                    <!-- Monthly Revenue Trend -->
                    <div class="chart-container" style="grid-column: span 2;">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-chart-line"></i> Monthly Revenue Trend
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('monthly-revenue')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="monthly-revenue-chart"></canvas>
                        </div>
                    </div>

                    <!-- Sales by Category -->
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-pie-chart"></i> Sales by Category
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('category-sales')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="category-sales-chart"></canvas>
                        </div>
                    </div>

                    <!-- Customer Acquisition -->
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-user-plus"></i> Customer Sources
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('customer-sources')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="customer-sources-chart"></canvas>
                        </div>
                    </div>

                    <!-- Top Products -->
                    <div class="chart-container" style="grid-column: span 2;">
                        <div class="chart-header">
                            <h3 class="chart-title">
                                <i class="fas fa-trophy"></i> Top Selling Products
                            </h3>
                            <button class="btn btn-secondary" onclick="refreshChart('top-products')">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="chart-canvas">
                            <canvas id="top-products-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI Insights View -->
            <div id="ai-insights-view" class="view-content" style="display: none;">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">
                            <i class="fas fa-brain"></i> AI-Generated Business Insights
                        </h3>
                        <button class="btn btn-ai" onclick="generateInsights()">
                            <i class="fas fa-magic"></i> Generate New Insights
                        </button>
                    </div>
                    <div id="ai-insights-content" class="loading">
                        Click "Generate New Insights" to get AI-powered business analysis...
                    </div>
                </div>
            </div>

            <!-- Natural Language Query View -->
            <div id="natural-query-view" class="view-content" style="display: none;">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">
                            <i class="fas fa-comments"></i> Ask Questions in Natural Language
                        </h3>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <textarea id="nl-query-input" class="ai-input" rows="3"
                                  placeholder="Ask questions like: 'What are the top 5 products by revenue?' or 'Show me customers from California'"></textarea>
                        <button class="btn btn-ai" onclick="processNaturalLanguageQuery()" style="margin-top: 0.5rem;">
                            <i class="fas fa-search"></i> Ask Question
                        </button>
                    </div>
                    <div id="nl-query-result" class="loading" style="display: none;">
                        Processing your question...
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- AI Chat Interface -->
    <div id="ai-chat" class="ai-chat-container">
        <div class="ai-chat-header">
            <h4><i class="fas fa-robot"></i> AI Assistant</h4>
            <button onclick="toggleAIChat()" style="background: none; border: none; color: white; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="ai-chat-body" id="chat-messages">
            <div style="text-align: center; color: #6b7280; padding: 1rem;">
                <i class="fas fa-robot" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                <p>Hi! I'm your AI assistant. Ask me anything about your data!</p>
            </div>
        </div>
        <div class="ai-chat-input">
            <textarea id="chat-input" class="ai-input" rows="2"
                      placeholder="Ask me about your data..."></textarea>
            <button class="ai-send-btn" onclick="sendChatMessage()">
                <i class="fas fa-paper-plane"></i> Send
            </button>
        </div>
    </div>

    <!-- AI Toggle Button -->
    <button id="ai-toggle" class="ai-toggle" onclick="toggleAIChat()">
        <i class="fas fa-robot"></i>
    </button>

    <script>
        // Global variables
        let charts = {};
        let currentView = 'overview';
        let aiChatOpen = false;

        // Initialize application
        window.onload = function() {
            loadMetrics();
            initializeCharts();
            showDashboard('main');
            setupDragAndDrop();
        };

        // Dashboard Management
        function showDashboard(dashboardId) {
            currentDashboard = dashboardId;

            // Update sidebar active state
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');

            // Show dashboard content
            showView('overview');

            // Update page title
            document.title = `Songo BI - ${dashboards[dashboardId].name}`;
        }

        function createNewDashboard() {
            const name = prompt('Enter dashboard name:');
            if (name) {
                const id = name.toLowerCase().replace(/\s+/g, '-');
                dashboards[id] = { name: name, charts: [] };

                // Add to sidebar
                const sidebar = document.querySelector('.sidebar-section');
                const newItem = document.createElement('div');
                newItem.className = 'sidebar-item';
                newItem.onclick = () => showDashboard(id);
                newItem.innerHTML = `<i class="fas fa-chart-bar"></i> ${name}`;
                sidebar.appendChild(newItem);

                showDashboard(id);
            }
        }

        // Import Data Functions
        function handleCSVUpload(event) {
            const file = event.target.files[0];
            if (file && file.type === 'text/csv') {
                const formData = new FormData();
                formData.append('file', file);

                // Show upload progress
                const recentImports = document.getElementById('recent-imports');
                recentImports.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: white; border-radius: 8px;">
                        <i class="fas fa-spinner fa-spin"></i>
                        <div>
                            <strong>Uploading ${file.name}</strong>
                            <div style="color: #6b7280; font-size: 0.9rem;">Processing CSV file...</div>
                        </div>
                    </div>
                `;

                // Simulate upload (replace with actual API call)
                setTimeout(() => {
                    recentImports.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: white; border-radius: 8px;">
                            <i class="fas fa-check-circle" style="color: #059669;"></i>
                            <div>
                                <strong>${file.name}</strong>
                                <div style="color: #6b7280; font-size: 0.9rem;">Uploaded successfully • ${new Date().toLocaleString()}</div>
                            </div>
                        </div>
                    `;
                }, 2000);
            } else {
                alert('Please select a valid CSV file');
            }
        }

        function setupDragAndDrop() {
            const uploadAreas = document.querySelectorAll('.upload-area');
            uploadAreas.forEach(area => {
                area.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    area.classList.add('dragover');
                });

                area.addEventListener('dragleave', () => {
                    area.classList.remove('dragover');
                });

                area.addEventListener('drop', (e) => {
                    e.preventDefault();
                    area.classList.remove('dragover');
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        handleCSVUpload({ target: { files: files } });
                    }
                });
            });
        }

        // Chart Builder Functions
        function selectChartType(type) {
            document.querySelectorAll('.chart-type-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }

        function buildChart() {
            const dataSource = document.getElementById('chart-data-source').value;
            const chartType = document.querySelector('.chart-type-btn.active').dataset.type;
            const xAxis = document.getElementById('chart-x-axis').value;
            const yAxis = document.getElementById('chart-y-axis').value;

            // Hide placeholder
            document.getElementById('chart-placeholder').style.display = 'none';

            // Create chart
            const ctx = document.getElementById('chart-builder-canvas').getContext('2d');

            if (chartBuilderChart) {
                chartBuilderChart.destroy();
            }

            // Generate sample data based on selections
            const sampleData = generateSampleChartData(dataSource, xAxis, yAxis);

            chartBuilderChart = new Chart(ctx, {
                type: chartType === 'area' ? 'line' : chartType,
                data: sampleData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: chartType === 'pie' },
                        title: {
                            display: true,
                            text: `${yAxis} by ${xAxis}`
                        }
                    },
                    scales: chartType === 'pie' ? {} : {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        function generateSampleChartData(dataSource, xAxis, yAxis) {
            // Generate sample data based on selections
            const labels = [];
            const data = [];

            if (xAxis === 'created_at') {
                // Generate monthly data
                for (let i = 11; i >= 0; i--) {
                    const date = new Date();
                    date.setMonth(date.getMonth() - i);
                    labels.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
                    data.push(Math.floor(Math.random() * 10000) + 1000);
                }
            } else if (xAxis === 'category') {
                labels.push('Widget', 'Gadget', 'Gizmo', 'Tool', 'Accessory');
                data.push(15000, 12000, 8000, 6000, 4000);
            } else if (xAxis === 'state') {
                labels.push('CA', 'NY', 'TX', 'FL', 'IL');
                data.push(25, 20, 15, 12, 10);
            }

            return {
                labels: labels,
                datasets: [{
                    label: yAxis,
                    data: data,
                    backgroundColor: ['#0078d4', '#7c3aed', '#dc2626', '#059669', '#d97706'],
                    borderColor: '#0078d4',
                    borderWidth: 2,
                    fill: false
                }]
            };
        }

        function saveChart() {
            if (chartBuilderChart) {
                const chartConfig = {
                    type: chartBuilderChart.config.type,
                    data: chartBuilderChart.data,
                    options: chartBuilderChart.options
                };

                // Add to current dashboard
                dashboards[currentDashboard].charts.push(chartConfig);

                alert(`Chart saved to ${dashboards[currentDashboard].name}!`);
            } else {
                alert('Please build a chart first');
            }
        }

        function addChartToDashboard() {
            if (chartBuilderChart) {
                saveChart();
                showDashboard(currentDashboard);
            } else {
                alert('Please build a chart first');
            }
        }

        // View Management
        function showView(viewName) {
            // Hide all views
            document.querySelectorAll('.view-content').forEach(view => {
                view.style.display = 'none';
            });

            // Remove active class from sidebar items
            document.querySelectorAll('.sidebar-item').forEach(item => {
                item.classList.remove('active');
            });

            // Show selected view
            const viewElement = document.getElementById(viewName + '-view');
            if (viewElement) {
                viewElement.style.display = 'block';
            }

            // Add active class to clicked sidebar item
            event.target.classList.add('active');
            currentView = viewName;

            // Load view-specific data
            switch(viewName) {
                case 'overview':
                    loadMetrics();
                    initializeCharts();
                    break;
                case 'ai-insights':
                    // AI insights view is loaded on demand
                    break;
                case 'natural-query':
                    // Natural query view is interactive
                    break;
            }
        }

        // Load Key Metrics
        function loadMetrics() {
            fetch('/api/analytics/sales-summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-revenue').textContent = '$' + data.total_revenue.toLocaleString();
                    document.getElementById('total-orders').textContent = data.total_orders.toLocaleString();
                    document.getElementById('avg-order-value').textContent = '$' + data.avg_order_value.toFixed(2);
                })
                .catch(error => console.error('Error loading metrics:', error));

            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-customers').textContent = data.data_counts.customers.toLocaleString();
                })
                .catch(error => console.error('Error loading customer count:', error));
        }

        // Initialize Charts
        function initializeCharts() {
            createMonthlyRevenueChart();
            createCategorySalesChart();
            createCustomerSourcesChart();
            createTopProductsChart();
        }

        // Monthly Revenue Trend Chart (Power BI style)
        function createMonthlyRevenueChart() {
            fetch('/api/analytics/sales-summary')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('monthly-revenue-chart').getContext('2d');

                    if (charts['monthly-revenue']) {
                        charts['monthly-revenue'].destroy();
                    }

                    charts['monthly-revenue'] = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.monthly_revenue.map(item => item.month),
                            datasets: [{
                                label: 'Revenue ($)',
                                data: data.monthly_revenue.map(item => item.revenue),
                                borderColor: '#0078d4',
                                backgroundColor: 'rgba(0, 120, 212, 0.1)',
                                borderWidth: 3,
                                fill: true,
                                tension: 0.4,
                                pointBackgroundColor: '#0078d4',
                                pointBorderColor: '#ffffff',
                                pointBorderWidth: 2,
                                pointRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                    titleColor: 'white',
                                    bodyColor: 'white',
                                    borderColor: '#0078d4',
                                    borderWidth: 1
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: { color: '#f1f5f9' },
                                    ticks: {
                                        callback: function(value) {
                                            return '$' + value.toLocaleString();
                                        }
                                    }
                                },
                                x: {
                                    grid: { display: false }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading monthly revenue chart:', error));
        }

        // Category Sales Pie Chart
        function createCategorySalesChart() {
            fetch('/api/analytics/sales-summary')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('category-sales-chart').getContext('2d');

                    if (charts['category-sales']) {
                        charts['category-sales'].destroy();
                    }

                    charts['category-sales'] = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: data.category_sales.map(item => item.category),
                            datasets: [{
                                data: data.category_sales.map(item => item.revenue),
                                backgroundColor: [
                                    '#0078d4', '#7c3aed', '#dc2626', '#059669', '#d97706'
                                ],
                                borderWidth: 0,
                                hoverOffset: 10
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: {
                                        padding: 20,
                                        usePointStyle: true
                                    }
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return context.label + ': $' + context.parsed.toLocaleString();
                                        }
                                    }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading category sales chart:', error));
        }

        // Customer Sources Chart
        function createCustomerSourcesChart() {
            fetch('/api/analytics/customer-insights')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('customer-sources-chart').getContext('2d');

                    if (charts['customer-sources']) {
                        charts['customer-sources'].destroy();
                    }

                    charts['customer-sources'] = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: data.by_source.map(item => item.source),
                            datasets: [{
                                label: 'Customers',
                                data: data.by_source.map(item => item.count),
                                backgroundColor: '#7c3aed',
                                borderRadius: 8,
                                borderSkipped: false
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: { color: '#f1f5f9' }
                                },
                                x: {
                                    grid: { display: false }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading customer sources chart:', error));
        }

        // Top Products Chart
        function createTopProductsChart() {
            fetch('/api/analytics/sales-summary')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('top-products-chart').getContext('2d');

                    if (charts['top-products']) {
                        charts['top-products'].destroy();
                    }

                    charts['top-products'] = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: data.top_products.slice(0, 8).map(item =>
                                item.name.length > 25 ? item.name.substring(0, 25) + '...' : item.name
                            ),
                            datasets: [{
                                label: 'Revenue ($)',
                                data: data.top_products.slice(0, 8).map(item => item.revenue),
                                backgroundColor: '#059669',
                                borderRadius: 8,
                                borderSkipped: false
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            indexAxis: 'y',
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                x: {
                                    beginAtZero: true,
                                    grid: { color: '#f1f5f9' },
                                    ticks: {
                                        callback: function(value) {
                                            return '$' + value.toLocaleString();
                                        }
                                    }
                                },
                                y: {
                                    grid: { display: false }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading top products chart:', error));
        }

        // AI Chat Functions
        function toggleAIChat() {
            const chatContainer = document.getElementById('ai-chat');
            const toggleButton = document.getElementById('ai-toggle');

            aiChatOpen = !aiChatOpen;

            if (aiChatOpen) {
                chatContainer.classList.add('open');
                toggleButton.classList.add('hidden');
            } else {
                chatContainer.classList.remove('open');
                toggleButton.classList.remove('hidden');
            }
        }

        function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();

            if (!message) return;

            // Add user message to chat
            addChatMessage('user', message);
            input.value = '';

            // Process with AI
            processAIMessage(message);
        }

        function addChatMessage(sender, message) {
            const chatMessages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.style.cssText = `
                margin-bottom: 1rem;
                padding: 0.75rem;
                border-radius: 8px;
                ${sender === 'user' ?
                    'background: #dbeafe; margin-left: 2rem; text-align: right;' :
                    'background: #f3f4f6; margin-right: 2rem;'
                }
            `;
            messageDiv.innerHTML = `
                <div style="font-weight: 500; margin-bottom: 0.25rem;">
                    ${sender === 'user' ? '👤 You' : '🤖 AI Assistant'}
                </div>
                <div>${message}</div>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function processAIMessage(message) {
            // Show typing indicator
            addChatMessage('ai', '<i class="fas fa-spinner fa-spin"></i> Thinking...');

            // Send to natural language processing
            fetch('/api/llm/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: message })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                const chatMessages = document.getElementById('chat-messages');
                chatMessages.removeChild(chatMessages.lastChild);

                if (data.error) {
                    addChatMessage('ai', `❌ Sorry, I encountered an error: ${data.error}`);
                } else {
                    let response = `📊 **Query Results:**\n\n`;
                    response += `**SQL Generated:** \`${data.sql}\`\n\n`;
                    response += `**Explanation:** ${data.explanation}\n\n`;

                    if (data.data && data.data.length > 0) {
                        response += `**Results:** Found ${data.row_count} records\n`;
                        // Show first few results
                        const preview = data.data.slice(0, 3);
                        preview.forEach((row, index) => {
                            response += `${index + 1}. ${JSON.stringify(row)}\n`;
                        });
                        if (data.data.length > 3) {
                            response += `... and ${data.data.length - 3} more records`;
                        }
                    }

                    addChatMessage('ai', response.replace(/\n/g, '<br>'));
                }
            })
            .catch(error => {
                // Remove typing indicator
                const chatMessages = document.getElementById('chat-messages');
                chatMessages.removeChild(chatMessages.lastChild);
                addChatMessage('ai', `❌ Error processing your question: ${error.message}`);
            });
        }

        // Natural Language Query Processing
        function processNaturalLanguageQuery() {
            const input = document.getElementById('nl-query-input');
            const question = input.value.trim();

            if (!question) {
                alert('Please enter a question');
                return;
            }

            const resultDiv = document.getElementById('nl-query-result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Processing your question...</div>';

            fetch('/api/llm/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `
                        <div style="color: #dc2626; padding: 1rem; background: #fef2f2; border-radius: 8px;">
                            <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                            <p>${data.error}</p>
                        </div>
                    `;
                } else {
                    let resultHTML = `
                        <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                            <h4><i class="fas fa-lightbulb"></i> Query Analysis</h4>
                            <p><strong>Your Question:</strong> ${data.question}</p>
                            <p><strong>Generated SQL:</strong> <code>\${data.sql}</code></p>
                            <p><strong>Explanation:</strong> ${data.explanation}</p>
                        </div>
                    `;

                    if (data.data && data.data.length > 0) {
                        resultHTML += `
                            <div style="background: white; padding: 1rem; border-radius: 8px;">
                                <h4><i class="fas fa-table"></i> Results (${data.row_count} records)</h4>
                                <div style="overflow-x: auto; margin-top: 1rem;">
                        `;

                        // Create table
                        if (data.data.length > 0) {
                            const headers = Object.keys(data.data[0]);
                            resultHTML += '<table class="data-table"><thead><tr>';
                            headers.forEach(header => {
                                resultHTML += `<th>${header.replace('_', ' ').toUpperCase()}</th>`;
                            });
                            resultHTML += '</tr></thead><tbody>';

                            data.data.slice(0, 10).forEach(row => {
                                resultHTML += '<tr>';
                                headers.forEach(header => {
                                    let value = row[header];
                                    if (typeof value === 'number' && (header.includes('price') || header.includes('total') || header.includes('revenue'))) {
                                        value = '$' + value.toFixed(2);
                                    }
                                    resultHTML += `<td>${value || 'N/A'}</td>`;
                                });
                                resultHTML += '</tr>';
                            });

                            resultHTML += '</tbody></table>';
                            if (data.data.length > 10) {
                                resultHTML += `<p style="margin-top: 1rem; color: #6b7280;">Showing first 10 of ${data.data.length} results</p>`;
                            }
                        }

                        resultHTML += '</div></div>';
                    } else {
                        resultHTML += `
                            <div style="background: #fef3c7; padding: 1rem; border-radius: 8px;">
                                <p><i class="fas fa-info-circle"></i> No results found for your query.</p>
                            </div>
                        `;
                    }

                    resultDiv.innerHTML = resultHTML;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = `
                    <div style="color: #dc2626; padding: 1rem; background: #fef2f2; border-radius: 8px;">
                        <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                        <p>Failed to process your question: ${error.message}</p>
                    </div>
                `;
            });
        }

        // AI Insights Generation
        function generateInsights() {
            const contentDiv = document.getElementById('ai-insights-content');
            contentDiv.innerHTML = '<div class="loading"><i class="fas fa-brain fa-spin"></i> AI is analyzing your data...</div>';

            fetch('/api/llm/insights')
                .then(response => response.json())
                .then(data => {
                    contentDiv.innerHTML = `
                        <div style="background: #f0f9ff; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
                            <h4 style="color: #0369a1; margin-bottom: 1rem;">
                                <i class="fas fa-lightbulb"></i> AI-Generated Business Insights
                            </h4>
                            <div style="white-space: pre-line; line-height: 1.8;">
                                ${data.insights}
                            </div>
                            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #bae6fd; font-size: 0.9rem; color: #0369a1;">
                                <i class="fas fa-clock"></i> Generated at: ${new Date(data.generated_at).toLocaleString()}
                            </div>
                        </div>

                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                            <h4 style="margin-bottom: 1rem;"><i class="fas fa-chart-bar"></i> Data Summary</h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                                <div>
                                    <strong>Total Revenue:</strong><br>
                                    $${data.data_summary.total_revenue.toLocaleString()}
                                </div>
                                <div>
                                    <strong>Total Customers:</strong><br>
                                    ${data.data_summary.total_customers.toLocaleString()}
                                </div>
                                <div>
                                    <strong>Total Products:</strong><br>
                                    ${data.data_summary.total_products.toLocaleString()}
                                </div>
                                <div>
                                    <strong>Avg Product Rating:</strong><br>
                                    ${data.data_summary.avg_product_rating}⭐
                                </div>
                            </div>
                        </div>
                    `;
                })
                .catch(error => {
                    contentDiv.innerHTML = `
                        <div style="color: #dc2626; padding: 1rem; background: #fef2f2; border-radius: 8px;">
                            <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                            <p>Failed to generate insights: ${error.message}</p>
                            <p style="margin-top: 0.5rem; font-size: 0.9rem;">
                                Note: AI insights require OpenAI API key configuration.
                            </p>
                        </div>
                    `;
                });
        }

        // Utility Functions
        function refreshChart(chartName) {
            switch(chartName) {
                case 'monthly-revenue':
                    createMonthlyRevenueChart();
                    break;
                case 'category-sales':
                    createCategorySalesChart();
                    break;
                case 'customer-sources':
                    createCustomerSourcesChart();
                    break;
                case 'top-products':
                    createTopProductsChart();
                    break;
            }
        }

        function refreshAllData() {
            loadMetrics();
            Object.keys(charts).forEach(chartName => {
                refreshChart(chartName);
            });
        }

        function exportDashboard() {
            alert('📊 Export functionality ready!\\n\\nThis would export the current dashboard to:\\n• PDF Report\\n• Excel Workbook\\n• PowerPoint Presentation\\n• JSON Data');
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter to send chat message
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                if (document.activeElement.id === 'chat-input') {
                    sendChatMessage();
                } else if (document.activeElement.id === 'nl-query-input') {
                    processNaturalLanguageQuery();
                }
            }

            // Escape to close AI chat
            if (e.key === 'Escape' && aiChatOpen) {
                toggleAIChat();
            }
        });

        // Modal Functions
        function showDatabaseConnectionModal() {
            document.getElementById('database-modal').classList.add('show');
        }

        function showAPIConnectionModal() {
            document.getElementById('api-modal').classList.add('show');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('show');
        }

        function addDatabaseConnection(event) {
            event.preventDefault();
            setTimeout(() => {
                alert('Database connection added successfully!');
                closeModal('database-modal');
            }, 1000);
        }

        function addAPIConnection(event) {
            event.preventDefault();
            setTimeout(() => {
                alert('API connection added successfully!');
                closeModal('api-modal');
            }, 1000);
        }

        // Enhanced utility functions
        function exportDashboard() {
            const dashboardData = {
                name: dashboards[currentDashboard].name,
                charts: dashboards[currentDashboard].charts,
                exported_at: new Date().toISOString()
            };

            const blob = new Blob([JSON.stringify(dashboardData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${dashboards[currentDashboard].name.replace(/\s+/g, '_')}_dashboard.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        // Close modals when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.classList.remove('show');
            }
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                createNewDashboard();
            }
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.show').forEach(modal => {
                    modal.classList.remove('show');
                });
            }
        });

        // Auto-refresh every 5 minutes
        setInterval(function() {
            if (currentView === 'overview') {
                refreshAllData();
            }
        }, 300000);
    </script>
</body>
</html>
"""

def create_enhanced_sample_data():
    """Create comprehensive sample data for the enhanced BI platform."""
    import random
    from datetime import datetime, timedelta

    # Check if data already exists
    if People.query.count() > 0:
        print("📊 Enhanced sample data already exists!")
        return

    print("🔄 Creating enhanced sample data...")

    # Sample data lists
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Chris", "Emma", "Alex", "Maria",
                   "Robert", "Jennifer", "Michael", "Jessica", "William", "Ashley", "James", "Amanda",
                   "Daniel", "Emily", "Matthew", "Madison", "Anthony", "Elizabeth", "Mark", "Samantha"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                  "Taylor", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Moore"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio",
              "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus",
              "Charlotte", "San Francisco", "Indianapolis", "Seattle", "Denver", "Boston"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "NC", "WA", "CO", "GA", "MI", "OR", "NV", "VA"]
    sources = ["Organic", "Google Ads", "Facebook", "Instagram", "LinkedIn", "Twitter", "Email Campaign", "Referral", "Direct"]

    # Create People (customers) with more realistic data
    people_list = []
    for i in range(200):  # Increased to 200 customers
        person = People(
            name=f"{random.choice(first_names)} {random.choice(last_names)}",
            email=f"customer{i+1}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'company.com'])}",
            address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Elm Dr', 'Maple Ln', 'Cedar Way'])}",
            city=random.choice(cities),
            state=random.choice(states),
            zip_code=f"{random.randint(10000, 99999)}",
            latitude=round(random.uniform(25.0, 49.0), 6),
            longitude=round(random.uniform(-125.0, -66.0), 6),
            birth_date=datetime.now().date() - timedelta(days=random.randint(6570, 25550)),  # 18-70 years old
            source=random.choice(sources),
            created_at=datetime.now() - timedelta(days=random.randint(1, 730))  # Up to 2 years ago
        )
        people_list.append(person)
        db.session.add(person)

    # Create Products with more categories
    categories = ["Widget", "Gadget", "Gizmo", "Doohickey", "Tool", "Accessory"]
    vendors = ["Acme Corp", "Global Industries", "Tech Solutions", "Premium Products", "Quality Goods",
               "Innovation Labs", "Future Tech", "Reliable Systems"]
    adjectives = ["Premium", "Deluxe", "Standard", "Economy", "Professional", "Advanced", "Basic", "Ultra", "Pro"]
    materials = ["Steel", "Aluminum", "Plastic", "Wood", "Carbon", "Titanium", "Copper", "Ceramic", "Glass"]

    products_list = []
    for i in range(100):  # Increased to 100 products
        product = Products(
            title=f"{random.choice(adjectives)} {random.choice(materials)} {random.choice(categories)} {random.randint(100, 999)}",
            category=random.choice(categories),
            vendor=random.choice(vendors),
            price=round(random.uniform(5.0, 999.99), 2),
            rating=round(random.uniform(2.5, 5.0), 1),
            created_at=datetime.now() - timedelta(days=random.randint(30, 1095))  # Up to 3 years ago
        )
        products_list.append(product)
        db.session.add(product)

    db.session.commit()  # Commit to get IDs

    # Create Orders with seasonal patterns
    for i in range(1000):  # Increased to 1000 orders
        # Create some seasonal patterns
        days_ago = random.randint(1, 365)
        order_date = datetime.now() - timedelta(days=days_ago)

        # Higher sales in November-December (holiday season)
        quantity_multiplier = 1.5 if order_date.month in [11, 12] else 1.0

        order = Orders(
            user_id=random.choice(people_list).id,
            product_id=random.choice(products_list).id,
            quantity=max(1, int(random.randint(1, 5) * quantity_multiplier)),
            total=round(random.uniform(10.0, 1500.0), 2),
            discount=round(random.uniform(0.0, 100.0), 2) if random.random() > 0.6 else 0.0,
            tax=round(random.uniform(0.5, 120.0), 2),
            created_at=order_date
        )
        db.session.add(order)

    # Create Reviews with more variety
    review_bodies = [
        "Excellent product! Exceeded my expectations.",
        "Good quality for the price point.",
        "Outstanding customer service and fast delivery.",
        "Product works exactly as described.",
        "Could be improved, but decent overall value.",
        "Amazing quality! Will definitely buy again.",
        "Super fast shipping and great packaging.",
        "Perfect for my specific needs.",
        "Great value for money, highly recommended.",
        "Outstanding product quality and durability!",
        "Not quite what I expected, but okay.",
        "Fantastic product, love the design.",
        "Works well, no complaints here.",
        "Impressive build quality and features.",
        "Good product, would recommend to others."
    ]

    for i in range(400):  # Increased to 400 reviews
        review = Reviews(
            product_id=random.choice(products_list).id,
            reviewer=f"{random.choice(first_names)} {random.choice(last_names)}",
            rating=random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0],  # Weighted towards higher ratings
            body=random.choice(review_bodies),
            created_at=datetime.now() - timedelta(days=random.randint(1, 365))
        )
        db.session.add(review)

    # Create Enhanced Dashboards
    dashboards_data = [
        {
            "title": "Executive Dashboard",
            "description": "High-level KPIs and business performance overview for executives",
            "config": {"layout": "executive", "auto_refresh": True}
        },
        {
            "title": "Sales Performance Dashboard",
            "description": "Detailed sales analytics, trends, and forecasting",
            "config": {"layout": "sales", "charts": ["revenue_trend", "product_performance"]}
        },
        {
            "title": "Customer Analytics Dashboard",
            "description": "Customer behavior, segmentation, and lifetime value analysis",
            "config": {"layout": "customer", "charts": ["acquisition", "retention", "clv"]}
        },
        {
            "title": "Product Intelligence Dashboard",
            "description": "Product performance, ratings, and inventory insights",
            "config": {"layout": "product", "charts": ["category_performance", "ratings_analysis"]}
        },
        {
            "title": "Financial Analytics Dashboard",
            "description": "Revenue analysis, profitability metrics, and financial forecasting",
            "config": {"layout": "financial", "charts": ["revenue", "profit_margins", "forecasts"]}
        }
    ]

    for dash_data in dashboards_data:
        dashboard = Dashboard(
            title=dash_data["title"],
            description=dash_data["description"],
            config=dash_data["config"]
        )
        db.session.add(dashboard)

    # Create Enhanced Data Sources
    data_sources_data = [
        {
            "name": "Enhanced E-commerce Database",
            "source_type": "sqlite",
            "connection_string": "sqlite:///songo_bi_enhanced.db"
        },
        {
            "name": "NetSuite ERP Production",
            "source_type": "netsuite",
            "connection_string": "netsuite://production.netsuite.com"
        },
        {
            "name": "Google Analytics 4",
            "source_type": "analytics",
            "connection_string": "ga4://analytics.google.com"
        },
        {
            "name": "Salesforce CRM",
            "source_type": "salesforce",
            "connection_string": "sf://salesforce.com"
        },
        {
            "name": "PostgreSQL Data Warehouse",
            "source_type": "postgresql",
            "connection_string": "postgresql://warehouse.company.com"
        }
    ]

    for ds_data in data_sources_data:
        data_source = DataSource(
            name=ds_data["name"],
            source_type=ds_data["source_type"],
            connection_string=ds_data["connection_string"]
        )
        db.session.add(data_source)

    db.session.commit()
    print("✅ Created enhanced sample data: 200 customers, 100 products, 1000 orders, 400 reviews!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_enhanced_sample_data()
        print("✅ Enhanced database initialized!")

    print("🚀 Starting Enhanced Songo BI...")
    print("🌐 Access the application at: http://localhost:8088")
    print("🤖 AI Features: Natural Language Queries, Automated Insights")
    print("📊 Power BI-style Analytics with Metabase UI")
    app.run(host='0.0.0.0', port=8088, debug=True)
