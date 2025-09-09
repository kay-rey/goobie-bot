"""
Commands module for goobie-bot
Contains all Discord slash commands and text commands
"""

from .nextgame import nextgame_command
from .ping import ping_command
from .test import test_command
from .sync import sync_command

__all__ = [
    "nextgame_command",
    "ping_command",
    "test_command",
    "sync_command",
]
