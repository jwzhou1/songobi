#!/bin/bash
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

set -e

# Bootstrap script for Songo BI Docker containers

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

# Run different services based on command
case "$1" in
  "app")
    echo "Starting Songo BI application server..."
    exec gunicorn \
      --bind 0.0.0.0:8088 \
      --workers 4 \
      --worker-class gevent \
      --timeout 120 \
      --keep-alive 2 \
      --max-requests 1000 \
      --max-requests-jitter 100 \
      --preload \
      "songo_bi.app:create_app()"
    ;;
  
  "worker")
    echo "Starting Songo BI Celery worker..."
    exec celery \
      --app=songo_bi.tasks.celery_app:app \
      worker \
      --loglevel=info \
      --concurrency=${CELERYD_CONCURRENCY:-2}
    ;;
  
  "beat")
    echo "Starting Songo BI Celery beat scheduler..."
    exec celery \
      --app=songo_bi.tasks.celery_app:app \
      beat \
      --loglevel=info \
      --schedule=/tmp/celerybeat-schedule
    ;;
  
  "flower")
    echo "Starting Celery Flower monitoring..."
    exec celery \
      --app=songo_bi.tasks.celery_app:app \
      flower \
      --port=5555
    ;;
  
  *)
    echo "Usage: $0 {app|worker|beat|flower}"
    exit 1
    ;;
esac
