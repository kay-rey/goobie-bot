import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

# Enable logging
import logging
import sys

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Create a new Discord bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Set up logging to stdout so it shows in Docker logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@bot.event
async def on_ready():
    """Event that runs when the bot is ready and connected to Discord"""
    logger.info(f"🚀 {bot.user} has connected to Discord!")
    logger.info(f"📊 Bot is in {len(bot.guilds)} guilds")

    # Sync slash commands with Discord
    logger.info("🔄 Syncing slash commands...")
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} command(s)")
        for cmd in synced:
            logger.info(f"  - /{cmd.name}: {cmd.description}")
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        import traceback

        traceback.print_exc()

    logger.info("🎯 Bot ready! Try /ping command.")


@bot.tree.command(name="ping", description="Test the bot's responsiveness")
async def ping(interaction: discord.Interaction):
    """Slash command that responds with Pong!"""
    logger.info(f"Ping command triggered by {interaction.user}")
    await interaction.response.send_message("Pong!", ephemeral=True)


@bot.tree.command(name="nextgame", description="Get LA Galaxy's next match")
async def nextgame(interaction: discord.Interaction):
    """Get LA Galaxy's next match with team logos"""
    logger.info(f"Nextgame command triggered by {interaction.user}")
    await interaction.response.defer()

    try:
        # Get LA Galaxy team data from TheSportsDB
        logger.info("Fetching LA Galaxy team data...")
        team_data = await get_galaxy_team_data()
        logger.info(f"Team data result: {bool(team_data)}")
        if not team_data:
            await interaction.followup.send("❌ Could not find LA Galaxy team data")
            return

        # Get next game from ESPN API
        logger.info("Fetching next game data...")
        game_data = await get_galaxy_next_game()
        logger.info(f"Game data result: {bool(game_data)}")
        if game_data:
            logger.info(
                f"Game data structure: {json.dumps(game_data, indent=2)[:500]}..."
            )
        if not game_data:
            await interaction.followup.send(
                "❌ Could not find LA Galaxy's next game. The season may be over or no upcoming games are scheduled."
            )
            return

        # Get team ID for more detailed logo lookup
        team_id = team_data.get("idTeam")
        if team_id:
            logger.info(f"Getting detailed logos for team ID: {team_id}")
            logos = await get_team_logos(team_id)

            # If no logos found, try fallback from search results
            if not any(logos.values()):
                logger.info("No logos from lookup, trying search results...")
                logos = {
                    "logo": team_data.get("strTeamBadge", ""),
                    "jersey": team_data.get("strTeamJersey", ""),
                    "stadium": team_data.get("strStadium", ""),
                    "stadium_thumb": team_data.get("strStadiumThumb", ""),
                }
                logger.info(f"Using search result logos: {logos}")
        else:
            # Fallback to basic logo extraction
            logos = {
                "logo": team_data.get("strTeamBadge", ""),
                "jersey": team_data.get("strTeamJersey", ""),
                "stadium": team_data.get("strStadium", ""),
                "stadium_thumb": team_data.get("strStadiumThumb", ""),
            }
            logger.info(f"Using fallback logos: {logos}")

        # Create rich embed
        logger.info("Creating embed...")
        embed = create_game_embed(game_data, logos)
        await interaction.followup.send(embed=embed)
        logger.info("Nextgame command completed successfully")

    except Exception as e:
        logger.error(f"Error in nextgame command: {e}")
        import traceback

        traceback.print_exc()
        await interaction.followup.send("❌ An error occurred while fetching game data")


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    print(f"❌ Command error: {error}")


@bot.event
async def on_app_command_error(interaction, error):
    """Handle slash command errors"""
    print(f"❌ Slash command error: {error}")
    if not interaction.response.is_done():
        await interaction.response.send_message("An error occurred!", ephemeral=True)


@bot.command(name="test")
async def test_command(ctx):
    """Test command to verify bot is working"""
    await ctx.send("Bot is working!")


@bot.command(name="sync")
async def sync_commands(ctx):
    """Force sync slash commands"""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands: {[cmd.name for cmd in synced]}")
        logger.info(f"Manual sync: {len(synced)} commands")
    except Exception as e:
        await ctx.send(f"Sync failed: {e}")
        logger.error(f"Manual sync failed: {e}")


@bot.event
async def on_message(message):
    """Handle regular messages"""
    if message.author == bot.user:
        return

    # Process commands
    logger.info(f"Processing message: {message.content} from {message.author}")
    await bot.process_commands(message)


# API Helper Functions
async def get_galaxy_team_data():
    """Get LA Galaxy team data from TheSportsDB"""
    try:
        url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
        params = {"t": "LA Galaxy"}

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"TheSportsDB search response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Search results: {json.dumps(data, indent=2)[:500]}...")
            if data.get("teams") and len(data["teams"]) > 0:
                # Find LA Galaxy specifically (not Arsenal)
                for team in data["teams"]:
                    if "LA Galaxy" in team.get("strTeam", "") and "Soccer" in team.get(
                        "strSport", ""
                    ):
                        logger.info(
                            f"Found LA Galaxy team: {team['strTeam']} with ID: {team['idTeam']}"
                        )
                        return team
                # Fallback to first result if no exact match
                return data["teams"][0]
        return None
    except Exception as e:
        logger.error(f"Error getting Galaxy team data: {e}")
        return None


async def get_galaxy_next_game():
    """Get LA Galaxy's next game from ESPN API"""
    try:
        from datetime import datetime, timedelta

        # Get current date and create a date range for upcoming games
        today = datetime.now()
        # Start from today and go 6 months into the future
        start_date = today.strftime("%Y%m%d")
        end_date = (today + timedelta(days=180)).strftime("%Y%m%d")

        # ESPN API endpoint for MLS LA Galaxy
        url = "https://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
        params = {
            "limit": 10,
            "dates": f"{start_date}-{end_date}",
        }  # Get more results to filter

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"ESPN API response status: {response.status_code}")
        logger.info(f"Date range: {start_date} to {end_date}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"ESPN API data keys: {list(data.keys())}")
            if data.get("items") and len(data["items"]) > 0:
                # Find the first upcoming game (not past)
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
                                    # Parse the event date
                                    event_date = datetime.fromisoformat(
                                        event_date_str.replace("Z", "+00:00")
                                    )
                                    # Check if the event is in the future
                                    if event_date > today:
                                        logger.info(
                                            f"Found upcoming game on {event_date.strftime('%Y-%m-%d %H:%M')}"
                                        )
                                        return event_data
                                    else:
                                        logger.info(
                                            f"Skipping past game on {event_date.strftime('%Y-%m-%d %H:%M')}"
                                        )
                                except Exception as date_error:
                                    logger.warning(
                                        f"Error parsing date {event_date_str}: {date_error}"
                                    )
                                    # If we can't parse the date, assume it's upcoming
                                    return event_data

                # If no upcoming games found, return the first one anyway
                logger.warning(
                    "No upcoming games found, returning first available game"
                )
                event_ref = data["items"][0].get("$ref")
                if event_ref:
                    event_response = requests.get(event_ref, timeout=10)
                    if event_response.status_code == 200:
                        return event_response.json()
                return data["items"][0]
        else:
            logger.error(f"ESPN API error: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error getting Galaxy next game: {e}")
        return None


async def get_team_logos(team_id):
    """Get team logos from TheSportsDB"""
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/123/lookupteam.php?id={team_id}"

        response = requests.get(url, timeout=10)
        logger.info(f"TheSportsDB response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"TheSportsDB data: {json.dumps(data, indent=2)[:500]}...")
            if data.get("teams") and len(data["teams"]) > 0:
                team = data["teams"][0]
                logger.info(
                    f"Team found: {team.get('strTeam', 'Unknown')} (ID: {team.get('idTeam', 'Unknown')})"
                )

                # Check if this is the right team
                if team.get("idTeam") != str(team_id):
                    logger.warning(
                        f"Team ID mismatch! Expected {team_id}, got {team.get('idTeam')}"
                    )

                logos = {
                    "logo": team.get("strTeamBadge", ""),
                    "jersey": team.get("strTeamJersey", ""),
                    "stadium": team.get("strStadium", ""),
                    "stadium_thumb": team.get("strStadiumThumb", ""),
                }
                logger.info(f"Extracted logos: {logos}")

                # Test logo URLs for validity
                for logo_type, logo_url in logos.items():
                    if logo_url:
                        is_valid = await test_logo_url(logo_url)
                        logger.info(f"Logo {logo_type}: {logo_url} - Valid: {is_valid}")
                        if not is_valid:
                            logos[logo_type] = ""

                return logos
        return {}
    except Exception as e:
        logger.error(f"Error getting team logos: {e}")
        return {}


async def test_logo_url(url):
    """Test if a logo URL is valid and accessible"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def create_game_embed(game_data, logos):
    """Create a rich Discord embed for the game"""
    embed = discord.Embed(
        title="⚽ LA Galaxy Next Match",
        color=0x1A1A1A,  # Galaxy colors
        timestamp=datetime.utcnow(),
    )

    # Log logo availability for debugging
    logger.info(f"Creating embed with logos: {logos}")

    # Add team logo if available
    if logos.get("logo"):
        logger.info(f"Setting thumbnail to: {logos['logo']}")
        embed.set_thumbnail(url=logos["logo"])
    else:
        logger.warning("No team logo available")

    # Extract game information
    competition = game_data.get("competitions", [{}])[0]
    date = competition.get("date", "")
    venue = competition.get("venue", {}).get("fullName", "TBD")

    # Format date
    if date:
        try:
            game_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
            # Convert to local time (you can adjust timezone as needed)
            formatted_date = game_date.strftime("%A, %B %d, %Y at %I:%M %p")
            embed.add_field(name="📅 Date", value=formatted_date, inline=True)
            logger.info(f"Game date: {game_date} (UTC) -> {formatted_date}")
        except Exception as e:
            logger.warning(f"Error formatting date {date}: {e}")
            embed.add_field(name="📅 Date", value=date, inline=True)

    # Add venue
    embed.add_field(name="🏟️ Venue", value=venue, inline=True)

    # Add competition info
    league = competition.get("league", {}).get("name", "MLS")
    embed.add_field(name="🏆 Competition", value=league, inline=True)

    # Add teams
    competitors = competition.get("competitors", [])
    if len(competitors) >= 2:
        # Log the competitor structure for debugging
        logger.info(
            f"Competitor 0 structure: {json.dumps(competitors[0], indent=2)[:500]}..."
        )
        logger.info(
            f"Competitor 1 structure: {json.dumps(competitors[1], indent=2)[:500]}..."
        )

        # Try different possible team name fields
        home_team = (
            competitors[0].get("team", {}).get("displayName")
            or competitors[0].get("team", {}).get("name")
            or competitors[0].get("team", {}).get("shortDisplayName")
            or competitors[0].get("team", {}).get("abbreviation")
            or "TBD"
        )
        away_team = (
            competitors[1].get("team", {}).get("displayName")
            or competitors[1].get("team", {}).get("name")
            or competitors[1].get("team", {}).get("shortDisplayName")
            or competitors[1].get("team", {}).get("abbreviation")
            or "TBD"
        )
        embed.add_field(name="🏠 Home", value=home_team, inline=True)
        embed.add_field(name="✈️ Away", value=away_team, inline=True)

    # Add stadium image if available
    if logos.get("stadium_thumb"):
        logger.info(f"Setting image to: {logos['stadium_thumb']}")
        embed.set_image(url=logos["stadium_thumb"])
    else:
        logger.warning("No stadium image available")

    embed.set_footer(text="Data provided by ESPN API • Logos by TheSportsDB")

    return embed


# Run the bot with the token from the .env file
if __name__ == "__main__":
    if DISCORD_TOKEN:
        logger.info("🤖 Starting goobie-bot...")
        logger.info("🔑 Discord Token found")
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"❌ Bot crashed: {e}")
            import traceback

            traceback.print_exc()
    else:
        logger.error("Error: DISCORD_TOKEN not found in environment variables!")
        logger.error("Please make sure your .env file contains a valid DISCORD_TOKEN.")
