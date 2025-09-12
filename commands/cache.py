"""
Cache management command for goobie-bot
Provides cache statistics and management functionality
"""

import discord
from discord.ext import commands
import logging
from api.cache import get_cache_stats, clear_cache, cleanup_expired_cache
from utils.permissions import require_admin_permissions

logger = logging.getLogger(__name__)


@commands.command(name="cache")
async def cache_command(ctx, action: str = None):
    """Get cache statistics and manage cache - !cache <action>"""
    logger.info(f"Cache command triggered by {ctx.author} for action: {action}")

    # Check admin permissions
    if not require_admin_permissions(ctx):
        return

    try:
        if not action:
            # Show help message
            embed = discord.Embed(
                title="🔧 Cache Admin Commands",
                description="Available admin commands for cache management",
                color=0x00923F,
            )
            embed.add_field(
                name="Usage",
                value="`!cache <action>`",
                inline=False,
            )
            embed.add_field(
                name="Available Actions",
                value="• `stats` - View cache statistics\n"
                "• `clear` - Clear all cache data\n"
                "• `cleanup` - Clean up expired cache entries",
                inline=False,
            )
            await ctx.send(embed=embed)
            return

        if action == "stats":
            # Get cache statistics
            logger.info(f"Retrieving cache statistics for {ctx.author}")
            stats = await get_cache_stats()

            embed = discord.Embed(
                title="📊 Cache Statistics",
                color=0x00FF00,
                timestamp=discord.utils.utcnow(),
            )

            # Performance metrics
            hit_rate_color = (
                "🟢"
                if stats["hit_rate"] >= 70
                else "🟡"
                if stats["hit_rate"] >= 40
                else "🔴"
            )
            embed.add_field(
                name="📈 Performance",
                value=f"**Hit Rate:** {hit_rate_color} {stats['hit_rate']}%\n"
                f"**Total Requests:** {stats['total_requests']}\n"
                f"**Cache Hits:** {stats['hits']}\n"
                f"**Cache Misses:** {stats['misses']}",
                inline=True,
            )

            # Storage metrics
            embed.add_field(
                name="💾 Storage",
                value=f"**Total Entries:** {stats['total_entries']}\n"
                f"**Cache Sets:** {stats['sets']}\n"
                f"**Cache Deletes:** {stats['deletes']}\n"
                f"**Cache Clears:** {stats['clears']}",
                inline=True,
            )

            # Performance status
            if stats["total_requests"] > 0:
                if stats["hit_rate"] >= 70:
                    status = "🟢 Excellent"
                elif stats["hit_rate"] >= 40:
                    status = "🟡 Good"
                else:
                    status = "🔴 Needs Improvement"
            else:
                status = "⚪ No Data"

            embed.add_field(
                name="📊 Status",
                value=f"**Performance:** {status}\n"
                f"**Memory Usage:** {stats['total_entries']} entries\n"
                f"**Efficiency:** {stats['hit_rate']}% hit rate",
                inline=False,
            )

            embed.set_footer(
                text="Cache performance metrics • Use /cache clear to reset"
            )

            await ctx.send(embed=embed)
            logger.info(
                f"Cache statistics displayed: {stats['hit_rate']}% hit rate, {stats['total_entries']} entries"
            )

        elif action == "clear":
            # Clear all cache
            logger.info(f"Clearing all cache entries for {ctx.author}")
            cleared_count = await clear_cache()

            embed = discord.Embed(
                title="🧹 Cache Cleared",
                description=f"Successfully cleared **{cleared_count}** cache entries",
                color=0xFFA500,
                timestamp=discord.utils.utcnow(),
            )

            await ctx.send(embed=embed)
            logger.info(f"Cache cleared: {cleared_count} entries removed")

        elif action == "cleanup":
            # Cleanup expired entries
            logger.info(f"Cleaning up expired cache entries for {ctx.author}")
            cleaned_count = await cleanup_expired_cache()

            embed = discord.Embed(
                title="🧽 Cache Cleanup",
                description=f"Successfully cleaned up **{cleaned_count}** expired entries",
                color=0x00BFFF,
                timestamp=discord.utils.utcnow(),
            )

            await ctx.send(embed=embed)
            logger.info(
                f"Cache cleanup completed: {cleaned_count} expired entries removed"
            )

        logger.info(f"Cache command completed successfully for {action}")

    except Exception as e:
        logger.error(f"Error in cache command: {e}")
        import traceback

        traceback.print_exc()
        await ctx.send("❌ An error occurred while managing cache")


# Export the command
