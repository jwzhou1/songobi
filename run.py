#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Main entry point for Songo BI application.
"""

import os
import sys
from songo_bi.app import create_app

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask application
app = create_app()

if __name__ == "__main__":
    # Run development server
    app.run(
        host=app.config.get("SONGO_WEBSERVER_ADDRESS", "0.0.0.0"),
        port=app.config.get("SONGO_WEBSERVER_PORT", 8088),
        debug=app.config.get("DEBUG", False)
    )
