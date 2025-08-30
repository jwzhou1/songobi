# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Data service for Songo BI.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from songo_bi.extensions import db, cache_manager
from songo_bi.models.core import Database, Table, Query

logger = logging.getLogger(__name__)


class DataService:
    """Service for data operations and query execution."""
    
    def __init__(self):
        self.engines = {}  # Cache for database engines
    
    def get_engine(self, database_id: int):
        """Get or create database engine."""
        
        if database_id in self.engines:
            return self.engines[database_id]
        
        database = Database.query.get(database_id)
        if not database:
            return None
        
        try:
            engine = create_engine(
                database.sqlalchemy_uri,
                **database.extra or {}
            )
            self.engines[database_id] = engine
            return engine
            
        except Exception as e:
            logger.error(f"Failed to create engine for database {database_id}: {e}")
            return None
    
    def execute_sql(self, database_id: int, sql: str, limit: Optional[int] = None) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Execute SQL query against database.
        
        Args:
            database_id: Database ID
            sql: SQL query
            limit: Optional result limit
            
        Returns:
            Tuple of (success, dataframe, error_message)
        """
        try:
            engine = self.get_engine(database_id)
            if not engine:
                return False, None, "Database connection not available"
            
            # Apply limit if specified
            if limit:
                sql = f"SELECT * FROM ({sql}) AS limited_query LIMIT {limit}"
            
            # Execute query
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            return True, df, None
            
        except SQLAlchemyError as e:
            logger.error(f"SQL execution failed: {e}")
            return False, None, str(e)
        except Exception as e:
            logger.error(f"Unexpected error in SQL execution: {e}")
            return False, None, str(e)
    
    def get_chart_data(self, datasource_id: int, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get data for chart visualization.
        
        Args:
            datasource_id: Data source (table) ID
            form_data: Chart form configuration
            
        Returns:
            Chart data dictionary
        """
        try:
            table = Table.query.get(datasource_id)
            if not table:
                return {"error": "Data source not found"}
            
            # Build query based on form data
            sql = self._build_chart_query(table, form_data)
            
            # Execute query
            success, df, error = self.execute_sql(table.database_id, sql)
            
            if not success:
                return {"error": error}
            
            # Format data for visualization
            chart_data = self._format_chart_data(df, form_data)
            
            return {
                "data": chart_data,
                "query": sql,
                "rowcount": len(df),
                "columns": list(df.columns) if df is not None else []
            }
            
        except Exception as e:
            logger.error(f"Chart data retrieval failed: {e}")
            return {"error": str(e)}
    
    def _build_chart_query(self, table: Table, form_data: Dict[str, Any]) -> str:
        """Build SQL query for chart data."""
        
        # Extract form data components
        groupby = form_data.get("groupby", [])
        metrics = form_data.get("metrics", [])
        where_clause = form_data.get("where", "")
        having_clause = form_data.get("having", "")
        order_by = form_data.get("order_by_cols", [])
        limit = form_data.get("row_limit", 1000)
        
        # Build SELECT clause
        select_parts = []
        
        # Add groupby columns
        for col in groupby:
            if isinstance(col, dict):
                select_parts.append(f"{col.get('column_name', col.get('sqlExpression', col))}")
            else:
                select_parts.append(str(col))
        
        # Add metrics
        for metric in metrics:
            if isinstance(metric, dict):
                expr = metric.get("sqlExpression")
                label = metric.get("label", expr)
                if expr:
                    select_parts.append(f"{expr} AS \"{label}\"")
            else:
                select_parts.append(str(metric))
        
        if not select_parts:
            select_parts = ["*"]
        
        # Build query
        sql_parts = [
            f"SELECT {', '.join(select_parts)}",
            f"FROM {table.schema}.{table.table_name}" if table.schema else f"FROM {table.table_name}"
        ]
        
        if where_clause:
            sql_parts.append(f"WHERE {where_clause}")
        
        if groupby:
            group_cols = [
                col.get('column_name', col) if isinstance(col, dict) else str(col)
                for col in groupby
            ]
            sql_parts.append(f"GROUP BY {', '.join(group_cols)}")
        
        if having_clause:
            sql_parts.append(f"HAVING {having_clause}")
        
        if order_by:
            order_parts = []
            for order_col in order_by:
                if isinstance(order_col, dict):
                    col_name = order_col.get("column_name", "")
                    direction = "DESC" if order_col.get("descending") else "ASC"
                    order_parts.append(f"{col_name} {direction}")
            if order_parts:
                sql_parts.append(f"ORDER BY {', '.join(order_parts)}")
        
        if limit:
            sql_parts.append(f"LIMIT {limit}")
        
        return " ".join(sql_parts)
    
    def _format_chart_data(self, df: pd.DataFrame, form_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format DataFrame for chart visualization."""
        
        if df is None or df.empty:
            return []
        
        viz_type = form_data.get("viz_type", "table")
        
        if viz_type == "table":
            return df.to_dict("records")
        elif viz_type in ["bar", "line", "area"]:
            return self._format_timeseries_data(df, form_data)
        elif viz_type == "pie":
            return self._format_pie_data(df, form_data)
        else:
            # Default to table format
            return df.to_dict("records")
    
    def _format_timeseries_data(self, df: pd.DataFrame, form_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format data for time series charts."""
        
        # Simplified formatting - in production, handle various time series formats
        return df.to_dict("records")
    
    def _format_pie_data(self, df: pd.DataFrame, form_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format data for pie charts."""
        
        # Simplified formatting - in production, handle pie chart specific formatting
        return df.to_dict("records")
    
    @cache_manager.memoize(timeout=3600)
    def get_table_metadata(self, table_id: int) -> Dict[str, Any]:
        """Get table metadata including columns and sample data."""
        
        table = Table.query.get(table_id)
        if not table:
            return {}
        
        try:
            # Get column information
            columns = [
                {
                    "name": col.column_name,
                    "type": col.type,
                    "is_dttm": col.is_dttm,
                    "groupby": col.groupby,
                    "filterable": col.filterable,
                    "description": col.description
                }
                for col in table.columns
            ]
            
            # Get sample data
            sample_sql = f"SELECT * FROM {table.table_name} LIMIT 10"
            success, sample_df, error = self.execute_sql(table.database_id, sample_sql)
            
            sample_data = sample_df.to_dict("records") if success and sample_df is not None else []
            
            return {
                "id": table.id,
                "name": table.table_name,
                "schema": table.schema,
                "description": table.description,
                "columns": columns,
                "sample_data": sample_data,
                "row_count": self._get_table_row_count(table)
            }
            
        except Exception as e:
            logger.error(f"Failed to get table metadata: {e}")
            return {"error": str(e)}
    
    def _get_table_row_count(self, table: Table) -> Optional[int]:
        """Get approximate row count for table."""
        
        try:
            count_sql = f"SELECT COUNT(*) as row_count FROM {table.table_name}"
            success, df, error = self.execute_sql(table.database_id, count_sql)
            
            if success and df is not None and not df.empty:
                return int(df.iloc[0]["row_count"])
            
        except Exception as e:
            logger.error(f"Failed to get row count: {e}")
        
        return None
