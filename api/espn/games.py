"""
ESPN Games API module for goobie-bot
Handles all ESPN API calls related to games and events
"""

import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def get_galaxy_next_game():
    """Get LA Galaxy's next game from ESPN API"""
    try:
        logger.info("Fetching next game data...")

        # Get current date and 2 weeks from now
        today = datetime.now()
        future_date = today + timedelta(days=14)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for LA Galaxy events
        url = "http://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"ESPN API response status: {response.status_code}")
        logger.info(f"Date range: {start_date} to {end_date}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"ESPN API data keys: {list(data.keys())}")

            if data.get("items"):
                # Get the first upcoming game
                return data["items"][0]

        logger.warning("No upcoming games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching game data: {e}")
        return None


async def get_galaxy_next_game_extended():
    """Get LA Galaxy's next game with detailed information from ESPN API"""
    try:
        logger.info("Fetching next game data...")

        # Get current date and 2 weeks from now
        today = datetime.now()
        future_date = today + timedelta(days=14)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for LA Galaxy events
        url = "http://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"ESPN API response status: {response.status_code}")
        logger.info(f"Date range: {start_date} to {end_date}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"ESPN API data keys: {list(data.keys())}")
            logger.info(f"ESPN API items count: {len(data.get('items', []))}")

            if data.get("items") and len(data["items"]) > 0:
                # Find the closest upcoming game by following $ref URLs
                upcoming_games = []

                for item in data["items"]:
                    event_ref = item.get("$ref")
                    if event_ref:
                        logger.info(f"Fetching event details from: {event_ref}")
                        event_response = requests.get(event_ref, timeout=10)
                        if event_response.status_code == 200:
                            event_data = event_response.json()
                            event_date_str = event_data.get("date", "")

                            if event_date_str:
                                try:
                                    # Parse the event date (make both timezone-aware)
                                    event_date = datetime.fromisoformat(
                                        event_date_str.replace("Z", "+00:00")
                                    )
                                    # Make today timezone-aware for comparison
                                    today_aware = today.replace(
                                        tzinfo=event_date.tzinfo
                                    )
                                    # Check if the event is in the future
                                    if event_date > today_aware:
                                        logger.info(
                                            f"Found upcoming game on {event_date.strftime('%Y-%m-%d %H:%M')}"
                                        )
                                        upcoming_games.append((event_date, event_data))
                                except Exception as e:
                                    logger.warning(f"Error parsing event date: {e}")
                                    continue

                if upcoming_games:
                    # Sort by date and get the closest upcoming game
                    upcoming_games.sort(key=lambda x: x[0])
                    closest_date, closest_game = upcoming_games[0]
                    logger.info(f"Found next game: {closest_game}")

                    # Return game data (logos will be fetched separately)
                    return closest_game

        logger.warning("No upcoming games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching game data: {e}")
        return None
