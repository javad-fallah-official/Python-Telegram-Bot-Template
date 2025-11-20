"""
Handlers package initialization.
"""

from .commands import *
from .messages import *
from .errors import *
from .registry import register_handlers

__all__ = ["register_handlers"]