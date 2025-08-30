# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
CLI command implementations for Songo BI.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import current_app
from flask_appbuilder.security.sqla.models import User, Role

from songo_bi.extensions import db
from songo_bi.models.core import Database, Table, Column
from songo_bi.models.dashboard import Dashboard, Slice
from songo_bi.models.netsuite import NetSuiteConnection, NetSuiteDataSource

logger = logging.getLogger(__name__)


# Additional command implementations
def netsuite_commands():
    """NetSuite-related command implementations."""
    pass


def backup_commands():
    """Backup and restore command implementations."""
    pass


def init_db():
    """Initialize database with tables and default data."""
    
    # Create all tables
    db.create_all()
    
    # Create default roles if they don't exist
    from flask_appbuilder.security.sqla.models import Role
    
    roles_data = [
        {"name": "Admin", "description": "Administrator role with full access"},
        {"name": "Alpha", "description": "Alpha user with advanced access"},
        {"name": "Gamma", "description": "Standard user with read access"},
        {"name": "Public", "description": "Public access role"},
    ]
    
    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data["name"]).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
    
    db.session.commit()
    logger.info("Database initialized successfully")


def create_admin_user(username: str, firstname: str, lastname: str, email: str, password: str) -> bool:
    """Create admin user."""
    
    try:
        from flask_appbuilder.security.sqla.models import User, Role
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logger.warning(f"User {username} already exists")
            return False
        
        # Get admin role
        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            logger.error("Admin role not found")
            return False
        
        # Create user
        user = User(
            username=username,
            first_name=firstname,
            last_name=lastname,
            email=email,
            active=True
        )
        user.roles.append(admin_role)
        
        # Set password (this would use proper hashing in production)
        user.password = password
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Admin user {username} created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        db.session.rollback()
        return False


def load_sample_data():
    """Load sample data for development and testing."""
    
    try:
        # Create sample database connection
        sample_db = Database.query.filter_by(database_name="Sample Database").first()
        if not sample_db:
            sample_db = Database(
                database_name="Sample Database",
                sqlalchemy_uri="sqlite:///sample.db",
                expose_in_sqllab=True,
                allow_csv_upload=True,
                allow_ctas=True,
                allow_cvas=True
            )
            db.session.add(sample_db)
            db.session.flush()
        
        # Create sample table
        sample_table = Table.query.filter_by(table_name="sales_data").first()
        if not sample_table:
            sample_table = Table(
                table_name="sales_data",
                database_id=sample_db.id,
                description="Sample sales data for demonstration",
                is_sqllab_view=False
            )
            db.session.add(sample_table)
            db.session.flush()
            
            # Create sample columns
            columns_data = [
                {"column_name": "date", "type": "DATE", "is_dttm": True, "groupby": True},
                {"column_name": "region", "type": "VARCHAR", "groupby": True, "filterable": True},
                {"column_name": "product", "type": "VARCHAR", "groupby": True, "filterable": True},
                {"column_name": "sales_amount", "type": "DECIMAL", "groupby": False, "filterable": True},
                {"column_name": "quantity", "type": "INTEGER", "groupby": False, "filterable": True},
            ]
            
            for col_data in columns_data:
                column = Column(
                    table_id=sample_table.id,
                    **col_data
                )
                db.session.add(column)
        
        # Create sample NetSuite connection (inactive by default)
        netsuite_conn = NetSuiteConnection.query.filter_by(name="Sample NetSuite").first()
        if not netsuite_conn:
            netsuite_conn = NetSuiteConnection(
                name="Sample NetSuite",
                account_id="sample_account",
                consumer_key="sample_key",
                consumer_secret="sample_secret",
                token_id="sample_token",
                token_secret="sample_token_secret",
                is_active=False,  # Inactive until real credentials are provided
                description="Sample NetSuite connection for demonstration"
            )
            db.session.add(netsuite_conn)
            db.session.flush()
            
            # Create sample data source
            sample_ds = NetSuiteDataSource(
                name="Customer Data",
                connection_id=netsuite_conn.id,
                record_type="customer",
                fields=["id", "companyname", "email", "phone", "datecreated"],
                filters={"subsidiary": "1"},
                auto_refresh=False
            )
            db.session.add(sample_ds)
        
        # Create sample dashboard
        sample_dashboard = Dashboard.query.filter_by(dashboard_title="Sample Dashboard").first()
        if not sample_dashboard:
            sample_dashboard = Dashboard(
                dashboard_title="Sample Dashboard",
                description="Sample dashboard showcasing Songo BI features",
                position_json='{"DASHBOARD_VERSION_KEY": "v2"}',
                json_metadata='{"refresh_frequency": 0}',
                published=True
            )
            db.session.add(sample_dashboard)
            db.session.flush()
            
            # Create sample chart
            sample_chart = Slice(
                slice_name="Sales by Region",
                datasource_id=sample_table.id,
                datasource_type="table",
                viz_type="bar",
                params='{"groupby": ["region"], "metrics": ["sales_amount"]}',
                description="Sample bar chart showing sales by region",
                form_data='{"viz_type": "bar", "groupby": ["region"], "metrics": ["sales_amount"]}'
            )
            db.session.add(sample_chart)
            db.session.flush()
            
            # Add chart to dashboard
            sample_dashboard.slices.append(sample_chart)
        
        db.session.commit()
        logger.info("Sample data loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")
        db.session.rollback()
        raise
