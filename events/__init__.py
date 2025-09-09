"""
Events module for goobie-bot
Contains all Discord event handlers
"""

from .ready import on_ready
from .message import on_message
from .errors import on_command_error, on_app_command_error

__all__ = [
    "on_ready",
    "on_message",
    "on_command_error",
    "on_app_command_error",
]
