# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Views package for Songo BI.
"""

from songo_bi.views.api import api_bp
from songo_bi.views.core import core_bp
from songo_bi.views.dashboard import dashboard_bp
from songo_bi.views.netsuite import netsuite_bp
from songo_bi.views.chatbot import chatbot_bp

__all__ = [
    "api_bp",
    "core_bp", 
    "dashboard_bp",
    "netsuite_bp",
    "chatbot_bp",
]
