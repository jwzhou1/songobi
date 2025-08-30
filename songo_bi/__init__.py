# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Songo BI - Modern Business Intelligence Platform

A comprehensive BI platform with AI integration and NetSuite connectivity.
"""

__version__ = "0.1.0"
__author__ = "Songo BI Team"
__email__ = "team@songo-bi.com"
__license__ = "Apache-2.0"

from songo_bi.app import create_app

__all__ = ["create_app"]
