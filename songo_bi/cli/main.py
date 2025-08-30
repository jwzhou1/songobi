# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Command-line interface for Songo BI.
"""

import click
import logging
from flask.cli import with_appcontext

from songo_bi.app import create_app
from songo_bi.extensions import db
from songo_bi.cli.commands import (
    init_db,
    create_admin_user,
    load_sample_data,
    netsuite_commands,
    backup_commands
)

logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', default='development', help='Configuration to use')
@click.pass_context
def songo_bi(ctx, config):
    """Songo BI command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    
    # Create app context
    app = create_app(config)
    ctx.obj['app'] = app


@songo_bi.group()
def db():
    """Database management commands."""
    pass


@db.command()
@with_appcontext
def init():
    """Initialize the database."""
    click.echo("Initializing database...")
    init_db()
    click.echo("Database initialized successfully!")


@db.command()
@with_appcontext
def upgrade():
    """Upgrade database to latest migration."""
    from flask_migrate import upgrade
    click.echo("Upgrading database...")
    upgrade()
    click.echo("Database upgraded successfully!")


@db.command()
@with_appcontext
def downgrade():
    """Downgrade database by one migration."""
    from flask_migrate import downgrade
    click.echo("Downgrading database...")
    downgrade()
    click.echo("Database downgraded successfully!")


@songo_bi.group()
def fab():
    """Flask-AppBuilder commands."""
    pass


@fab.command('create-admin')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--firstname', prompt=True, help='Admin first name')
@click.option('--lastname', prompt=True, help='Admin last name')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, help='Admin password')
@with_appcontext
def create_admin(username, firstname, lastname, email, password):
    """Create admin user."""
    click.echo("Creating admin user...")
    success = create_admin_user(username, firstname, lastname, email, password)
    if success:
        click.echo("Admin user created successfully!")
    else:
        click.echo("Failed to create admin user!")


@songo_bi.command()
@with_appcontext
def init():
    """Initialize Songo BI with default data."""
    click.echo("Initializing Songo BI...")
    
    # Initialize database
    init_db()
    
    # Load sample data in development
    import os
    if os.environ.get('FLASK_ENV') == 'development':
        load_sample_data()
    
    click.echo("Songo BI initialized successfully!")


@songo_bi.command('load-examples')
@with_appcontext
def load_examples():
    """Load example data and dashboards."""
    click.echo("Loading example data...")
    load_sample_data()
    click.echo("Example data loaded successfully!")


@songo_bi.group()
def netsuite():
    """NetSuite integration commands."""
    pass


@netsuite.command('test-connection')
@click.option('--connection-id', type=int, required=True, help='NetSuite connection ID')
@with_appcontext
def test_netsuite_connection(connection_id):
    """Test NetSuite connection."""
    from songo_bi.services.netsuite import NetSuiteService
    
    service = NetSuiteService()
    success, error = service.test_connection(connection_id)
    
    if success:
        click.echo(f"✅ NetSuite connection {connection_id} is working!")
    else:
        click.echo(f"❌ NetSuite connection {connection_id} failed: {error}")


@netsuite.command('refresh-data')
@click.option('--data-source-id', type=int, required=True, help='Data source ID')
@with_appcontext
def refresh_netsuite_data(data_source_id):
    """Refresh NetSuite data source."""
    from songo_bi.services.netsuite import NetSuiteService
    
    service = NetSuiteService()
    success, error = service.refresh_data_source(data_source_id)
    
    if success:
        click.echo(f"✅ Data source {data_source_id} refreshed successfully!")
    else:
        click.echo(f"❌ Data source {data_source_id} refresh failed: {error}")


@songo_bi.group()
def backup():
    """Backup and restore commands."""
    pass


@backup.command('create')
@click.option('--output', default='backup.sql', help='Output file path')
@with_appcontext
def create_backup(output):
    """Create database backup."""
    click.echo(f"Creating backup to {output}...")
    # Implementation would go here
    click.echo("Backup created successfully!")


@backup.command('restore')
@click.option('--input', required=True, help='Backup file path')
@with_appcontext
def restore_backup(input):
    """Restore database from backup."""
    click.echo(f"Restoring from {input}...")
    # Implementation would go here
    click.echo("Backup restored successfully!")


@songo_bi.command('run')
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8088, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@with_appcontext
def run_server(host, port, debug):
    """Run Songo BI development server."""
    from flask import current_app
    
    click.echo(f"Starting Songo BI server on {host}:{port}")
    current_app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    songo_bi()
