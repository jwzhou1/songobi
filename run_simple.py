#!/usr/bin/env python3
"""
Simplified Songo BI application without Flask-AppBuilder.
This version demonstrates the core functionality while avoiding compatibility issues.
"""

import os
from flask import Flask, render_template_string, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songo_bi_simple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Sample Database Models (inspired by Metabase's sample data)
class People(db.Model):
    """Customer information table."""
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
    source = db.Column(db.String(50))  # Organic, Google, Facebook, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'city': self.city,
            'state': self.state,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Products(db.Model):
    """Product catalog table."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    vendor = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float)  # 1-5 rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'vendor': self.vendor,
            'price': self.price,
            'rating': self.rating
        }

class Orders(db.Model):
    """Orders transaction table."""
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
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total': self.total,
            'discount': self.discount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Reviews(db.Model):
    """Product reviews table."""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    reviewer = db.Column(db.String(100))
    rating = db.Column(db.Integer)  # 1-5 stars
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    product = db.relationship('Products', backref='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'reviewer': self.reviewer,
            'rating': self.rating,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Dashboard and BI Models
class Dashboard(db.Model):
    """BI Dashboard model."""
    __tablename__ = 'dashboards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

class DataSource(db.Model):
    """Data source connections."""
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

# HTML template for the main page
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Songo BI - Business Intelligence Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8fafc;
            color: #2d3748;
            line-height: 1.6;
        }
        .navbar {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .navbar h1 { font-size: 1.8rem; font-weight: 600; }
        .navbar p { opacity: 0.9; margin-top: 0.25rem; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            transition: transform 0.2s, box-shadow 0.2s;
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
        }
        .chart-canvas {
            position: relative;
            height: 300px;
            margin: 1rem 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
        .btn {
            background: #4f46e5;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn:hover {
            background: #4338ca;
            transform: translateY(-1px);
        }
        .btn-secondary {
            background: #6b7280;
        }
        .btn-secondary:hover {
            background: #4b5563;
        }
        .status { color: #10b981; font-weight: 600; }
        .loading {
            text-align: center;
            color: #6b7280;
            font-style: italic;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
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
        .tabs {
            display: flex;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }
        .tab {
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        .tab.active {
            border-bottom-color: #4f46e5;
            color: #4f46e5;
            font-weight: 600;
        }
        .tab:hover {
            background: #f8fafc;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div>
            <h1>📊 Songo BI</h1>
            <p>Modern Business Intelligence Platform • <span class="status">Live Data</span></p>
        </div>
    </nav>

    <div class="container">
        <!-- Key Metrics Row -->
        <div class="dashboard-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 2rem;">
            <div class="metric-card">
                <div class="metric-value" id="total-revenue">$0</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-orders">0</div>
                <div class="metric-label">Total Orders</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-customers">0</div>
                <div class="metric-label">Total Customers</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="avg-order-value">$0</div>
                <div class="metric-label">Avg Order Value</div>
            </div>
        </div>

        <!-- Charts Dashboard -->
        <div class="dashboard-grid">
            <!-- Sales Trend Chart -->
            <div class="chart-container" style="grid-column: span 2;">
                <div class="chart-header">
                    <h3 class="chart-title">📈 Sales Trend (Last 30 Days)</h3>
                    <button class="btn btn-secondary" onclick="refreshChart('sales-trend')">Refresh</button>
                </div>
                <div class="chart-canvas">
                    <canvas id="sales-trend-chart"></canvas>
                </div>
            </div>

            <!-- Product Categories Pie Chart -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">🛍️ Sales by Category</h3>
                    <button class="btn btn-secondary" onclick="refreshChart('category-pie')">Refresh</button>
                </div>
                <div class="chart-canvas">
                    <canvas id="category-pie-chart"></canvas>
                </div>
            </div>

            <!-- Customer Acquisition Sources -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">👥 Customer Sources</h3>
                    <button class="btn btn-secondary" onclick="refreshChart('customer-sources')">Refresh</button>
                </div>
                <div class="chart-canvas">
                    <canvas id="customer-sources-chart"></canvas>
                </div>
            </div>

            <!-- Top Products Bar Chart -->
            <div class="chart-container" style="grid-column: span 2;">
                <div class="chart-header">
                    <h3 class="chart-title">🏆 Top Selling Products</h3>
                    <button class="btn btn-secondary" onclick="refreshChart('top-products')">Refresh</button>
                </div>
                <div class="chart-canvas">
                    <canvas id="top-products-chart"></canvas>
                </div>
            </div>

            <!-- Geographic Distribution -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">🌍 Geographic Distribution</h3>
                    <button class="btn btn-secondary" onclick="refreshChart('geographic')">Refresh</button>
                </div>
                <div class="chart-canvas">
                    <canvas id="geographic-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- Data Explorer Section -->
        <div class="chart-container">
            <div class="chart-header">
                <h3 class="chart-title">🔍 Data Explorer</h3>
                <div>
                    <button class="btn" onclick="exportData()">Export Data</button>
                    <button class="btn btn-secondary" onclick="refreshAllCharts()">Refresh All</button>
                </div>
            </div>

            <div class="tabs">
                <div class="tab active" onclick="switchTab('customers')">👥 Customers</div>
                <div class="tab" onclick="switchTab('products')">🛍️ Products</div>
                <div class="tab" onclick="switchTab('orders')">📦 Orders</div>
                <div class="tab" onclick="switchTab('reviews')">⭐ Reviews</div>
            </div>

            <div id="customers-tab" class="tab-content active">
                <div id="customers-table" class="loading">Loading customer data...</div>
            </div>
            <div id="products-tab" class="tab-content">
                <div id="products-table" class="loading">Loading product data...</div>
            </div>
            <div id="orders-tab" class="tab-content">
                <div id="orders-table" class="loading">Loading order data...</div>
            </div>
            <div id="reviews-tab" class="tab-content">
                <div id="reviews-table" class="loading">Loading review data...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Global chart instances
        let charts = {};

        // Initialize dashboard on page load
        window.onload = function() {
            loadMetrics();
            initializeCharts();
            loadTableData('customers');
        };

        // Load key metrics
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

        // Initialize all charts
        function initializeCharts() {
            createSalesTrendChart();
            createCategoryPieChart();
            createCustomerSourcesChart();
            createTopProductsChart();
            createGeographicChart();
        }

        // Sales Trend Line Chart
        function createSalesTrendChart() {
            const ctx = document.getElementById('sales-trend-chart').getContext('2d');

            // Generate sample daily sales data for last 30 days
            const labels = [];
            const salesData = [];
            const today = new Date();

            for (let i = 29; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
                salesData.push(Math.floor(Math.random() * 5000) + 1000);
            }

            charts['sales-trend'] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Daily Sales ($)',
                        data: salesData,
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
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
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }

        // Category Pie Chart
        function createCategoryPieChart() {
            fetch('/api/analytics/product-performance')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('category-pie-chart').getContext('2d');

                    charts['category-pie'] = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: data.by_category.map(item => item.category),
                            datasets: [{
                                data: data.by_category.map(item => item.product_count),
                                backgroundColor: [
                                    '#4f46e5', '#7c3aed', '#ec4899', '#f59e0b', '#10b981'
                                ],
                                borderWidth: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: { padding: 20 }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading category chart:', error));
        }

        // Customer Sources Chart
        function createCustomerSourcesChart() {
            fetch('/api/analytics/customer-insights')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('customer-sources-chart').getContext('2d');

                    charts['customer-sources'] = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: data.by_source.map(item => item.source),
                            datasets: [{
                                label: 'Customers',
                                data: data.by_source.map(item => item.count),
                                backgroundColor: '#7c3aed',
                                borderRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading customer sources chart:', error));
        }

        // Top Products Bar Chart
        function createTopProductsChart() {
            fetch('/api/analytics/sales-summary')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('top-products-chart').getContext('2d');

                    charts['top-products'] = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: data.top_products.map(item => item.name.substring(0, 20) + '...'),
                            datasets: [{
                                label: 'Revenue ($)',
                                data: data.top_products.map(item => item.revenue),
                                backgroundColor: '#10b981',
                                borderRadius: 6
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
                                    ticks: {
                                        callback: function(value) {
                                            return '$' + value.toLocaleString();
                                        }
                                    }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading top products chart:', error));
        }

        // Geographic Distribution Chart
        function createGeographicChart() {
            fetch('/api/analytics/customer-insights')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('geographic-chart').getContext('2d');

                    charts['geographic'] = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: data.by_state.slice(0, 8).map(item => item.state),
                            datasets: [{
                                label: 'Customers',
                                data: data.by_state.slice(0, 8).map(item => item.count),
                                backgroundColor: '#f59e0b',
                                borderRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading geographic chart:', error));
        }

        // Customer Sources Chart
        function createCustomerSourcesChart() {
            fetch('/api/analytics/customer-insights')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('customer-sources-chart').getContext('2d');

                    charts['customer-sources'] = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: data.by_source.map(item => item.source),
                            datasets: [{
                                label: 'Customers',
                                data: data.by_source.map(item => item.count),
                                backgroundColor: '#7c3aed',
                                borderRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading customer sources chart:', error));
        }

        // Tab switching functionality
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');

            // Add active class to clicked tab
            event.target.classList.add('active');

            // Load data for the selected tab
            loadTableData(tabName);
        }

        // Load table data
        function loadTableData(tableName) {
            const endpoint = tableName === 'customers' ? 'people' : tableName;

            fetch(`/api/data/${endpoint}?per_page=10`)
                .then(response => response.json())
                .then(data => {
                    const tableId = tableName + '-table';
                    const tableElement = document.getElementById(tableId);

                    if (data.data.length === 0) {
                        tableElement.innerHTML = '<p>No data available</p>';
                        return;
                    }

                    // Create table HTML
                    const headers = Object.keys(data.data[0]);
                    let tableHTML = '<table class="data-table"><thead><tr>';

                    headers.forEach(header => {
                        tableHTML += `<th>${header.replace('_', ' ').toUpperCase()}</th>`;
                    });
                    tableHTML += '</tr></thead><tbody>';

                    data.data.forEach(row => {
                        tableHTML += '<tr>';
                        headers.forEach(header => {
                            let value = row[header];
                            if (typeof value === 'number' && header.includes('price') || header.includes('total')) {
                                value = '$' + value.toFixed(2);
                            } else if (typeof value === 'string' && value.includes('T')) {
                                value = new Date(value).toLocaleDateString();
                            }
                            tableHTML += `<td>${value || 'N/A'}</td>`;
                        });
                        tableHTML += '</tr>';
                    });

                    tableHTML += '</tbody></table>';
                    tableHTML += `<p style="margin-top: 1rem; color: #6b7280;">Showing ${data.data.length} of ${data.total} records</p>`;

                    tableElement.innerHTML = tableHTML;
                })
                .catch(error => {
                    console.error('Error loading table data:', error);
                    document.getElementById(tableName + '-table').innerHTML = '<p>Error loading data</p>';
                });
        }

        // Refresh individual charts
        function refreshChart(chartName) {
            if (charts[chartName]) {
                charts[chartName].destroy();
            }

            switch(chartName) {
                case 'sales-trend':
                    createSalesTrendChart();
                    break;
                case 'category-pie':
                    createCategoryPieChart();
                    break;
                case 'customer-sources':
                    createCustomerSourcesChart();
                    break;
                case 'top-products':
                    createTopProductsChart();
                    break;
                case 'geographic':
                    createGeographicChart();
                    break;
            }
        }

        // Refresh all charts and metrics
        function refreshAllCharts() {
            loadMetrics();
            Object.keys(charts).forEach(chartName => {
                refreshChart(chartName);
            });
        }

        // Export data functionality
        function exportData() {
            const currentTab = document.querySelector('.tab.active').textContent.trim();
            alert(`📊 Export functionality ready!\\n\\nCurrent view: ${currentTab}\\n\\nThis would export the current dataset to CSV/Excel format.`);
        }
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    return render_template_string(MAIN_TEMPLATE)

@app.route('/api/dashboards')
def get_dashboards():
    dashboards = Dashboard.query.all()
    return jsonify([d.to_dict() for d in dashboards])

@app.route('/api/datasources')
def get_datasources():
    sources = DataSource.query.all()
    return jsonify([s.to_dict() for s in sources])

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'running',
        'version': '0.1.0',
        'database': 'sqlite',
        'features': ['dashboards', 'ai-analytics', 'netsuite', 'sql-lab'],
        'data_counts': {
            'customers': People.query.count(),
            'products': Products.query.count(),
            'orders': Orders.query.count(),
            'reviews': Reviews.query.count()
        }
    })

@app.route('/api/analytics/sales-summary')
def get_sales_summary():
    """Get sales summary analytics."""
    from sqlalchemy import func

    # Total revenue
    total_revenue = db.session.query(func.sum(Orders.total)).scalar() or 0

    # Total orders
    total_orders = Orders.query.count()

    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # Top selling products
    top_products = db.session.query(
        Products.title,
        func.sum(Orders.quantity).label('total_sold'),
        func.sum(Orders.total).label('revenue')
    ).join(Orders).group_by(Products.id, Products.title).order_by(
        func.sum(Orders.total).desc()
    ).limit(5).all()

    return jsonify({
        'total_revenue': round(total_revenue, 2),
        'total_orders': total_orders,
        'avg_order_value': round(avg_order_value, 2),
        'top_products': [
            {
                'name': product.title,
                'units_sold': int(product.total_sold),
                'revenue': round(product.revenue, 2)
            }
            for product in top_products
        ]
    })

@app.route('/api/analytics/customer-insights')
def get_customer_insights():
    """Get customer analytics."""
    from sqlalchemy import func

    # Customer by source
    customers_by_source = db.session.query(
        People.source,
        func.count(People.id).label('count')
    ).group_by(People.source).all()

    # Customer by state
    customers_by_state = db.session.query(
        People.state,
        func.count(People.id).label('count')
    ).group_by(People.state).order_by(func.count(People.id).desc()).limit(10).all()

    return jsonify({
        'by_source': [
            {'source': item.source, 'count': item.count}
            for item in customers_by_source
        ],
        'by_state': [
            {'state': item.state, 'count': item.count}
            for item in customers_by_state
        ]
    })

@app.route('/api/analytics/product-performance')
def get_product_performance():
    """Get product performance analytics."""
    from sqlalchemy import func

    # Products by category
    products_by_category = db.session.query(
        Products.category,
        func.count(Products.id).label('product_count'),
        func.avg(Products.rating).label('avg_rating'),
        func.avg(Products.price).label('avg_price')
    ).group_by(Products.category).all()

    # Top rated products
    top_rated = Products.query.order_by(Products.rating.desc()).limit(10).all()

    return jsonify({
        'by_category': [
            {
                'category': item.category,
                'product_count': item.product_count,
                'avg_rating': round(item.avg_rating, 2) if item.avg_rating else 0,
                'avg_price': round(item.avg_price, 2) if item.avg_price else 0
            }
            for item in products_by_category
        ],
        'top_rated': [product.to_dict() for product in top_rated]
    })

@app.route('/api/data/people')
def get_people():
    """Get people data with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    people = People.query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'data': [person.to_dict() for person in people.items],
        'total': people.total,
        'pages': people.pages,
        'current_page': page
    })

@app.route('/api/data/products')
def get_products():
    """Get products data with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')

    query = Products.query
    if category:
        query = query.filter(Products.category == category)

    products = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'data': [product.to_dict() for product in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    })

@app.route('/api/data/orders')
def get_orders():
    """Get orders data with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    orders = Orders.query.order_by(Orders.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'data': [order.to_dict() for order in orders.items],
        'total': orders.total,
        'pages': orders.pages,
        'current_page': page
    })

def create_sample_data():
    """Create comprehensive sample data inspired by Metabase's sample database."""
    import random
    from datetime import datetime, timedelta

    # Check if data already exists
    if People.query.count() > 0:
        print("📊 Sample data already exists!")
        return

    print("🔄 Creating sample data...")

    # Sample data lists
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Chris", "Emma", "Alex", "Maria",
                   "Robert", "Jennifer", "Michael", "Jessica", "William", "Ashley", "James", "Amanda"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio",
              "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "NC", "WA", "CO", "GA", "MI", "OR"]
    sources = ["Organic", "Google", "Facebook", "Twitter", "Affiliate", "Email", "Direct"]

    # Create People (customers)
    people_list = []
    for i in range(100):
        person = People(
            name=f"{random.choice(first_names)} {random.choice(last_names)}",
            email=f"user{i+1}@example.com",
            address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Elm Dr'])}",
            city=random.choice(cities),
            state=random.choice(states),
            zip_code=f"{random.randint(10000, 99999)}",
            latitude=round(random.uniform(25.0, 49.0), 6),
            longitude=round(random.uniform(-125.0, -66.0), 6),
            birth_date=datetime.now().date() - timedelta(days=random.randint(6570, 21900)),  # 18-60 years old
            source=random.choice(sources),
            created_at=datetime.now() - timedelta(days=random.randint(1, 365))
        )
        people_list.append(person)
        db.session.add(person)

    # Create Products
    categories = ["Widget", "Gadget", "Gizmo", "Doohickey"]
    vendors = ["Acme Corp", "Global Industries", "Tech Solutions", "Premium Products", "Quality Goods"]
    adjectives = ["Premium", "Deluxe", "Standard", "Economy", "Professional", "Advanced", "Basic"]
    materials = ["Steel", "Aluminum", "Plastic", "Wood", "Carbon", "Titanium", "Copper"]

    products_list = []
    for i in range(50):
        product = Products(
            title=f"{random.choice(adjectives)} {random.choice(materials)} {random.choice(categories)}",
            category=random.choice(categories),
            vendor=random.choice(vendors),
            price=round(random.uniform(10.0, 500.0), 2),
            rating=round(random.uniform(3.0, 5.0), 1),
            created_at=datetime.now() - timedelta(days=random.randint(30, 730))
        )
        products_list.append(product)
        db.session.add(product)

    db.session.commit()  # Commit to get IDs

    # Create Orders (transactions)
    for i in range(500):
        order = Orders(
            user_id=random.choice(people_list).id,
            product_id=random.choice(products_list).id,
            quantity=random.randint(1, 5),
            total=round(random.uniform(15.0, 1000.0), 2),
            discount=round(random.uniform(0.0, 50.0), 2) if random.random() > 0.7 else 0.0,
            tax=round(random.uniform(1.0, 80.0), 2),
            created_at=datetime.now() - timedelta(days=random.randint(1, 365))
        )
        db.session.add(order)

    # Create Reviews
    review_bodies = [
        "Great product! Highly recommended.",
        "Good quality for the price.",
        "Excellent customer service and fast delivery.",
        "Product works as expected.",
        "Could be better, but decent overall.",
        "Amazing quality! Will buy again.",
        "Fast shipping and great packaging.",
        "Perfect for my needs.",
        "Good value for money.",
        "Outstanding product quality!"
    ]

    for i in range(200):
        review = Reviews(
            product_id=random.choice(products_list).id,
            reviewer=f"{random.choice(first_names)} {random.choice(last_names)}",
            rating=random.randint(1, 5),
            body=random.choice(review_bodies),
            created_at=datetime.now() - timedelta(days=random.randint(1, 365))
        )
        db.session.add(review)

    # Create Dashboards
    dashboards_data = [
        {
            "title": "E-commerce Analytics Dashboard",
            "description": "Comprehensive overview of sales performance, customer insights, and product analytics"
        },
        {
            "title": "Customer Insights Dashboard",
            "description": "Deep dive into customer behavior, demographics, and purchasing patterns"
        },
        {
            "title": "Product Performance Dashboard",
            "description": "Product sales trends, ratings analysis, and inventory insights"
        },
        {
            "title": "Revenue Analytics Dashboard",
            "description": "Financial metrics, revenue trends, and profitability analysis"
        }
    ]

    for dash_data in dashboards_data:
        dashboard = Dashboard(
            title=dash_data["title"],
            description=dash_data["description"]
        )
        db.session.add(dashboard)

    # Create Data Sources
    data_sources_data = [
        {
            "name": "Sample E-commerce Database",
            "source_type": "sqlite",
            "connection_string": "sqlite:///songo_bi_simple.db"
        },
        {
            "name": "NetSuite Production",
            "source_type": "netsuite",
            "connection_string": "netsuite://production.netsuite.com"
        },
        {
            "name": "Google Analytics",
            "source_type": "analytics",
            "connection_string": "ga://analytics.google.com"
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
    print("✅ Created comprehensive sample data with 100 customers, 50 products, 500 orders, and 200 reviews!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
        print("✅ Database initialized with sample data!")
    
    print("🚀 Starting Songo BI (Simplified Version)...")
    print("🌐 Access the application at: http://localhost:8088")
    app.run(host='0.0.0.0', port=8088, debug=True)
