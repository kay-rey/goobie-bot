"""
ESPN Games API module for goobie-bot
Handles all ESPN API calls related to games and events
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from api.http_client import get_json
from api.cache import game_data_key, get_cached, set_cached

logger = logging.getLogger(__name__)

# Team configuration mapping
TEAM_CONFIG = {
    "galaxy": {
        "sport": "soccer",
        "league": "usa.1",
        "team_id": "187",
        "days_ahead": 14,
    },
    "dodgers": {
        "sport": "baseball",
        "league": "mlb",
        "team_id": "19",
        "days_ahead": 14,
    },
    "lakers": {
        "sport": "basketball",
        "league": "nba",
        "team_id": "13",
        "days_ahead": 30,
    },
    "rams": {"sport": "football", "league": "nfl", "team_id": "14", "days_ahead": 14},
    "kings": {"sport": "hockey", "league": "nhl", "team_id": "8", "days_ahead": 14},
}


async def _get_team_next_game(
    team_name: str, config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Generic function to get the next game for any team

    Args:
        team_name: Name of the team (for logging and cache keys)
        config: Team configuration containing sport, league, team_id, and days_ahead

    Returns:
        Game data dictionary or None if no upcoming games found
    """
    try:
        logger.info(f"Fetching {team_name} next game data...")

        # Get current date and future date based on team config
        today = datetime.now()
        future_date = today + timedelta(days=config["days_ahead"])

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        # Check cache first
        cache_key = game_data_key(team_name, config["sport"], start_date, end_date)
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            logger.info(f"Returning cached {team_name} game data")
            return cached_result

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint
        url = f"http://sports.core.api.espn.com/v2/sports/{config['sport']}/leagues/{config['league']}/teams/{config['team_id']}/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        data = await get_json(url, params=params)
        logger.debug(f"ESPN API data keys: {list(data.keys()) if data else 'None'}")
        logger.debug(
            f"ESPN API items count: {len(data.get('items', [])) if data else 0}"
        )

        if data and data.get("items") and len(data["items"]) > 0:
            # Find the closest upcoming game by following $ref URLs
            upcoming_games = []

            for item in data["items"]:
                event_ref = item.get("$ref")
                if event_ref:
                    logger.debug(
                        f"Fetching {team_name} event details from: {event_ref}"
                    )
                    event_data = await get_json(event_ref)
                    if event_data:
                        event_date_str = event_data.get("date", "")

                        if event_date_str:
                            try:
                                # Parse the event date (make both timezone-aware)
                                event_date = datetime.fromisoformat(
                                    event_date_str.replace("Z", "+00:00")
                                )
                                # Make today timezone-aware for comparison
                                today_aware = today.replace(tzinfo=event_date.tzinfo)
                                # Check if the event is in the future
                                if event_date > today_aware:
                                    logger.debug(
                                        f"Found upcoming {team_name} game on {event_date}"
                                    )
                                    upcoming_games.append((event_date, event_data))
                            except Exception as e:
                                logger.warning(
                                    f"Error parsing {team_name} event date: {e}"
                                )
                                continue

            if upcoming_games:
                # Sort by date and get the closest upcoming game
                upcoming_games.sort(key=lambda x: x[0])
                closest_date, closest_game = upcoming_games[0]
                logger.info(
                    f"Found next {team_name} game: {closest_game.get('name', 'Unknown')} on {closest_game.get('date', 'TBD')}"
                )

                # Cache the result
                await set_cached(cache_key, closest_game, "game_data")
                return closest_game

        logger.warning(f"No upcoming {team_name} games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching {team_name} game data: {e}")
        return None


async def get_galaxy_next_game():
    """Get LA Galaxy's next game from ESPN API"""
    return await _get_team_next_game("galaxy", TEAM_CONFIG["galaxy"])


async def get_galaxy_next_game_extended():
    """Get LA Galaxy's next game with detailed information from ESPN API"""
    return await _get_team_next_game("galaxy", TEAM_CONFIG["galaxy"])


async def get_dodgers_next_game():
    """Get Los Angeles Dodgers' next game from ESPN API"""
    return await _get_team_next_game("dodgers", TEAM_CONFIG["dodgers"])


async def get_lakers_next_game():
    """Get Los Angeles Lakers' next game from ESPN API"""
    return await _get_team_next_game("lakers", TEAM_CONFIG["lakers"])


async def get_team_games_in_date_range(team_id, sport, league, start_date, end_date):
    """Get all games for a team within a specific date range"""
    try:
        logger.info(
            f"Fetching {sport} games for team {team_id} from {start_date} to {end_date}"
        )

        # Format dates for ESPN API
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        # ESPN API endpoint
        url = f"http://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/teams/{team_id}/events"
        params = {"dates": f"{start_str}-{end_str}", "limit": 50}

        data = await get_json(url, params=params)
        logger.debug(f"ESPN API response status: {200 if data else 'Failed'}")

        if data:
            games = []

            if data.get("items"):
                for item in data["items"]:
                    event_ref = item.get("$ref")
                    if event_ref:
                        event_data = await get_json(event_ref)
                        if event_data:
                            games.append(event_data)

            logger.info(f"Found {len(games)} games for team {team_id}")
            return games

        return []

    except Exception as e:
        logger.error(f"Error fetching games for team {team_id}: {e}")
        return []


async def get_rams_next_game():
    """Get Los Angeles Rams' next game from ESPN API"""
    return await _get_team_next_game("rams", TEAM_CONFIG["rams"])


async def get_kings_next_game():
    """Get Los Angeles Kings' next game from ESPN API"""
    return await _get_team_next_game("kings", TEAM_CONFIG["kings"])
