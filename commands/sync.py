"""
Sync command implementation
"""

from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


@commands.command(name="sync")
async def sync_command(ctx):
    """Force sync slash commands"""
    try:
        await ctx.send("Syncing commands...")
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands: {[cmd.name for cmd in synced]}")
        logger.info(f"Manual sync: {len(synced)} commands")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: {e}")
        logger.error(f"Manual sync failed: {e}")
