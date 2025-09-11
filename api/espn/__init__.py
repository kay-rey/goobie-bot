"""
ESPN API module for goobie-bot
Handles all ESPN API calls for games and team information
"""

from .games import (
    get_galaxy_next_game,
    get_galaxy_next_game_extended,
    get_dodgers_next_game,
    get_lakers_next_game,
    get_rams_next_game,
    get_kings_next_game,
)
from .teams import get_team_name_from_ref

__all__ = [
    "get_galaxy_next_game",
    "get_galaxy_next_game_extended",
    "get_dodgers_next_game",
    "get_lakers_next_game",
    "get_rams_next_game",
    "get_kings_next_game",
    "get_team_name_from_ref",
]
