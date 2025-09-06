"""
ESPN Teams API module for goobie-bot
Handles all ESPN API calls related to team information
"""

import logging
import requests

logger = logging.getLogger(__name__)


async def get_team_name_from_ref(team_ref):
    """Get team name from ESPN team reference URL"""
    if not team_ref:
        return "TBD"

    try:
        response = requests.get(team_ref, timeout=10)
        if response.status_code == 200:
            team_data = response.json()
            # Try different name fields in order of preference
            return (
                team_data.get("displayName")
                or team_data.get("name")
                or team_data.get("shortDisplayName")
                or team_data.get("abbreviation")
                or "TBD"
            )
    except Exception as e:
        logger.error(f"Error fetching team name from {team_ref}: {e}")

    return "TBD"
