import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api import (
    get_galaxy_team_data,
    get_galaxy_next_game_extended,
    get_team_logos,
    extract_logos_from_team,
    create_game_embed,
)

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

        # Get next game from ESPN API with logos
        logger.info("Fetching next game data...")
        game_result = await get_galaxy_next_game_extended()
        logger.info(f"Game data result: {bool(game_result)}")
        if game_result:
            logger.info(f"Game data structure: {game_result}")
        if not game_result:
            await interaction.followup.send(
                "❌ Could not find LA Galaxy's next game. The season may be over or no upcoming games are scheduled."
            )
            return

        # Extract game data and logos from the result
        game_data = game_result["game"]
        logos = game_result["logos"]
        logger.info(f"Game data: {game_data}")
        logger.info(f"Logos: {logos}")

        # If no logos found, try fallback from team data
        if not any(logos.values()):
            logger.info("No logos from game search, trying fallback...")
            team_id = team_data.get("idTeam")
            if team_id:
                fallback_logos = await get_team_logos(team_id)
                if not any(fallback_logos.values()):
                    fallback_logos = extract_logos_from_team(team_data)
                # Convert to new format
                logos = {"LA Galaxy": fallback_logos}
                logger.info(f"Using fallback logos: {logos}")

        # If still no logos, try alternative sources or use default
        if not any(logos.values()):
            logger.warning(
                "No logos found from any source, using default LA Galaxy logo"
            )
            # Use the actual working LA Galaxy logo URL from the team page
            # Reference: https://www.thesportsdb.com/team/134153-la-galaxy
            logos = {
                "LA Galaxy": {
                    "logo": "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png",
                    "logo_small": "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png/small",
                    "jersey": "",
                    "stadium": team_data.get(
                        "strStadium", "Dignity Health Sports Park"
                    ),
                    "stadium_thumb": "",
                    "stadium_thumb_small": "",
                }
            }
            logger.info(f"Using fallback logos from LA Galaxy team page: {logos}")

        # Create rich embed
        logger.info("Creating embed...")
        embed = await create_game_embed(game_data, logos)
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
        logger.error("❌ No Discord token found! Please check your .env file")
