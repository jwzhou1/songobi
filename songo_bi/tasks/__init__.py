# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Background tasks package for Songo BI.
"""

from songo_bi.tasks.celery_app import app as celery_app
from songo_bi.tasks.netsuite import *
from songo_bi.tasks.dashboard import *
from songo_bi.tasks.ai import *

__all__ = [
    "celery_app",
]
