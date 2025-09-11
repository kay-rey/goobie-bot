"""
ESPN Games API module for goobie-bot
Handles all ESPN API calls related to games and events
"""

import logging
from datetime import datetime, timedelta
from api.http_client import get_json

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

        data = await get_json(url, params=params)
        logger.info(f"ESPN API data keys: {list(data.keys()) if data else 'None'}")

        if data and data.get("items"):
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

        data = await get_json(url, params=params)
        logger.info(f"ESPN API data keys: {list(data.keys()) if data else 'None'}")
        logger.info(
            f"ESPN API items count: {len(data.get('items', [])) if data else 0}"
        )

        if data and data.get("items") and len(data["items"]) > 0:
            # Find the closest upcoming game by following $ref URLs
            upcoming_games = []

            for item in data["items"]:
                event_ref = item.get("$ref")
                if event_ref:
                    logger.info(f"Fetching event details from: {event_ref}")
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


async def get_dodgers_next_game():
    """Get Los Angeles Dodgers' next game from ESPN API"""
    try:
        logger.info("Fetching Dodgers next game data...")

        # Get current date and 2 weeks from now
        today = datetime.now()
        future_date = today + timedelta(days=14)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for Dodgers events (MLB team ID: 19)
        url = "http://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/teams/19/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        data = await get_json(url, params=params)
        logger.info(f"ESPN MLB API data keys: {list(data.keys()) if data else 'None'}")
        logger.info(
            f"ESPN MLB API items count: {len(data.get('items', [])) if data else 0}"
        )

        if data and data.get("items") and len(data["items"]) > 0:
            # Find the closest upcoming game by following $ref URLs
            upcoming_games = []

            for item in data["items"]:
                event_ref = item.get("$ref")
                if event_ref:
                    logger.info(f"Fetching Dodgers event details from: {event_ref}")
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
                                    logger.info(
                                        f"Found upcoming Dodgers game on {event_date.strftime('%Y-%m-%d %H:%M')}"
                                    )
                                    upcoming_games.append((event_date, event_data))
                            except Exception as e:
                                logger.warning(f"Error parsing Dodgers event date: {e}")
                                continue

            if upcoming_games:
                # Sort by date and get the closest upcoming game
                upcoming_games.sort(key=lambda x: x[0])
                closest_date, closest_game = upcoming_games[0]
                logger.info(f"Found next Dodgers game: {closest_game}")

                # Return game data (logos will be fetched separately)
                return closest_game

        logger.warning("No upcoming Dodgers games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching Dodgers game data: {e}")
        return None


async def get_lakers_next_game():
    """Get Los Angeles Lakers' next game from ESPN API"""
    try:
        logger.info("Fetching Lakers next game data...")

        # Get current date and 2 months from now to catch October games
        today = datetime.now()
        future_date = today + timedelta(days=60)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for Lakers events (NBA team ID: 13)
        url = "http://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/teams/13/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        data = await get_json(url, params=params)
        logger.info(f"ESPN NBA API data keys: {list(data.keys()) if data else 'None'}")
        logger.info(
            f"ESPN NBA API items count: {len(data.get('items', [])) if data else 0}"
        )

        if data and data.get("items") and len(data["items"]) > 0:
            # Find the closest upcoming game by following $ref URLs
            upcoming_games = []

            for item in data["items"]:
                event_ref = item.get("$ref")
                if event_ref:
                    logger.info(f"Fetching Lakers event details from: {event_ref}")
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

                                if event_date > today_aware:
                                    logger.info(
                                        f"Found upcoming Lakers game on {event_date}"
                                    )
                                    upcoming_games.append(event_data)
                            except ValueError as e:
                                logger.warning(
                                    f"Could not parse date {event_date_str}: {e}"
                                )
                                continue

            if upcoming_games:
                # Sort by date and return the earliest
                upcoming_games.sort(key=lambda x: x.get("date", ""))
                next_game = upcoming_games[0]
                logger.info(f"Found next Lakers game: {next_game}")
                return next_game

        logger.warning("No upcoming Lakers games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching Lakers game data: {e}")
        return None


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
        logger.info(f"ESPN API response status: {200 if data else 'Failed'}")

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
    try:
        logger.info("Fetching Rams next game data...")

        # Get current date and 2 weeks from now
        today = datetime.now()
        future_date = today + timedelta(days=14)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for Rams events (NFL team ID: 14)
        url = "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/14/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        data = await get_json(url, params=params)
        logger.info(f"ESPN NFL API data keys: {list(data.keys()) if data else 'None'}")
        logger.info(
            f"ESPN NFL API items count: {len(data.get('items', [])) if data else 0}"
        )

        if data and data.get("items") and len(data["items"]) > 0:
            # Find the closest upcoming game by following $ref URLs
            upcoming_games = []

            for item in data["items"]:
                event_ref = item.get("$ref")
                if event_ref:
                    logger.info(f"Fetching Rams event details from: {event_ref}")
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
                                    upcoming_games.append(event_data)
                                    logger.info(
                                        f"Found upcoming Rams game: {event_date}"
                                    )
                            except Exception as e:
                                logger.warning(f"Error parsing Rams game date: {e}")
                                continue

            # Sort by date and return the closest upcoming game
            if upcoming_games:
                upcoming_games.sort(key=lambda x: x.get("date", ""))
                logger.info(f"Found {len(upcoming_games)} upcoming Rams games")
                return upcoming_games[0]

        logger.warning("No upcoming Rams games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching Rams game data: {e}")
        return None


async def get_kings_next_game():
    """Get Los Angeles Kings' next game from ESPN API"""
    try:
        logger.info("Fetching Kings next game data...")

        # Get current date and 2 weeks from now
        today = datetime.now()
        future_date = today + timedelta(days=14)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for Kings events (NHL team ID: 8)
        url = "http://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl/teams/8/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        data = await get_json(url, params=params)
        logger.info(f"ESPN NHL API data keys: {list(data.keys()) if data else 'None'}")
        logger.info(
            f"ESPN NHL API items count: {len(data.get('items', [])) if data else 0}"
        )

        if data and data.get("items") and len(data["items"]) > 0:
            # Find the closest upcoming game by following $ref URLs
            upcoming_games = []

            for item in data["items"]:
                event_ref = item.get("$ref")
                if event_ref:
                    logger.info(f"Fetching Kings event details from: {event_ref}")
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
                                    upcoming_games.append(event_data)
                                    logger.info(
                                        f"Found upcoming Kings game: {event_date}"
                                    )
                            except Exception as e:
                                logger.warning(f"Error parsing Kings game date: {e}")
                                continue

            # Sort by date and return the closest upcoming game
            if upcoming_games:
                upcoming_games.sort(key=lambda x: x.get("date", ""))
                logger.info(f"Found {len(upcoming_games)} upcoming Kings games")
                return upcoming_games[0]

        logger.warning("No upcoming Kings games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching Kings game data: {e}")
        return None
