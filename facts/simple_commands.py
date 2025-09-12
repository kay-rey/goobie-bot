"""
Simple commands module for facts feature
Uses JSON file directly without database complexity
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
import pytz

from .simple_facts import SimpleFacts

logger = logging.getLogger(__name__)

# Global facts instance
_facts = SimpleFacts()


@discord.app_commands.command(name="fact", description="Get a random LA sports fact")
async def fact_command(interaction: discord.Interaction):
    """Slash command to get a random fact"""
    try:
        # Get a random fact
        fact_data = _facts.get_random_fact()
        if not fact_data:
            await interaction.response.send_message(
                "❌ No facts available at the moment. Please try again later.",
                ephemeral=True,
            )
            return

        # Create embed
        embed = discord.Embed(
            title=f"{fact_data['emoji']} LA Sports Fact",
            description=f"**{fact_data['category']}**\n\n{fact_data['fact']}",
            color=0x00923F,  # LA City green
            timestamp=datetime.now(),
        )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Add footer
        embed.set_footer(text="🏆 Go LA! • Use /fact for more random facts")

        # Send response
        await interaction.response.send_message(embed=embed)

        logger.info(f"Sent fact {fact_data['id']} to {interaction.user.name}")

    except Exception as e:
        logger.error(f"Error in fact command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while getting a fact. Please try again later.",
            ephemeral=True,
        )


@discord.app_commands.command(
    name="factstats", description="Get statistics about daily facts"
)
async def fact_stats_command(interaction: discord.Interaction):
    """Slash command to get fact statistics"""
    try:
        # Check if user is admin
        from utils.permissions import is_admin

        if not is_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", ephemeral=True
            )
            return

        # Get stats
        stats = _facts.get_stats()
        if not stats:
            await interaction.response.send_message(
                "❌ Could not retrieve fact statistics.", ephemeral=True
            )
            return

        # Create embed
        embed = discord.Embed(
            title="📊 Daily Facts Statistics",
            color=0x00923F,
            timestamp=datetime.now(),
        )

        # Add stats fields
        embed.add_field(
            name="📚 Total Facts", value=str(stats["total_facts"]), inline=True
        )
        embed.add_field(
            name="🏷️ Categories", value=str(stats["category_count"]), inline=True
        )

        # Add category breakdown
        if stats["categories"]:
            category_text = "\n".join(
                [
                    f"**{cat}**: {count} facts"
                    for cat, count in sorted(stats["categories"].items())
                ]
            )
            embed.add_field(
                name="📋 By Category",
                value=category_text,
                inline=False,
            )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Add footer
        embed.set_footer(text="🏆 Go LA! • Admin only command")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logger.error(f"Error in fact stats command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while getting statistics. Please try again later.",
            ephemeral=True,
        )


@discord.app_commands.command(
    name="factsearch", description="Search for facts by keyword"
)
async def fact_search_command(interaction: discord.Interaction, search_term: str):
    """Slash command to search facts"""
    try:
        # Search facts
        matching_facts = _facts.search_facts(search_term)
        if not matching_facts:
            await interaction.response.send_message(
                f"❌ No facts found matching '{search_term}'",
                ephemeral=True,
            )
            return

        # Limit to 5 results to avoid embed limits
        display_facts = matching_facts[:5]

        # Create embed
        embed = discord.Embed(
            title=f"🔍 Facts matching '{search_term}'",
            description=f"Found {len(matching_facts)} result{'s' if len(matching_facts) != 1 else ''}",
            color=0x00923F,
            timestamp=datetime.now(),
        )

        # Add facts as fields
        for i, fact in enumerate(display_facts, 1):
            embed.add_field(
                name=f"{i}. {fact['emoji']} {fact['category']}",
                value=fact["fact"][:200] + "..."
                if len(fact["fact"]) > 200
                else fact["fact"],
                inline=False,
            )

        if len(matching_facts) > 5:
            embed.set_footer(text=f"Showing 5 of {len(matching_facts)} results")

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logger.error(f"Error in fact search command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while searching facts. Please try again later.",
            ephemeral=True,
        )


# Text command for random fact
@commands.command(name="fact")
async def fact_text_command(ctx):
    """Text command to get a random fact"""
    try:
        # Get a random fact
        fact_data = _facts.get_random_fact()
        if not fact_data:
            await ctx.send(
                "❌ No facts available at the moment. Please try again later."
            )
            return

        # Create embed
        embed = discord.Embed(
            title=f"{fact_data['emoji']} LA Sports Fact",
            description=f"**{fact_data['category']}**\n\n{fact_data['fact']}",
            color=0x00923F,  # LA City green
            timestamp=datetime.now(),
        )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Add footer
        embed.set_footer(text="🏆 Go LA! • Use !fact for more random facts")

        # Send message
        await ctx.send(embed=embed)

        logger.info(f"Sent fact {fact_data['id']} to {ctx.author.name}")

    except Exception as e:
        logger.error(f"Error in fact text command: {e}")
        await ctx.send(
            "❌ An error occurred while getting a fact. Please try again later."
        )


# Text command for fact stats
@commands.command(name="factstats")
async def fact_stats_text_command(ctx):
    """Text command to get fact statistics"""
    try:
        # Check if user is admin
        from utils.permissions import is_admin

        if not is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command.")
            return

        # Get stats
        stats = _facts.get_stats()
        if not stats:
            await ctx.send("❌ Could not retrieve fact statistics.")
            return

        # Create embed
        embed = discord.Embed(
            title="📊 Daily Facts Statistics",
            color=0x00923F,
            timestamp=datetime.now(),
        )

        # Add stats fields
        embed.add_field(
            name="📚 Total Facts", value=str(stats["total_facts"]), inline=True
        )
        embed.add_field(
            name="🏷️ Categories", value=str(stats["category_count"]), inline=True
        )

        # Add category breakdown
        if stats["categories"]:
            category_text = "\n".join(
                [
                    f"**{cat}**: {count} facts"
                    for cat, count in sorted(stats["categories"].items())
                ]
            )
            embed.add_field(
                name="📋 By Category",
                value=category_text,
                inline=False,
            )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Add footer
        embed.set_footer(text="🏆 Go LA! • Admin only command")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in fact stats text command: {e}")
        await ctx.send(
            "❌ An error occurred while getting statistics. Please try again later."
        )


# Text command for fact search
@commands.command(name="factsearch")
async def fact_search_text_command(ctx, *, search_term: str):
    """Text command to search facts"""
    try:
        # Search facts
        matching_facts = _facts.search_facts(search_term)
        if not matching_facts:
            await ctx.send(f"❌ No facts found matching '{search_term}'")
            return

        # Limit to 5 results to avoid embed limits
        display_facts = matching_facts[:5]

        # Create embed
        embed = discord.Embed(
            title=f"🔍 Facts matching '{search_term}'",
            description=f"Found {len(matching_facts)} result{'s' if len(matching_facts) != 1 else ''}",
            color=0x00923F,
            timestamp=datetime.now(),
        )

        # Add facts as fields
        for i, fact in enumerate(display_facts, 1):
            embed.add_field(
                name=f"{i}. {fact['emoji']} {fact['category']}",
                value=fact["fact"][:200] + "..."
                if len(fact["fact"]) > 200
                else fact["fact"],
                inline=False,
            )

        if len(matching_facts) > 5:
            embed.set_footer(text=f"Showing 5 of {len(matching_facts)} results")

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in fact search text command: {e}")
        await ctx.send(
            "❌ An error occurred while searching facts. Please try again later."
        )
