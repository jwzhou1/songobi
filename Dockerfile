# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

FROM python:3.11-slim-bookworm AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    default-libmysqlclient-dev \
    freetds-bin \
    freetds-dev \
    gcc \
    git \
    libaio1 \
    libecpg-dev \
    libffi-dev \
    libldap2-dev \
    libpq-dev \
    libsasl2-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    pkg-config \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r songo && useradd -r -g songo songo

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements/ /app/requirements/
COPY setup.py pyproject.toml /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy application code
COPY . /app/

# Install the application
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/songo_home /app/logs
RUN chown -R songo:songo /app

# Development target
FROM base AS dev
RUN pip install --no-cache-dir -r requirements/development.txt
USER songo
EXPOSE 8088
CMD ["gunicorn", "--bind", "0.0.0.0:8088", "--workers", "4", "--timeout", "120", "songo_bi.app:create_app()"]

# Production target
FROM base AS prod
USER songo
EXPOSE 8088
CMD ["gunicorn", "--bind", "0.0.0.0:8088", "--workers", "4", "--worker-class", "gevent", "--timeout", "120", "songo_bi.app:create_app()"]

# Frontend build stage
FROM node:20.18.1-slim AS songo-frontend

WORKDIR /app

# Copy package files
COPY songo-bi-frontend/package*.json ./
RUN npm ci

# Copy frontend source
COPY songo-bi-frontend/ ./

# Build frontend
RUN npm run build

# Final stage combining backend and frontend
FROM prod AS final
COPY --from=songo-frontend /app/dist /app/songo_bi/static/assets/
USER songo
