"""
Main bot application for goobie-bot
A Discord bot for sports statistics

Version: 0.2.0-beta
Author: kay-rey
License: MIT
"""

import asyncio
from config import (
    DISCORD_TOKEN,
    WEEKLY_NOTIFICATIONS_CHANNEL_ID,
    TRIVIA_CHANNEL_ID,
    FACTS_CHANNEL_ID,
    setup_logging,
    create_bot,
    monitor_resources_periodically,
    PI_MODE,
    MEMORY_LIMIT_MB,
    CACHE_SIZE_LIMIT,
)
from events import (
    on_ready as ready_handler,
    on_message as message_handler,
    on_command_error as command_error_handler,
    on_app_command_error as app_command_error_handler,
)
from commands import nextgame_command, test_command, sync_command
from commands.weekly import weekly_command
from commands.cache import cache_command
from scheduler import scheduler_manager
from scheduler.weekly_matches import schedule_weekly_matches
from trivia.commands import trivia_command, trivia_admin_command, trigger_trivia_command
from trivia.scheduler import schedule_daily_trivia
from facts.simple_commands import (
    fact_command,
    fact_stats_text_command,
    fact_search_text_command,
)
from facts.simple_scheduler import schedule_daily_facts
from api.http_client import cleanup_http_client
from api.cache import cache_cleanup_task

# Set up logging
logger = setup_logging()

# Create bot instance
bot = create_bot()


# Register event handlers
@bot.event
async def on_ready():
    await ready_handler(bot)

    # Stop any existing schedulers to prevent duplicates on reconnection
    logger.info("Stopping any existing schedulers...")
    await scheduler_manager.stop_all_schedulers()

    # Start the weekly matches scheduler
    await scheduler_manager.start_scheduler(
        "weekly_matches", schedule_weekly_matches, bot, WEEKLY_NOTIFICATIONS_CHANNEL_ID
    )

    # Start the daily trivia scheduler
    await scheduler_manager.start_scheduler(
        "daily_trivia", schedule_daily_trivia, bot, TRIVIA_CHANNEL_ID
    )

    # Start the daily facts scheduler
    await scheduler_manager.start_scheduler(
        "daily_facts", schedule_daily_facts, bot, FACTS_CHANNEL_ID
    )

    # Start cache cleanup task
    logger.info("Starting cache cleanup task...")
    asyncio.create_task(cache_cleanup_task())

    # Start resource monitoring if in Pi mode
    if PI_MODE:
        logger.info("Starting Pi resource monitoring...")
        asyncio.create_task(monitor_resources_periodically(bot))
        logger.info(
            f"🤖 Pi mode enabled - Memory limit: {MEMORY_LIMIT_MB}MB, Cache limit: {CACHE_SIZE_LIMIT} entries"
        )


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
bot.tree.add_command(nextgame_command)
bot.tree.add_command(weekly_command)
bot.tree.add_command(trivia_command)
bot.tree.add_command(fact_command)

# Register text commands
bot.add_command(test_command)
bot.add_command(sync_command)
bot.add_command(cache_command)
bot.add_command(trivia_admin_command)
bot.add_command(trigger_trivia_command)
bot.add_command(fact_stats_text_command)
bot.add_command(fact_search_text_command)


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
