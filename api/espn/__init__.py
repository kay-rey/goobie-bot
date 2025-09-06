"""
ESPN API module for goobie-bot
Handles all ESPN API calls for games and team information
"""

from .games import get_galaxy_next_game, get_galaxy_next_game_extended
from .teams import get_team_name_from_ref

__all__ = [
    "get_galaxy_next_game",
    "get_galaxy_next_game_extended",
    "get_team_name_from_ref",
]
