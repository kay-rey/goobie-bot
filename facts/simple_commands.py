"""
Simple commands module for facts feature
Uses JSON file directly without database complexity
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime

from .simple_facts import SimpleFacts

logger = logging.getLogger(__name__)

# Global facts instance
_facts = SimpleFacts()


@discord.app_commands.command(name="fact", description="Get a random goobie fact")
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
            title=f"{fact_data['emoji']} Goobie Fact",
            description=f"**{fact_data['category']}**\n\n{fact_data['fact']}",
            color=0xFF6B35, # Orange
            timestamp=datetime.now(),
        )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Add footer
        embed.set_footer(text="🏆 Use /fact for more random facts")

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
    name="factsearch", description="Search for goobie facts by keyword"
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

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logger.error(f"Error in fact search command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while searching facts. Please try again later.",
            ephemeral=True,
        )


# Text command for fact stats
@commands.command(name="factstats")
async def fact_stats_text_command(ctx):
    """Text command to get fact statistics"""
    # Check if user is admin
    from utils.permissions import has_admin_permissions

    if not has_admin_permissions(ctx):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    # Get stats
    try:
        stats = _facts.get_stats()
        if not stats:
            await ctx.send("❌ Could not retrieve fact statistics.")
            return
    except Exception as stats_error:
        logger.error(f"Error getting stats: {stats_error}")
        await ctx.send("❌ Error retrieving fact statistics.")
        return

    # Create embed
    try:
        embed = discord.Embed(
            title="📊 Daily Facts Statistics",
            color=0xFF6B35, # Orange
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

        # Add footer
        embed.set_footer(text="🏆 Admin only command")
    except Exception as embed_error:
        logger.error(f"Error creating embed: {embed_error}")
        await ctx.send("❌ Error creating statistics display.")
        return

    # Send as DM to keep stats private
    try:
        await ctx.author.send(embed=embed)
    except discord.Forbidden:
        # If DMs are disabled, send in channel but mention it's private
        embed.set_footer(text="🏆 Admin only command • Private stats")
        await ctx.send(embed=embed)
    except Exception as dm_error:
        logger.error(f"Error sending DM: {dm_error}")
        await ctx.send("❌ Could not send stats to DMs. Please check your DM settings.")


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
            color=0xFF6B35, # Orange
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
