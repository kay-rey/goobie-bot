"""
Weekly matches scheduler for goobie-bot
Handles sending weekly match notifications every Monday at 1pm PT
"""

import asyncio
import logging
from datetime import datetime, timedelta
import pytz
import discord

from api.espn.games import get_team_games_in_date_range
from api.espn.teams import get_team_name_from_ref

logger = logging.getLogger(__name__)


async def get_weekly_matches_for_team(team_name, team_id, sport, league):
    """Get all matches for a team in the current week (Monday to Sunday)"""
    try:
        logger.info(f"Getting weekly matches for {team_name}")

        # Get current date and calculate week boundaries
        pacific_tz = pytz.timezone("America/Los_Angeles")
        now_pacific = datetime.now(pacific_tz)

        # Find the most recent Monday (start of week)
        days_since_monday = now_pacific.weekday()  # Monday is 0
        week_start = now_pacific - timedelta(days=days_since_monday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        # End of week is next Sunday
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        logger.info(f"Week boundaries: {week_start} to {week_end}")

        # Get games for the team using the new function
        games = await get_team_games_in_date_range(
            team_id, sport, league, week_start, week_end
        )

        # Filter games to only include those within the week
        filtered_games = []
        for game in games:
            if game.get("date"):
                try:
                    game_date = datetime.fromisoformat(
                        game["date"].replace("Z", "+00:00")
                    )
                    game_date_pacific = game_date.astimezone(pacific_tz)

                    # Check if game is within our week
                    if week_start <= game_date_pacific <= week_end:
                        filtered_games.append(game)
                        logger.info(f"Added {team_name} game on {game_date_pacific}")
                except Exception as e:
                    logger.warning(f"Error parsing game date for {team_name}: {e}")

        logger.info(f"Found {len(filtered_games)} games for {team_name} this week")
        return filtered_games

    except Exception as e:
        logger.error(f"Error getting weekly matches for {team_name}: {e}")
        return []


async def create_weekly_matches_embed():
    """Create a Discord embed with all weekly matches for Dodgers, Lakers, and Galaxy"""
    try:
        logger.info("Creating weekly matches embed...")

        # Get weekly matches for each team
        # Team IDs: Dodgers (19), Lakers (13), Galaxy (187)
        dodgers_games = await get_weekly_matches_for_team(
            "Dodgers", 19, "baseball", "mlb"
        )
        lakers_games = await get_weekly_matches_for_team(
            "Lakers", 13, "basketball", "nba"
        )
        galaxy_games = await get_weekly_matches_for_team(
            "Galaxy", 187, "soccer", "usa.1"
        )

        # Calculate week boundaries for display
        pacific_tz = pytz.timezone("America/Los_Angeles")
        now_pacific = datetime.now(pacific_tz)
        days_since_monday = now_pacific.weekday()
        week_start = now_pacific - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)

        # Create main embed with better formatting
        embed = discord.Embed(
            title="🏆 LA Teams Weekly Schedule",
            description=f"**📅 Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}**\n\n",
            color=0x1E90FF,  # Dodger blue
            timestamp=datetime.now(),
        )

        # Add a thumbnail or image if available
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Calculate total games for summary
        total_games = len(dodgers_games) + len(lakers_games) + len(galaxy_games)

        # Add summary field
        if total_games > 0:
            summary_text = f"⚽ Galaxy: {len(galaxy_games)} games\n"
            summary_text += f"⚾ Dodgers: {len(dodgers_games)} games\n"
            summary_text += f"🏀 Lakers: {len(lakers_games)} games"
            embed.add_field(
                name=f"**📈 Total Games This Week: {total_games}**\n",
                value=summary_text,
                inline=False,
            )

        # Add team sections with detailed game information
        teams_data = [
            ("⚽ LA Galaxy", galaxy_games, 0x00245D),
            ("⚾ Los Angeles Dodgers", dodgers_games, 0x005A9C),
            ("🏀 Los Angeles Lakers", lakers_games, 0xFDB927),
        ]

        for team_name, games, color in teams_data:
            if games:
                # Create detailed game information for each team
                game_details = []

                for i, game in enumerate(games[:5]):  # Show up to 5 games per team
                    try:
                        # Parse game date
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

                        # Get opponent information
                        opponent = "TBD"
                        home_away = ""
                        competitions = game.get("competitions", [])
                        if competitions:
                            competition = competitions[0]
                            competitors = competition.get("competitors", [])

                            # Define our LA team IDs
                            la_team_ids = {
                                "dodgers": "19",
                                "lakers": "13",
                                "galaxy": "187",  # LA Galaxy's actual ESPN team ID
                            }

                            # Get the current team ID based on team name
                            current_team_id = None
                            for team_key, team_id in la_team_ids.items():
                                if team_key in team_name.lower():
                                    current_team_id = team_id
                                    break

                            logger.info(
                                f"Processing game for {team_name} (ID: {current_team_id}): {len(competitors)} competitors"
                            )

                            if len(competitors) >= 2 and current_team_id:
                                # Find which team is the opponent (not our LA team)
                                for competitor in competitors:
                                    competitor_id = competitor.get("id", "")
                                    competitor_home_away = competitor.get(
                                        "homeAway", ""
                                    )

                                    logger.info(
                                        f"Competitor ID: {competitor_id} ({competitor_home_away})"
                                    )

                                    # If this is NOT our LA team, it's the opponent
                                    if competitor_id != current_team_id:
                                        # Get opponent name from team reference URL
                                        team_ref = competitor.get("team", {}).get(
                                            "$ref", ""
                                        )
                                        opponent_name = await get_team_name_from_ref(
                                            team_ref
                                        )
                                        opponent = opponent_name

                                        # Determine if LA team is home or away
                                        home_away = (
                                            "vs"
                                            if competitor_home_away == "away"
                                            else "@"
                                        )

                                        logger.info(
                                            f"Found opponent: {opponent} (ID: {competitor_id}, {competitor_home_away}) -> LA team is {home_away}"
                                        )
                                        break

                        # Get venue
                        venue_name = "TBD"
                        if competitions:
                            venue_info = competition.get("venue", {})
                            venue_name = venue_info.get("fullName", "TBD")

                        # Create game detail string with better formatting
                        if opponent == "TBD":
                            # Fallback to game name if opponent not found
                            game_name = game.get("name", "Match")
                            game_detail = f"**{formatted_date}** at **{formatted_time}**\n🎯 {game_name}\n🏟️ {venue_name}"
                        else:
                            # Format with better visual hierarchy
                            home_away_emoji = "🏠" if home_away == "vs" else "✈️"
                            game_detail = f"**{formatted_date}** at **{formatted_time}**\n{home_away_emoji} {home_away} **{opponent}**\n🏟️ {venue_name}"
                        game_details.append(game_detail)

                    except Exception as e:
                        logger.warning(
                            f"Error processing game {i + 1} for {team_name}: {e}"
                        )
                        continue

                # Add team section to main embed with better formatting
                if game_details:
                    # Join all game details for this team with separators
                    team_summary = "\n\n".join(game_details)

                    # Add a header for the team section
                    team_header = f"{team_name}: *{len(game_details)} game{'s' if len(game_details) != 1 else ''} this week*\n"
                    team_summary = team_summary + "\n\n"

                    # Truncate if too long for Discord embed field
                    if len(team_summary) > 1024:
                        team_summary = team_summary[:1021] + "..."

                    embed.add_field(name=team_header, value=team_summary, inline=False)
                else:
                    embed.add_field(
                        name=f"{team_name} - No Games",
                        value="*No games scheduled this week*",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name=f"{team_name} - No Games",
                    value="*No games scheduled this week*",
                    inline=False,
                )

        # Add footer with better formatting
        embed.set_footer(
            text="📊 Data from ESPN & TheSportsDB • 🔄 Updates every Monday at 1pm PT • 🏆 Go LA Teams!"
        )

        return embed

    except Exception as e:
        logger.error(f"Error creating weekly matches embed: {e}")
        # Return a basic error embed
        embed = discord.Embed(
            title="🏆 LA Teams Weekly Schedule",
            description="Error loading weekly schedule",
            color=0xFF0000,
        )
        return embed


async def send_weekly_matches_notification(bot, channel_id=None):
    """Send the weekly matches notification to Discord"""
    try:
        logger.info("Sending weekly matches notification...")

        # Create the embed
        embed = await create_weekly_matches_embed()

        # Find the channel to send to
        if channel_id:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)
                logger.info(f"Weekly matches notification sent to channel {channel_id}")
            else:
                logger.error(f"Channel {channel_id} not found")
        else:
            # Send to the first available text channel
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed=embed)
                        logger.info(
                            f"Weekly matches notification sent to {guild.name}#{channel.name}"
                        )
                        return

            logger.warning(
                "No suitable channel found to send weekly matches notification"
            )

    except Exception as e:
        logger.error(f"Error sending weekly matches notification: {e}")


async def schedule_weekly_matches(bot, channel_id=None):
    """Schedule the weekly matches notification for every Monday at 1pm PT"""
    try:
        logger.info("Setting up weekly matches scheduler...")

        pacific_tz = pytz.timezone("America/Los_Angeles")

        while True:
            # Get current time in Pacific
            now_pacific = datetime.now(pacific_tz)

            # Calculate next Monday at 1pm PT
            days_until_monday = (7 - now_pacific.weekday()) % 7
            if days_until_monday == 0:  # If it's Monday
                if now_pacific.hour >= 13:  # If it's past 1pm
                    days_until_monday = 7  # Next Monday
                else:
                    days_until_monday = 0  # Today, but wait until 1pm

            next_monday = now_pacific + timedelta(days=days_until_monday)
            next_monday = next_monday.replace(
                hour=13, minute=0, second=0, microsecond=0
            )

            # Calculate seconds until next Monday 1pm PT
            seconds_until_next = (next_monday - now_pacific).total_seconds()

            logger.info(
                f"Next weekly matches notification scheduled for: {next_monday}"
            )
            logger.info(f"Waiting {seconds_until_next / 3600:.1f} hours...")

            # Wait until next Monday 1pm PT
            await asyncio.sleep(seconds_until_next)

            # Send the notification
            await send_weekly_matches_notification(bot, channel_id)

            # Wait a bit before calculating the next run
            await asyncio.sleep(60)  # Wait 1 minute to avoid rapid re-scheduling

    except Exception as e:
        logger.error(f"Error in weekly matches scheduler: {e}")
        # Restart the scheduler after a delay
        await asyncio.sleep(300)  # Wait 5 minutes before restarting
        await schedule_weekly_matches(bot, channel_id)
