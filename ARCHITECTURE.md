# Songo BI Architecture Overview

## Project Structure

Songo BI is a modern business intelligence platform built with a microservices architecture, inspired by Apache Superset but enhanced with AI capabilities and NetSuite integration.

## Core Components

### Backend (Python/Flask)
```
songo_bi/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── extensions.py          # Flask extensions initialization
├── models/                # Database models
│   ├── core.py           # Core models (User, Database, Table, Query)
│   ├── dashboard.py      # Dashboard and chart models
│   ├── netsuite.py       # NetSuite integration models
│   └── chatbot.py        # AI chatbot models
├── services/              # Business logic services
│   ├── dashboard.py      # Dashboard management
│   ├── netsuite.py       # NetSuite integration
│   ├── chatbot.py        # AI chatbot service
│   └── data.py           # Data processing service
├── views/                 # API endpoints and web views
│   ├── api.py            # REST API endpoints
│   ├── core.py           # Core web views
│   ├── dashboard.py      # Dashboard views
│   ├── netsuite.py       # NetSuite API endpoints
│   └── chatbot.py        # Chatbot API endpoints
├── tasks/                 # Background tasks (Celery)
│   ├── celery_app.py     # Celery configuration
│   ├── netsuite.py       # NetSuite background tasks
│   └── ai.py             # AI processing tasks
└── cli/                   # Command-line interface
    ├── main.py           # Main CLI entry point
    └── commands.py       # CLI command implementations
```

### Frontend (React/TypeScript)
```
songo-bi-frontend/
├── src/
│   ├── components/        # React components
│   │   ├── Layout/       # Application layout
│   │   ├── Chat/         # AI chatbot interface
│   │   ├── Charts/       # Chart visualization components
│   │   └── Common/       # Shared components
│   ├── pages/            # Page components
│   │   ├── Dashboard/    # Dashboard pages
│   │   ├── SQLLab/       # SQL editor
│   │   ├── NetSuite/     # NetSuite management
│   │   └── Login/        # Authentication
│   ├── store/            # Redux state management
│   │   └── slices/       # Redux slices
│   ├── services/         # API services
│   ├── hooks/            # Custom React hooks
│   ├── types/            # TypeScript definitions
│   └── utils/            # Utility functions
├── public/               # Static assets
└── webpack.config.js     # Build configuration
```

## Key Features Implemented

### 1. NetSuite Integration ✅
- **NetSuite Connection Management**: Secure OAuth-based connections
- **Web Query Support**: Execute NetSuite searches and SuiteQL queries
- **Auto-Refresh**: Scheduled data synchronization every 30 minutes
- **Real-time Data**: Live data refresh capabilities
- **Background Processing**: Celery tasks for data synchronization

### 2. AI-Powered Chatbot ✅
- **ChatGPT-like Interface**: Natural language interaction
- **Data Analysis**: AI-powered insights and recommendations
- **Auto-Visualization**: Automatic chart generation from queries
- **Dashboard Assistance**: Help with dashboard creation and management
- **Context Awareness**: Understands current dashboard and data context

### 3. Modern BI Platform ✅
- **Interactive Dashboards**: Drag-and-drop dashboard builder
- **Chart Library**: Multiple visualization types (bar, line, pie, table, etc.)
- **SQL Lab**: Advanced SQL editor with syntax highlighting
- **Data Exploration**: Interactive data discovery interface
- **Real-time Updates**: Live data refresh and streaming

### 4. CI/CD Pipeline ✅
- **GitHub Actions**: Automated testing and deployment
- **Multi-stage Pipeline**: Test → Build → Deploy workflow
- **Security Scanning**: Automated vulnerability detection
- **Docker Integration**: Containerized deployment
- **Environment Management**: Staging and production deployments

## Technology Stack

### Backend
- **Framework**: Flask 2.3+ with Flask-AppBuilder
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for session and query caching
- **Task Queue**: Celery with Redis broker
- **AI Integration**: OpenAI API with LangChain
- **NetSuite**: NetSuite SDK with OAuth authentication

### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: Ant Design for components
- **State Management**: Redux Toolkit
- **Charts**: ECharts for data visualization
- **Build Tool**: Webpack 5 with TypeScript support
- **Testing**: Jest with React Testing Library

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Web Server**: Nginx for reverse proxy
- **Process Management**: Gunicorn with Gevent workers
- **Monitoring**: Built-in health checks and logging

## Security Features

- **Authentication**: Flask-AppBuilder security with role-based access
- **Authorization**: Granular permissions for dashboards and data
- **CSRF Protection**: Cross-site request forgery protection
- **Security Headers**: Talisman for security headers
- **Input Validation**: Comprehensive input sanitization
- **API Security**: JWT tokens and rate limiting

## Deployment Options

### Development
```bash
# Using Docker Compose
docker-compose up -d

# Or local development
pip install -r requirements/development.txt
npm install && npm run dev
flask run --debug
```

### Production
- **Docker**: Multi-stage builds with optimized images
- **Kubernetes**: Ready for container orchestration
- **Cloud**: Supports AWS, GCP, Azure deployments
- **Load Balancing**: Nginx configuration included

## Data Flow

1. **NetSuite Data Ingestion**:
   NetSuite → API → Background Tasks → Database → Cache → Frontend

2. **Dashboard Rendering**:
   User Request → API → Data Service → SQL Execution → Chart Rendering

3. **AI Chatbot Interaction**:
   User Message → Chatbot Service → OpenAI API → Response Processing → Frontend

4. **Real-time Updates**:
   Scheduled Tasks → Data Refresh → WebSocket → Frontend Updates

## Configuration

The platform uses environment-based configuration with support for:
- Development, staging, and production environments
- Feature flags for enabling/disabling components
- Flexible database and cache configuration
- Comprehensive logging and monitoring

## Next Steps

The core platform is now established with:
✅ Complete backend architecture
✅ Frontend foundation with React/TypeScript
✅ NetSuite integration framework
✅ AI chatbot infrastructure
✅ CI/CD pipeline configuration
✅ Docker containerization
✅ Database models and migrations

Ready for:
- Frontend component implementation
- NetSuite connector testing
- AI chatbot training and optimization
- Dashboard template creation
- Performance optimization
- Security hardening
