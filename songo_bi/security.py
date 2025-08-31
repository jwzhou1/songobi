# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Security configuration for Songo BI.
"""

from flask_appbuilder.security.sqla.manager import SecurityManager
from flask_appbuilder.security.views import UserDBModelView


class SongoSecurityManager(SecurityManager):
    """Custom security manager for Songo BI."""

    def __init__(self, appbuilder):
        """Initialize the security manager."""
        super().__init__(appbuilder)
        # Don't create admin user here - do it after app is fully initialized


class SongoUserDBModelView(UserDBModelView):
    """Custom user view for Songo BI."""
    
    list_columns = ['username', 'email', 'first_name', 'last_name', 'active', 'created_on']
    show_columns = ['username', 'email', 'first_name', 'last_name', 'active', 'created_on', 'changed_on']
    add_columns = ['username', 'first_name', 'last_name', 'email', 'active', 'roles', 'password', 'conf_password']
    edit_columns = ['username', 'first_name', 'last_name', 'email', 'active', 'roles']
    
    # Additional customizations can be added here
