# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
NetSuite integration service for Songo BI.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from netsuitesdk import NetSuiteConnection as NSConnection
from requests_oauthlib import OAuth1Session

from songo_bi.extensions import db, cache_manager
from songo_bi.models.netsuite import (
    NetSuiteConnection, NetSuiteDataSource, NetSuiteQuery, NetSuiteRefreshLog
)

logger = logging.getLogger(__name__)


class NetSuiteService:
    """Service for NetSuite integration and data synchronization."""
    
    def __init__(self):
        self.connections = {}  # Cache for active connections
    
    def get_connection(self, connection_id: int) -> Optional[NSConnection]:
        """
        Get or create NetSuite connection.
        
        Args:
            connection_id: NetSuite connection ID
            
        Returns:
            NetSuite connection instance or None
        """
        if connection_id in self.connections:
            return self.connections[connection_id]
        
        connection_config = NetSuiteConnection.query.get(connection_id)
        if not connection_config or not connection_config.is_active:
            return None
        
        try:
            ns_connection = NSConnection(
                account=connection_config.account_id,
                consumer_key=connection_config.consumer_key,
                consumer_secret=connection_config.consumer_secret,
                token_key=connection_config.token_id,
                token_secret=connection_config.token_secret
            )
            
            self.connections[connection_id] = ns_connection
            return ns_connection
            
        except Exception as e:
            logger.error(f"Failed to create NetSuite connection {connection_id}: {e}")
            return None
    
    def test_connection(self, connection_id: int) -> Tuple[bool, Optional[str]]:
        """
        Test NetSuite connection.
        
        Args:
            connection_id: NetSuite connection ID
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            connection = self.get_connection(connection_id)
            if not connection:
                return False, "Failed to establish connection"
            
            # Test with a simple query
            result = connection.suiteql(
                query="SELECT id FROM customer LIMIT 1",
                limit=1
            )
            
            return True, None
            
        except Exception as e:
            logger.error(f"NetSuite connection test failed: {e}")
            return False, str(e)
    
    def execute_query(self, query_id: int) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Execute NetSuite query and return results.
        
        Args:
            query_id: NetSuite query ID
            
        Returns:
            Tuple of (success, dataframe, error_message)
        """
        query = NetSuiteQuery.query.get(query_id)
        if not query or not query.is_active:
            return False, None, "Query not found or inactive"
        
        start_time = time.time()
        
        try:
            connection = self.get_connection(query.connection_id)
            if not connection:
                return False, None, "Failed to establish NetSuite connection"
            
            # Execute query based on type
            if query.query_type == "suiteql":
                result = self._execute_suiteql(connection, query.query_config)
            elif query.query_type == "search":
                result = self._execute_search(connection, query.query_config)
            elif query.query_type == "saved_search":
                result = self._execute_saved_search(connection, query.query_config)
            else:
                return False, None, f"Unsupported query type: {query.query_type}"
            
            # Convert to DataFrame
            df = pd.DataFrame(result)
            
            # Update query metadata
            execution_time = int((time.time() - start_time) * 1000)
            query.last_execution = datetime.utcnow()
            query.execution_status = "success"
            query.result_count = len(df)
            query.execution_time = execution_time
            query.execution_error = None
            
            db.session.commit()
            
            return True, df, None
            
        except Exception as e:
            logger.error(f"NetSuite query execution failed: {e}")
            
            # Update query with error
            query.last_execution = datetime.utcnow()
            query.execution_status = "failed"
            query.execution_error = str(e)
            db.session.commit()
            
            return False, None, str(e)
    
    def _execute_suiteql(self, connection: NSConnection, config: Dict[str, Any]) -> List[Dict]:
        """Execute SuiteQL query."""
        query_sql = config.get("sql")
        limit = config.get("limit", 1000)
        
        return connection.suiteql(query=query_sql, limit=limit)
    
    def _execute_search(self, connection: NSConnection, config: Dict[str, Any]) -> List[Dict]:
        """Execute NetSuite search."""
        record_type = config.get("record_type")
        fields = config.get("fields", [])
        filters = config.get("filters", {})
        
        return connection.search(
            record_type=record_type,
            fields=fields,
            filters=filters
        )
    
    def _execute_saved_search(self, connection: NSConnection, config: Dict[str, Any]) -> List[Dict]:
        """Execute NetSuite saved search."""
        search_id = config.get("search_id")
        
        return connection.saved_search(search_id=search_id)
    
    def refresh_data_source(self, data_source_id: int) -> Tuple[bool, Optional[str]]:
        """
        Refresh NetSuite data source.
        
        Args:
            data_source_id: NetSuite data source ID
            
        Returns:
            Tuple of (success, error_message)
        """
        data_source = NetSuiteDataSource.query.get(data_source_id)
        if not data_source:
            return False, "Data source not found"
        
        # Create refresh log
        refresh_log = NetSuiteRefreshLog(
            connection_id=data_source.connection_id,
            refresh_type="manual",
            status="running"
        )
        db.session.add(refresh_log)
        db.session.commit()
        
        try:
            # Update data source status
            data_source.refresh_status = "running"
            db.session.commit()
            
            # Execute refresh logic here
            connection = self.get_connection(data_source.connection_id)
            if not connection:
                raise Exception("Failed to establish NetSuite connection")
            
            # Fetch data based on data source configuration
            result = connection.search(
                record_type=data_source.record_type,
                fields=data_source.fields,
                filters=data_source.filters
            )
            
            # Update data source
            data_source.last_refresh = datetime.utcnow()
            data_source.refresh_status = "success"
            data_source.refresh_error = None
            
            # Update refresh log
            refresh_log.end_time = datetime.utcnow()
            refresh_log.status = "success"
            refresh_log.records_processed = len(result)
            
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            logger.error(f"NetSuite data source refresh failed: {e}")
            
            # Update data source with error
            data_source.refresh_status = "failed"
            data_source.refresh_error = str(e)
            
            # Update refresh log
            refresh_log.end_time = datetime.utcnow()
            refresh_log.status = "failed"
            refresh_log.error_message = str(e)
            
            db.session.commit()
            
            return False, str(e)
    
    @cache_manager.memoize(timeout=300)
    def get_netsuite_schema(self, connection_id: int) -> Dict[str, List[str]]:
        """
        Get NetSuite schema information.
        
        Args:
            connection_id: NetSuite connection ID
            
        Returns:
            Dictionary mapping record types to available fields
        """
        try:
            connection = self.get_connection(connection_id)
            if not connection:
                return {}
            
            # Get available record types and their fields
            # This is a simplified version - in practice, you'd query NetSuite metadata
            schema = {
                "customer": ["id", "companyname", "email", "phone", "datecreated"],
                "transaction": ["id", "tranid", "type", "amount", "trandate"],
                "item": ["id", "itemid", "displayname", "description", "unitprice"],
                "employee": ["id", "entityid", "firstname", "lastname", "email"],
                "vendor": ["id", "companyname", "email", "phone", "datecreated"],
            }
            
            return schema
            
        except Exception as e:
            logger.error(f"Failed to get NetSuite schema: {e}")
            return {}
    
    def schedule_refresh(self, data_source_id: int, interval_minutes: int = 30) -> bool:
        """
        Schedule automatic refresh for data source.
        
        Args:
            data_source_id: NetSuite data source ID
            interval_minutes: Refresh interval in minutes
            
        Returns:
            Success status
        """
        try:
            data_source = NetSuiteDataSource.query.get(data_source_id)
            if not data_source:
                return False
            
            # Update data source with auto refresh settings
            data_source.auto_refresh = True
            data_source.refresh_interval = interval_minutes * 60  # Convert to seconds
            
            db.session.commit()
            
            # Schedule with Celery (implementation would depend on Celery setup)
            from songo_bi.tasks.netsuite import refresh_data_source_task
            refresh_data_source_task.apply_async(
                args=[data_source_id],
                countdown=interval_minutes * 60
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule refresh: {e}")
            return False
