"""
ESPN Teams API module for goobie-bot
Handles all ESPN API calls related to team information
"""

import logging
from api.http_client import get_json

logger = logging.getLogger(__name__)

# Simple cache to avoid repeated API calls
_team_name_cache = {}


async def get_team_name_from_ref(team_ref):
    """Get team name from ESPN team reference URL with caching"""
    if not team_ref:
        return "TBD"

    # Check cache first
    if team_ref in _team_name_cache:
        return _team_name_cache[team_ref]

    try:
        team_data = await get_json(team_ref)
        if team_data:
            # Try different name fields in order of preference
            team_name = (
                team_data.get("displayName")
                or team_data.get("name")
                or team_data.get("shortDisplayName")
                or team_data.get("abbreviation")
                or "TBD"
            )
            # Cache the result
            _team_name_cache[team_ref] = team_name
            return team_name
        else:
            logger.warning(f"Failed to fetch team data from {team_ref}")
    except Exception as e:
        logger.error(f"Error fetching team name from {team_ref}: {e}")

    return "TBD"
