"""
Weekly matches command for goobie-bot
Allows manual testing of the weekly matches notification with optimizations
"""

import discord
from discord import app_commands
import logging
import asyncio
import time
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any, Tuple

from scheduler.weekly_matches import get_weekly_matches_for_team
from api.cache import get_cached, set_cached

logger = logging.getLogger(__name__)

# Team configuration for weekly matches
WEEKLY_TEAMS = [
    {"name": "Dodgers", "id": 19, "sport": "baseball", "league": "mlb", "emoji": "⚾"},
    {"name": "Lakers", "id": 13, "sport": "basketball", "league": "nba", "emoji": "🏀"},
    {"name": "Galaxy", "id": 187, "sport": "soccer", "league": "usa.1", "emoji": "⚽"},
    {"name": "Rams", "id": 14, "sport": "football", "league": "nfl", "emoji": "🏈"},
]


async def get_weekly_cache_key() -> str:
    """Generate cache key for weekly matches data"""
    pacific_tz = pytz.timezone("America/Los_Angeles")
    now_pacific = datetime.now(pacific_tz)
    days_since_monday = now_pacific.weekday()
    week_start = now_pacific - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    return f"weekly_matches_{week_start.strftime('%Y%m%d')}"


async def get_weekly_matches_optimized() -> Tuple[
    Dict[str, List[Dict]], Dict[str, Any]
]:
    """Get weekly matches for all teams with parallel processing and caching"""
    start_time = time.time()

    # Check cache first
    cache_key = await get_weekly_cache_key()
    cached_data = await get_cached(cache_key)

    if cached_data:
        logger.info("Using cached weekly matches data")
        return cached_data["team_games"], {
            "cache_hit": True,
            "duration": time.time() - start_time,
        }

    logger.info("Fetching fresh weekly matches data")

    # Create tasks for parallel execution
    tasks = []
    for team in WEEKLY_TEAMS:
        task = get_weekly_matches_for_team(
            team["name"], team["id"], team["sport"], team["league"]
        )
        tasks.append((team["name"], task))

    # Execute all tasks in parallel
    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

    # Process results and handle errors
    team_games = {}
    errors = {}

    for i, (team_name, result) in enumerate(
        zip([team["name"] for team in WEEKLY_TEAMS], results)
    ):
        if isinstance(result, Exception):
            logger.error(f"Error fetching games for {team_name}: {result}")
            errors[team_name] = str(result)
            team_games[team_name] = []
        else:
            team_games[team_name] = result

    # Cache the results for 1 hour
    cache_data = {"team_games": team_games, "errors": errors, "timestamp": time.time()}
    await set_cached(cache_key, cache_data, "game_data")

    duration = time.time() - start_time
    logger.info(f"Weekly matches data fetched in {duration:.2f}s")

    return team_games, {"cache_hit": False, "duration": duration, "errors": errors}


async def create_optimized_weekly_embed(
    team_games: Dict[str, List[Dict]], metadata: Dict[str, Any]
) -> discord.Embed:
    """Create an optimized weekly matches embed"""
    try:
        # Calculate week boundaries
        pacific_tz = pytz.timezone("America/Los_Angeles")
        now_pacific = datetime.now(pacific_tz)
        days_since_monday = now_pacific.weekday()
        week_start = now_pacific - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)

        # Create embed
        embed = discord.Embed(
            title="🏆 LA Teams Weekly Schedule",
            description=f"**📅 Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}**\n\n",
            color=0x00923F,
            timestamp=datetime.now(),
        )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Calculate total games
        total_games = sum(len(games) for games in team_games.values())

        # Add performance info
        cache_status = "🟢 Cached" if metadata.get("cache_hit") else "🔄 Fresh"
        duration = metadata.get("duration", 0)
        embed.add_field(
            name="📊 Performance",
            value=f"**Status:** {cache_status}\n**Duration:** {duration:.2f}s\n**Total Games:** {total_games}",
            inline=True,
        )

        # Add error info if any
        errors = metadata.get("errors", {})
        if errors:
            error_text = "\n".join(
                [f"• {team}: {error}" for team, error in errors.items()]
            )
            embed.add_field(
                name="⚠️ Errors",
                value=error_text[:1024],  # Discord field limit
                inline=False,
            )

        # Add team sections
        for team in WEEKLY_TEAMS:
            team_name = team["name"]
            games = team_games.get(team_name, [])
            emoji = team["emoji"]

            if games:
                # Format games (limit to 5 per team)
                game_texts = []
                for game in games[:5]:
                    try:
                        if game.get("date"):
                            game_date = datetime.fromisoformat(
                                game["date"].replace("Z", "+00:00")
                            )
                            game_date_pacific = game_date.astimezone(pacific_tz)
                            formatted_date = game_date_pacific.strftime("%a, %b %d")
                            formatted_time = game_date_pacific.strftime("%I:%M %p PT")
                        else:
                            formatted_date = "TBD"
                            formatted_time = "TBD"

                        # Get opponent info
                        opponent = "TBD"
                        home_away = ""
                        competitions = game.get("competitions", [])
                        if competitions:
                            competition = competitions[0]
                            competitors = competition.get("competitors", [])

                            if len(competitors) >= 2:
                                for competitor in competitors:
                                    if competitor.get("id") != str(team["id"]):
                                        team_ref = competitor.get("team", {}).get(
                                            "$ref", ""
                                        )
                                        if team_ref:
                                            from api.espn.teams import (
                                                get_team_name_from_ref,
                                            )

                                            opponent = await get_team_name_from_ref(
                                                team_ref
                                            )
                                        home_away = (
                                            "vs"
                                            if competitor.get("homeAway") == "away"
                                            else "@"
                                        )
                                        break

                        # Get venue
                        venue = "TBD"
                        if competitions:
                            venue_info = competition.get("venue", {})
                            venue = venue_info.get("fullName", "TBD")

                        # Format game text
                        if opponent == "TBD":
                            game_text = f"**{formatted_date}** at **{formatted_time}**\n🎯 {game.get('name', 'Match')}\n🏟️ {venue}"
                        else:
                            home_away_emoji = "🏠" if home_away == "vs" else "✈️"
                            game_text = f"**{formatted_date}** at **{formatted_time}**\n{home_away_emoji} {home_away} **{opponent}**\n🏟️ {venue}"

                        game_texts.append(game_text)
                    except Exception as e:
                        logger.warning(f"Error formatting game for {team_name}: {e}")
                        continue

                if game_texts:
                    team_text = (
                        f"{emoji} **{team_name}** ({len(game_texts)} games)\n\n"
                        + "\n\n".join(game_texts)
                    )
                    if len(team_text) > 1024:
                        team_text = team_text[:1021] + "..."
                    embed.add_field(name="", value=team_text, inline=False)
            else:
                embed.add_field(
                    name=f"{emoji} {team_name}",
                    value="*No games scheduled this week*",
                    inline=False,
                )

        # Add footer
        embed.set_footer(text="🔄 Updates every Monday at 1pm PT • 🏆 Go LA!")

        return embed

    except Exception as e:
        logger.error(f"Error creating optimized weekly embed: {e}")
        # Return error embed
        embed = discord.Embed(
            title="🏆 LA Teams Weekly Schedule",
            description="❌ Error loading weekly schedule",
            color=0xFF0000,
        )
        return embed


@app_commands.command(
    name="weekly",
    description="Send the weekly matches notification for LA teams (Monday-Sunday schedule)",
)
async def weekly_command(interaction: discord.Interaction):
    """Send the weekly matches notification with optimizations"""
    try:
        logger.info(f"Weekly command called by {interaction.user}")

        # Send typing indicator
        await interaction.response.defer(ephemeral=True)

        # Send progress update
        await interaction.followup.send(
            "🔄 Fetching weekly matches data...", ephemeral=True
        )

        # Get weekly matches data (with caching and parallel processing)
        team_games, metadata = await get_weekly_matches_optimized()

        # Send progress update
        await interaction.followup.send(
            "🎨 Creating weekly schedule...", ephemeral=True
        )

        # Create optimized embed
        embed = await create_optimized_weekly_embed(team_games, metadata)

        # Send the embed to the channel
        await interaction.channel.send(embed=embed)

        # Send final confirmation
        cache_status = "cached" if metadata.get("cache_hit") else "fresh"
        duration = metadata.get("duration", 0)
        await interaction.followup.send(
            f"✅ Weekly matches notification sent! ({cache_status} data, {duration:.2f}s)",
            ephemeral=True,
        )

    except Exception as e:
        logger.error(f"Error in weekly command: {e}")
        await interaction.followup.send(
            "❌ Error sending weekly matches notification", ephemeral=True
        )


# Export the command
weekly_command = weekly_command
