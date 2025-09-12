#!/usr/bin/env python3
"""
Immediate trivia trigger for Docker container
This script can be run inside the container to immediately send a trivia post
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import setup_logging, TRIVIA_CHANNEL_ID, DISCORD_TOKEN
from trivia.scheduler import TriviaScheduler
import discord

# Set up logging
logger = setup_logging()


async def trigger_trivia_now():
    """Immediately trigger a trivia post"""
    try:
        if not DISCORD_TOKEN:
            logger.error("❌ No Discord token found! Please check your .env file")
            return

        if not TRIVIA_CHANNEL_ID:
            logger.error(
                "❌ No trivia channel ID found! Please set TRIVIA_CHANNEL_ID in your .env file"
            )
            return

        logger.info(f"🎯 Triggering trivia post in channel ID: {TRIVIA_CHANNEL_ID}")

        # Create trivia scheduler
        scheduler = TriviaScheduler()

        # Create a minimal bot instance for sending the post
        intents = discord.Intents.default()
        intents.message_content = True
        bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)

        @bot.event
        async def on_ready():
            logger.info(f"🤖 Bot logged in as {bot.user}")

            # Send the trivia post
            await scheduler.send_daily_trivia_post(bot, TRIVIA_CHANNEL_ID)

            logger.info("✅ Trivia post sent! Check your Discord channel.")

            # Close the bot
            await bot.close()

        # Run the bot
        await bot.start(DISCORD_TOKEN)

    except Exception as e:
        logger.error(f"❌ Error triggering trivia: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(trigger_trivia_now())
