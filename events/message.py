"""
Message event handler
"""

import logging

logger = logging.getLogger(__name__)


async def on_message(bot, message):
    """Handle regular messages"""
    if message.author == bot.user:
        return

    # Process commands
    logger.info(f"Processing message: {message.content} from {message.author}")
    await bot.process_commands(message)
