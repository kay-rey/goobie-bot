import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Create a new Discord bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Enable logging
import logging
import sys

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

    logger.info(f"🎯 Bot ready! Try /ping command.")


@bot.tree.command(name="ping", description="Test the bot's responsiveness")
async def ping(interaction: discord.Interaction):
    """Slash command that responds with Pong!"""
    logger.info(f"Ping command triggered by {interaction.user}")
    await interaction.response.send_message("Pong!", ephemeral=True)


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
    await bot.process_commands(message)


# Run the bot with the token from the .env file
if __name__ == "__main__":
    if DISCORD_TOKEN:
        logger.info("🤖 Starting goobie-bot...")
        logger.info(f"🔑 Token found: {DISCORD_TOKEN[:10]}...")
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"❌ Bot crashed: {e}")
            import traceback

            traceback.print_exc()
    else:
        logger.error("Error: DISCORD_TOKEN not found in environment variables!")
        logger.error("Please make sure your .env file contains a valid DISCORD_TOKEN.")
