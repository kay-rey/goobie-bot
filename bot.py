"""
Main bot application for goobie-bot
A Discord bot for sports statistics

Version: 0.1.0-alpha
Author: kay-rey
License: MIT
"""

import asyncio
from config import (
    DISCORD_TOKEN,
    WEEKLY_NOTIFICATIONS_CHANNEL_ID,
    setup_logging,
    create_bot,
)
from events import (
    on_ready as ready_handler,
    on_message as message_handler,
    on_command_error as command_error_handler,
    on_app_command_error as app_command_error_handler,
)
from commands import ping_command, nextgame_command, test_command, sync_command
from commands.weekly import weekly_command
from scheduler.weekly_matches import schedule_weekly_matches
from api.http_client import cleanup_http_client

# Set up logging
logger = setup_logging()

# Create bot instance
bot = create_bot()


# Register event handlers
@bot.event
async def on_ready():
    await ready_handler(bot)

    # Start the weekly matches scheduler
    logger.info("Starting weekly matches scheduler...")
    asyncio.create_task(schedule_weekly_matches(bot, WEEKLY_NOTIFICATIONS_CHANNEL_ID))


@bot.event
async def on_message(message):
    await message_handler(bot, message)


@bot.event
async def on_command_error(ctx, error):
    await command_error_handler(ctx, error)


@bot.event
async def on_app_command_error(interaction, error):
    await app_command_error_handler(interaction, error)


# Register slash commands
bot.tree.add_command(ping_command)
bot.tree.add_command(nextgame_command)
bot.tree.add_command(weekly_command)

# Register text commands
bot.add_command(test_command)
bot.add_command(sync_command)


# Run the bot with the token from the .env file
if __name__ == "__main__":
    if DISCORD_TOKEN:
        logger.info("🤖 Starting goobie-bot...")
        logger.info("🔑 Discord Token found")
        try:
            bot.run(DISCORD_TOKEN)
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot crashed: {e}")
            import traceback

            traceback.print_exc()
        finally:
            # Cleanup HTTP client
            logger.info("🧹 Cleaning up HTTP client...")
            asyncio.run(cleanup_http_client())
    else:
        logger.error("❌ No Discord token found! Please check your .env file")
