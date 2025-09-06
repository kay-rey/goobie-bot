"""
API module for goobie-bot
Combines ESPN and TheSportsDB API functions
"""

from .espn import (
    get_galaxy_next_game,
    get_galaxy_next_game_extended,
    get_team_name_from_ref,
)
from .sportsdb import (
    get_galaxy_team_data,
    get_team_logos,
    extract_logos_from_team,
    search_team_logos,
    search_venue_logos,
    test_logo_url,
)
from .processors import get_game_logos, create_game_embed

__all__ = [
    # ESPN API functions
    "get_galaxy_next_game",
    "get_galaxy_next_game_extended",
    "get_team_name_from_ref",
    # TheSportsDB API functions
    "get_galaxy_team_data",
    "get_team_logos",
    "extract_logos_from_team",
    "search_team_logos",
    "search_venue_logos",
    "test_logo_url",
    # Game processing functions
    "get_game_logos",
    "create_game_embed",
]
