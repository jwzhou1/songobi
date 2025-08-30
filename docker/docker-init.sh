#!/bin/bash
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

set -e

# Initialization script for Songo BI

echo "Initializing Songo BI..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 1
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done
echo "Redis is ready!"

# Set up Python path
export PYTHONPATH="/app:$PYTHONPATH"

# Change to app directory
cd /app

# Install the application in development mode
echo "Installing Songo BI..."
pip install -e .

# Initialize database
echo "Initializing database..."
songo-bi db upgrade

# Create admin user if it doesn't exist
echo "Creating admin user..."
songo-bi fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@songo-bi.com \
  --password admin || true

# Initialize roles and permissions
echo "Initializing roles and permissions..."
songo-bi init

# Load sample data if in development
if [ "$FLASK_ENV" = "development" ]; then
  echo "Loading sample data..."
  songo-bi load-examples || true
fi

echo "Songo BI initialization complete!"
