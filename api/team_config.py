"""
Team configuration module for goobie-bot
Centralized team data to eliminate redundant API calls
"""

from typing import Dict, Any, Callable
from api.espn.games import (
    get_galaxy_next_game_extended,
    get_dodgers_next_game,
    get_lakers_next_game,
    get_rams_next_game,
    get_kings_next_game,
)

# Pre-computed team data (eliminates API calls)
# Note: Logo URLs now point to GitHub repository for consistency with local logo system
TEAM_DATA = {
    "galaxy": {
        "idTeam": "134153",
        "strTeam": "LA Galaxy",
        "strLeague": "American Major League Soccer",
        "strSport": "Soccer",
        "strBadge": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/galaxy/logo.png",
        "strLogo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/galaxy/logo.png",
        "strStadium": "Dignity Health Sports Park",
    },
    "dodgers": {
        "idTeam": "1416",
        "strTeam": "Los Angeles Dodgers",
        "strLeague": "Major League Baseball",
        "strSport": "Baseball",
        "strBadge": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/dodgers/logo.png",
        "strLogo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/dodgers/logo.png",
        "strStadium": "Dodger Stadium",
    },
    "lakers": {
        "idTeam": "134154",
        "strTeam": "Los Angeles Lakers",
        "strLeague": "National Basketball Association",
        "strSport": "Basketball",
        "strBadge": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/lakers/logo.png",
        "strLogo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/lakers/logo.png",
        "strStadium": "Crypto.com Arena",
    },
    "rams": {
        "idTeam": "135907",
        "strTeam": "Los Angeles Rams",
        "strLeague": "National Football League",
        "strSport": "American Football",
        "strBadge": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/rams/logo.png",
        "strLogo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/rams/logo.png",
        "strStadium": "SoFi Stadium",
    },
    "kings": {
        "idTeam": "134852",
        "strTeam": "Los Angeles Kings",
        "strLeague": "National Hockey League",
        "strSport": "Ice Hockey",
        "strBadge": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/kings/logo.png",
        "strLogo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/kings/logo.png",
        "strStadium": "Crypto.com Arena",
    },
}

# Pre-computed team configuration for nextgame command
TEAM_CONFIG = {
    "galaxy": {
        "name": "LA Galaxy",
        "game_func": get_galaxy_next_game_extended,
        "default_logo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/galaxy/logo.png",
    },
    "dodgers": {
        "name": "Los Angeles Dodgers",
        "game_func": get_dodgers_next_game,
        "default_logo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/dodgers/logo.png",
    },
    "lakers": {
        "name": "Los Angeles Lakers",
        "game_func": get_lakers_next_game,
        "default_logo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/lakers/logo.png",
    },
    "rams": {
        "name": "Los Angeles Rams",
        "game_func": get_rams_next_game,
        "default_logo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/rams/logo.png",
    },
    "kings": {
        "name": "Los Angeles Kings",
        "game_func": get_kings_next_game,
        "default_logo": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/logos/kings/logo.png",
    },
}

# Note: Default logos are now handled by the local logo system's built-in fallbacks


def get_team_data(team_key: str) -> Dict[str, Any]:
    """Get team data by key (no API call required)"""
    return TEAM_DATA.get(team_key, {})


def get_team_config(team_key: str) -> Dict[str, Any]:
    """Get team configuration by key"""
    return TEAM_CONFIG.get(team_key, {})


# get_default_logos function removed - now handled by local logo system


def get_team_display_name(team_key: str) -> str:
    """Get team display name by key"""
    config = get_team_config(team_key)
    return config.get("name", "Unknown Team")


def get_game_function(team_key: str) -> Callable:
    """Get game data function by team key"""
    config = get_team_config(team_key)
    return config.get("game_func")


def get_team_default_logo(team_key: str) -> str:
    """Get default logo URL by team key"""
    config = get_team_config(team_key)
    return config.get("default_logo", "")
