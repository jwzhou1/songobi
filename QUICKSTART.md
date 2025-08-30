# Songo BI Quick Start Guide

Get your Songo BI platform up and running in minutes!

## Prerequisites

- Docker and Docker Compose
- Git
- OpenAI API key (for AI chatbot)
- NetSuite credentials (for NetSuite integration)

## 🚀 Quick Setup

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/your-org/songo-bi.git
cd songo-bi

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your credentials:

```bash
# Required: OpenAI API Key for chatbot
OPENAI_API_KEY=your_openai_api_key_here

# Optional: NetSuite credentials for integration
NETSUITE_ACCOUNT_ID=your_account_id
NETSUITE_CONSUMER_KEY=your_consumer_key
NETSUITE_CONSUMER_SECRET=your_consumer_secret
NETSUITE_TOKEN_ID=your_token_id
NETSUITE_TOKEN_SECRET=your_token_secret

# Database (uses Docker defaults)
DATABASE_URL=postgresql://songo:songo_password@db:5432/songo_bi
REDIS_URL=redis://redis:6379/0
```

### 3. Start the Platform

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Initialize Database

```bash
# Initialize database and create admin user
docker-compose exec songo-bi songo-bi db upgrade
docker-compose exec songo-bi songo-bi init
```

### 5. Access the Platform

- **Main Application**: http://localhost:8088
- **Frontend Dev Server**: http://localhost:9000
- **Default Login**: admin / admin

## 🎯 Key Features to Try

### 1. AI Chatbot Assistant

1. Click the chat icon in the bottom right
2. Try these example queries:
   - "Show me sales trends for this month"
   - "Create a chart showing top customers"
   - "Analyze revenue by region"
   - "Help me build a dashboard"

### 2. NetSuite Integration

1. Go to **NetSuite** → **Connections**
2. Add your NetSuite credentials
3. Create data sources for:
   - Customer data
   - Transaction records
   - Item information
4. Set up auto-refresh schedules

### 3. Dashboard Creation

1. Go to **Dashboards** → **New Dashboard**
2. Add charts using the chart builder
3. Use the AI assistant to generate dashboards automatically
4. Share dashboards with your team

### 4. SQL Lab

1. Go to **SQL Lab**
2. Connect to your databases
3. Write and execute SQL queries
4. Save queries for reuse
5. Create charts from query results

## 🔧 Development Setup

### Backend Development

```bash
# Install Python dependencies
pip install -r requirements/development.txt

# Run backend in development mode
export FLASK_ENV=development
flask run --debug

# Run tests
pytest tests/

# Code formatting
black songo_bi/
isort songo_bi/
```

### Frontend Development

```bash
# Install Node.js dependencies
cd songo-bi-frontend
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f songo-bi

# Restart a service
docker-compose restart songo-bi

# Stop all services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

## 📊 Sample Data

Load sample data for testing:

```bash
docker-compose exec songo-bi songo-bi load-examples
```

This creates:
- Sample database connection
- Sample sales data table
- Example dashboard with charts
- Demo NetSuite connection (inactive)

## 🔐 Security Configuration

### Production Security

Update `.env` for production:

```bash
# Generate secure secret key
SECRET_KEY=your-very-secure-secret-key

# Enable security features
WTF_CSRF_ENABLED=true
SESSION_COOKIE_SECURE=true
TALISMAN_ENABLED=true

# Set production database
DATABASE_URL=postgresql://user:pass@prod-db:5432/songo_bi
```

### User Management

```bash
# Create admin user
docker-compose exec songo-bi songo-bi fab create-admin

# List users
docker-compose exec songo-bi songo-bi fab list-users
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose logs db
   
   # Restart database
   docker-compose restart db
   ```

2. **Frontend Build Errors**
   ```bash
   # Clear node modules and reinstall
   cd songo-bi-frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **NetSuite Connection Issues**
   - Verify credentials in `.env`
   - Check NetSuite account permissions
   - Test connection via API: `/api/v1/netsuite/connections/{id}/test`

4. **AI Chatbot Not Working**
   - Verify OpenAI API key in `.env`
   - Check API quota and billing
   - Review chatbot logs: `docker-compose logs songo-chatbot`

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f songo-bi
docker-compose logs -f songo-worker
docker-compose logs -f songo-chatbot

# Access container shell
docker-compose exec songo-bi bash
```

## 📈 Performance Optimization

### Database Optimization
- Enable query caching
- Add database indexes
- Configure connection pooling

### Frontend Optimization
- Enable code splitting
- Optimize bundle size
- Use CDN for static assets

### Caching Strategy
- Redis for session caching
- Query result caching
- Dashboard metadata caching

## 🔄 Data Refresh

### Manual Refresh
```bash
# Refresh specific NetSuite data source
docker-compose exec songo-bi songo-bi netsuite refresh-data --data-source-id 1

# Test NetSuite connection
docker-compose exec songo-bi songo-bi netsuite test-connection --connection-id 1
```

### Automated Refresh
- Configured via Celery beat scheduler
- Default: Every 30 minutes
- Customizable per data source
- Monitoring via refresh logs

## 📚 Next Steps

1. **Customize Branding**: Update logos, colors, and themes
2. **Add Data Sources**: Connect your databases and APIs
3. **Create Dashboards**: Build your first business dashboards
4. **Train AI**: Customize chatbot responses for your domain
5. **Deploy to Production**: Use provided CI/CD pipeline

## 🆘 Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Community**: Join our Slack channel

Happy analyzing with Songo BI! 🎉
