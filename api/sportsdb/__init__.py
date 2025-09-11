"""
TheSportsDB API module for goobie-bot
Handles all TheSportsDB API calls for team data, logos, and venue information
"""

from .teams import (
    get_galaxy_team_data,
    get_dodgers_team_data,
    get_lakers_team_data,
    get_rams_team_data,
    get_kings_team_data,
    get_team_logos,
    extract_logos_from_team,
    search_team_logos,
    test_logo_url,
)
from .venues import search_venue_logos

__all__ = [
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
]
