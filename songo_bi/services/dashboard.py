# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Dashboard service for Songo BI.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from songo_bi.extensions import db, cache_manager
from songo_bi.models.dashboard import Dashboard, Slice, Chart, Filter
from songo_bi.models.core import Table, Query
from songo_bi.services.data import DataService

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard management and operations."""
    
    def __init__(self):
        self.data_service = DataService()
    
    def create_dashboard(self, user_id: int, title: str, description: str = "") -> Dashboard:
        """
        Create a new dashboard.
        
        Args:
            user_id: Owner user ID
            title: Dashboard title
            description: Dashboard description
            
        Returns:
            New dashboard instance
        """
        dashboard = Dashboard(
            dashboard_title=title,
            description=description,
            owner_id=user_id,
            position_json=json.dumps({"DASHBOARD_VERSION_KEY": "v2"}),
            json_metadata=json.dumps({
                "refresh_frequency": 0,
                "timed_refresh_immune_slices": [],
                "expanded_slices": {},
                "color_scheme": "songo_default"
            })
        )
        
        db.session.add(dashboard)
        db.session.commit()
        
        return dashboard
    
    def create_chart(self, dashboard_id: int, chart_config: Dict[str, Any]) -> Tuple[bool, Optional[Slice], Optional[str]]:
        """
        Create a new chart/slice.
        
        Args:
            dashboard_id: Dashboard ID to add chart to
            chart_config: Chart configuration
            
        Returns:
            Tuple of (success, slice, error_message)
        """
        try:
            dashboard = Dashboard.query.get(dashboard_id)
            if not dashboard:
                return False, None, "Dashboard not found"
            
            # Create slice
            slice_obj = Slice(
                slice_name=chart_config.get("name", "New Chart"),
                viz_type=chart_config.get("viz_type", "table"),
                datasource_id=chart_config.get("datasource_id"),
                datasource_type="table",
                params=json.dumps(chart_config.get("params", {})),
                description=chart_config.get("description", ""),
                query_context=json.dumps(chart_config.get("query_context", {})),
                form_data=json.dumps(chart_config.get("form_data", {}))
            )
            
            db.session.add(slice_obj)
            db.session.flush()  # Get the ID
            
            # Add to dashboard
            dashboard.slices.append(slice_obj)
            
            # Create enhanced chart record
            chart = Chart(
                slice_id=slice_obj.id,
                chart_type=chart_config.get("viz_type", "table"),
                title=chart_config.get("name", "New Chart"),
                viz_config=chart_config.get("viz_config", {}),
                data_config=chart_config.get("data_config", {}),
                color_scheme=chart_config.get("color_scheme", "default")
            )
            
            db.session.add(chart)
            db.session.commit()
            
            return True, slice_obj, None
            
        except Exception as e:
            logger.error(f"Chart creation failed: {e}")
            db.session.rollback()
            return False, None, str(e)
    
    def get_dashboard_data(self, dashboard_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get dashboard data with all charts.
        
        Args:
            dashboard_id: Dashboard ID
            filters: Applied filters
            
        Returns:
            Dashboard data dictionary
        """
        dashboard = Dashboard.query.get(dashboard_id)
        if not dashboard:
            return {}
        
        dashboard_data = {
            "id": dashboard.id,
            "title": dashboard.dashboard_title,
            "description": dashboard.description,
            "position_json": json.loads(dashboard.position_json or "{}"),
            "metadata": json.loads(dashboard.json_metadata or "{}"),
            "charts": []
        }
        
        # Get data for each chart
        for slice_obj in dashboard.slices:
            chart_data = self._get_chart_data(slice_obj.id, filters)
            dashboard_data["charts"].append(chart_data)
        
        return dashboard_data
    
    def _get_chart_data(self, slice_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get data for a specific chart."""
        
        slice_obj = Slice.query.get(slice_id)
        if not slice_obj:
            return {}
        
        try:
            # Parse form data
            form_data = json.loads(slice_obj.form_data or "{}")
            
            # Apply filters
            if filters:
                form_data.update(filters)
            
            # Get data from data service
            data = self.data_service.get_chart_data(slice_obj.datasource_id, form_data)
            
            return {
                "slice_id": slice_id,
                "slice_name": slice_obj.slice_name,
                "viz_type": slice_obj.viz_type,
                "form_data": form_data,
                "data": data,
                "cache_timeout": slice_obj.cache_timeout
            }
            
        except Exception as e:
            logger.error(f"Failed to get chart data for slice {slice_id}: {e}")
            return {
                "slice_id": slice_id,
                "error": str(e)
            }
    
    def generate_ai_dashboard(self, user_id: int, prompt: str, data_sources: List[int]) -> Tuple[bool, Optional[Dashboard], Optional[str]]:
        """
        Generate dashboard using AI based on user prompt.
        
        Args:
            user_id: User ID
            prompt: User prompt describing desired dashboard
            data_sources: List of data source IDs to use
            
        Returns:
            Tuple of (success, dashboard, error_message)
        """
        try:
            # Analyze data sources
            schema_info = self._analyze_data_sources(data_sources)
            
            # Generate dashboard configuration using AI
            dashboard_config = self._generate_dashboard_config(prompt, schema_info)
            
            # Create dashboard
            dashboard = self.create_dashboard(
                user_id=user_id,
                title=dashboard_config.get("title", "AI Generated Dashboard"),
                description=f"Generated from prompt: {prompt}"
            )
            
            # Mark as AI generated
            dashboard.ai_generated = True
            dashboard.ai_prompt = prompt
            dashboard.ai_confidence = dashboard_config.get("confidence", 0.7)
            
            # Create charts
            for chart_config in dashboard_config.get("charts", []):
                self.create_chart(dashboard.id, chart_config)
            
            db.session.commit()
            
            return True, dashboard, None
            
        except Exception as e:
            logger.error(f"AI dashboard generation failed: {e}")
            return False, None, str(e)
    
    def _analyze_data_sources(self, data_source_ids: List[int]) -> Dict[str, Any]:
        """Analyze available data sources for AI dashboard generation."""
        
        schema_info = {
            "tables": [],
            "columns": [],
            "relationships": []
        }
        
        for ds_id in data_source_ids:
            table = Table.query.get(ds_id)
            if table:
                table_info = {
                    "id": table.id,
                    "name": table.table_name,
                    "schema": table.schema,
                    "columns": [
                        {
                            "name": col.column_name,
                            "type": col.type,
                            "is_dttm": col.is_dttm,
                            "groupby": col.groupby,
                            "filterable": col.filterable
                        }
                        for col in table.columns
                    ]
                }
                schema_info["tables"].append(table_info)
        
        return schema_info
    
    def _generate_dashboard_config(self, prompt: str, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dashboard configuration using AI."""
        
        # Simplified AI generation - in production, use more sophisticated prompting
        system_prompt = f"""
        You are a BI dashboard expert. Based on the user prompt and available data schema,
        generate a dashboard configuration with appropriate charts.
        
        Available data schema: {json.dumps(schema_info, indent=2)}
        
        User prompt: {prompt}
        
        Generate a JSON configuration with:
        - title: Dashboard title
        - description: Dashboard description
        - charts: List of chart configurations
        - confidence: Your confidence in this configuration (0-1)
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse AI response (simplified)
            config = {
                "title": "AI Generated Dashboard",
                "description": f"Generated from: {prompt}",
                "charts": [
                    {
                        "name": "Sample Chart",
                        "viz_type": "table",
                        "datasource_id": schema_info["tables"][0]["id"] if schema_info["tables"] else None,
                        "params": {},
                        "viz_config": {},
                        "data_config": {}
                    }
                ],
                "confidence": 0.7
            }
            
            return config
            
        except Exception as e:
            logger.error(f"AI dashboard config generation failed: {e}")
            return {
                "title": "Dashboard",
                "description": prompt,
                "charts": [],
                "confidence": 0.1
            }
    
    @cache_manager.memoize(timeout=300)
    def get_dashboard_list(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of dashboards for user or all public dashboards."""
        
        query = Dashboard.query
        
        if user_id:
            query = query.filter(
                (Dashboard.owner_id == user_id) | (Dashboard.published == True)
            )
        else:
            query = query.filter_by(published=True)
        
        dashboards = query.all()
        
        return [
            {
                "id": d.id,
                "title": d.dashboard_title,
                "description": d.description,
                "owner_id": d.owner_id,
                "published": d.published,
                "is_featured": d.is_featured,
                "ai_generated": d.ai_generated,
                "created_on": d.created_on.isoformat() if d.created_on else None,
                "changed_on": d.changed_on.isoformat() if d.changed_on else None
            }
            for d in dashboards
        ]
