# Songo BI

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/license/apache-2-0)
[![Build Status](https://github.com/your-org/songo-bi/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/songo-bi/actions)

<picture width="500">
  <img
    width="600"
    src="./docs/assets/songo-bi-logo.svg"
    alt="Songo BI logo"
  />
</picture>

A modern, enterprise-ready business intelligence web application with AI-powered analytics and NetSuite integration.

## Why Songo BI?

Songo BI is a comprehensive data exploration and visualization platform built on modern web technologies. It provides enterprise-grade business intelligence capabilities with advanced AI integration and seamless NetSuite connectivity.

### Key Features

- **AI-Powered Analytics** - Built-in ChatGPT-like assistant for data analysis and insights
- **NetSuite Integration** - Direct web query integration with automatic refresh capabilities
- **No-Code Interface** - Build charts and dashboards without coding
- **Advanced SQL Editor** - Powerful web-based SQL editor for complex queries
- **Real-time Data** - Live data refresh from NetSuite and other sources
- **Beautiful Visualizations** - Wide array of charts and visualization types
- **Enterprise Security** - Role-based access control and authentication
- **Cloud-Native** - Designed for scalability and modern deployment
- **CI/CD Ready** - Built-in GitHub Actions for automated deployment

## Architecture

Songo BI is built with:

- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: React with TypeScript and Ant Design
- **Database**: PostgreSQL with Redis caching
- **AI Integration**: OpenAI API for chatbot functionality
- **NetSuite**: REST API integration for data synchronization
- **Containerization**: Docker and Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20.18.1+
- Python 3.10+
- Git

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/songo-bi.git
cd songo-bi
```

2. Copy environment configuration:
```bash
cp docker/.env.example docker/.env
```

3. Start the development environment:
```bash
docker-compose up -d
```

4. Initialize the database:
```bash
docker-compose exec songo-bi songo-bi db upgrade
docker-compose exec songo-bi songo-bi init
```

5. Access the application:
- Main application: http://localhost:8088
- Frontend dev server: http://localhost:9000

### Production Deployment

See [deployment documentation](./docs/deployment.md) for production setup instructions.

## Features

### NetSuite Integration

- Direct connection to NetSuite web queries
- Automatic data refresh scheduling
- Real-time synchronization
- Custom query builder for NetSuite data

### AI-Powered Chatbot

- Natural language queries about your data
- Automated chart and dashboard generation
- Data insights and recommendations
- Integration with all dashboard components

### Advanced Analytics

- Interactive dashboards
- Custom metrics and dimensions
- Advanced filtering and drill-down
- Export capabilities (PDF, Excel, CSV)

## Development

### Backend Development

```bash
# Install Python dependencies
pip install -r requirements/development.txt

# Run backend tests
pytest tests/

# Start development server
flask run --debug
```

### Frontend Development

```bash
# Install Node.js dependencies
cd songo-bi-frontend
npm install

# Start development server
npm run dev

# Run frontend tests
npm test

# Build for production
npm run build
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Support

- Documentation: [docs.songo-bi.com](https://docs.songo-bi.com)
- Issues: [GitHub Issues](https://github.com/your-org/songo-bi/issues)
- Community: [Slack Channel](https://songo-bi.slack.com)

## Roadmap

- [ ] Advanced AI analytics features
- [ ] Additional data source connectors
- [ ] Mobile application
- [ ] Advanced security features
- [ ] Multi-tenant support
