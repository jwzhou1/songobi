# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Celery application configuration for Songo BI.
"""

import os
from celery import Celery

from songo_bi.config import get_config

# Get configuration
config = get_config()

# Create Celery app
app = Celery('songo_bi')

# Configure Celery
app.conf.update(
    broker_url=config.REDIS_URL,
    result_backend=config.REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_annotations={
        '*': {'rate_limit': '100/s'}
    },
    beat_schedule={
        'netsuite-auto-refresh': {
            'task': 'songo_bi.tasks.netsuite.auto_refresh_data_sources',
            'schedule': 300.0,  # Every 5 minutes
        },
        'cleanup-old-queries': {
            'task': 'songo_bi.tasks.maintenance.cleanup_old_queries',
            'schedule': 3600.0,  # Every hour
        },
        'generate-ai-insights': {
            'task': 'songo_bi.tasks.ai.generate_dashboard_insights',
            'schedule': 1800.0,  # Every 30 minutes
        },
    }
)

# Auto-discover tasks
app.autodiscover_tasks([
    'songo_bi.tasks.netsuite',
    'songo_bi.tasks.dashboard', 
    'songo_bi.tasks.ai',
    'songo_bi.tasks.maintenance'
])
