# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
NetSuite background tasks for Songo BI.
"""

import logging
from datetime import datetime, timedelta
from typing import List

from celery import shared_task

from songo_bi.extensions import db
from songo_bi.models.netsuite import NetSuiteDataSource, NetSuiteQuery, NetSuiteRefreshLog
from songo_bi.services.netsuite import NetSuiteService

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def refresh_data_source_task(self, data_source_id: int):
    """
    Background task to refresh NetSuite data source.
    
    Args:
        data_source_id: NetSuite data source ID
    """
    try:
        logger.info(f"Starting refresh for NetSuite data source {data_source_id}")
        
        service = NetSuiteService()
        success, error = service.refresh_data_source(data_source_id)
        
        if success:
            logger.info(f"Successfully refreshed NetSuite data source {data_source_id}")
            return {"status": "success", "data_source_id": data_source_id}
        else:
            logger.error(f"Failed to refresh NetSuite data source {data_source_id}: {error}")
            return {"status": "failed", "data_source_id": data_source_id, "error": error}
            
    except Exception as e:
        logger.error(f"NetSuite refresh task failed: {e}")
        self.retry(countdown=60, max_retries=3)


@shared_task
def auto_refresh_data_sources():
    """
    Automatically refresh NetSuite data sources that are due for refresh.
    """
    try:
        logger.info("Starting auto-refresh of NetSuite data sources")
        
        # Find data sources that need refreshing
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        
        data_sources = NetSuiteDataSource.query.filter(
            NetSuiteDataSource.auto_refresh == True,
            (NetSuiteDataSource.last_refresh.is_(None) | 
             (NetSuiteDataSource.last_refresh < cutoff_time))
        ).all()
        
        refreshed_count = 0
        
        for data_source in data_sources:
            try:
                # Schedule individual refresh task
                refresh_data_source_task.delay(data_source.id)
                refreshed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to schedule refresh for data source {data_source.id}: {e}")
        
        logger.info(f"Scheduled refresh for {refreshed_count} NetSuite data sources")
        return {"refreshed_count": refreshed_count}
        
    except Exception as e:
        logger.error(f"Auto-refresh task failed: {e}")
        return {"error": str(e)}


@shared_task(bind=True)
def execute_netsuite_query_task(self, query_id: int):
    """
    Background task to execute NetSuite query.
    
    Args:
        query_id: NetSuite query ID
    """
    try:
        logger.info(f"Executing NetSuite query {query_id}")
        
        service = NetSuiteService()
        success, df, error = service.execute_query(query_id)
        
        if success:
            logger.info(f"Successfully executed NetSuite query {query_id}")
            return {
                "status": "success", 
                "query_id": query_id,
                "row_count": len(df) if df is not None else 0
            }
        else:
            logger.error(f"Failed to execute NetSuite query {query_id}: {error}")
            return {"status": "failed", "query_id": query_id, "error": error}
            
    except Exception as e:
        logger.error(f"NetSuite query execution task failed: {e}")
        self.retry(countdown=30, max_retries=2)


@shared_task
def cleanup_old_refresh_logs():
    """Clean up old NetSuite refresh logs."""
    try:
        # Delete logs older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        deleted_count = NetSuiteRefreshLog.query.filter(
            NetSuiteRefreshLog.start_time < cutoff_date
        ).delete()
        
        db.session.commit()
        
        logger.info(f"Cleaned up {deleted_count} old NetSuite refresh logs")
        return {"deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        db.session.rollback()
        return {"error": str(e)}


@shared_task
def refresh_netsuite_data():
    """
    Scheduled task to refresh all active NetSuite data sources.
    This is the main scheduled task that runs periodically.
    """
    try:
        logger.info("Starting scheduled NetSuite data refresh")
        
        # Get all active data sources with auto-refresh enabled
        data_sources = NetSuiteDataSource.query.filter_by(
            auto_refresh=True
        ).join(NetSuiteDataSource.connection).filter_by(
            is_active=True
        ).all()
        
        total_refreshed = 0
        total_failed = 0
        
        for data_source in data_sources:
            try:
                # Check if refresh is due
                if data_source.last_refresh:
                    time_since_refresh = datetime.utcnow() - data_source.last_refresh
                    if time_since_refresh.total_seconds() < data_source.refresh_interval:
                        continue  # Not due for refresh yet
                
                # Schedule refresh task
                refresh_data_source_task.delay(data_source.id)
                total_refreshed += 1
                
            except Exception as e:
                logger.error(f"Failed to schedule refresh for data source {data_source.id}: {e}")
                total_failed += 1
        
        logger.info(f"Scheduled refresh for {total_refreshed} data sources, {total_failed} failed")
        
        return {
            "total_refreshed": total_refreshed,
            "total_failed": total_failed,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Scheduled NetSuite refresh failed: {e}")
        return {"error": str(e)}
