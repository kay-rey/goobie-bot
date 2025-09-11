"""
API module for goobie-bot
Combines ESPN and TheSportsDB API functions
"""

from .espn import (
    get_galaxy_next_game,
    get_galaxy_next_game_extended,
    get_dodgers_next_game,
    get_lakers_next_game,
    get_rams_next_game,
    get_kings_next_game,
    get_team_name_from_ref,
)
from .sportsdb import (
    get_galaxy_team_data,
    get_dodgers_team_data,
    get_lakers_team_data,
    get_rams_team_data,
    get_kings_team_data,
    get_team_logos,
    extract_logos_from_team,
    search_team_logos,
    search_venue_logos,
    test_logo_url,
)
from .processors import get_game_logos, create_game_embed
from .local_logos import (
    get_local_team_logos,
    get_local_opponent_logo,
    get_local_team_logos_by_name,
    get_team_key_from_choice,
)

__all__ = [
    # ESPN API functions
    "get_galaxy_next_game",
    "get_galaxy_next_game_extended",
    "get_dodgers_next_game",
    "get_lakers_next_game",
    "get_rams_next_game",
    "get_kings_next_game",
    "get_team_name_from_ref",
    # TheSportsDB API functions
    "get_galaxy_team_data",
    "get_dodgers_team_data",
    "get_lakers_team_data",
    "get_rams_team_data",
    "get_kings_team_data",
    "get_team_logos",
    "extract_logos_from_team",
    "search_team_logos",
    "search_venue_logos",
    "test_logo_url",
    # Game processing functions
    "get_game_logos",
    "create_game_embed",
    # Local logo functions
    "get_local_team_logos",
    "get_local_opponent_logo",
    "get_local_team_logos_by_name",
    "get_team_key_from_choice",
]
