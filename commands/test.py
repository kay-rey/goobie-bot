"""
Test command implementation
"""

from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


@commands.command(name="test")
async def test_command(ctx):
    """Test command to verify bot is working"""
    await ctx.send("Bot is working!")
