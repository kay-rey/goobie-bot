"""
Trivia commands for goobie-bot
Handles slash commands for trivia management
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from datetime import datetime

from .database import TriviaDatabase
from utils.permissions import require_admin_permissions

logger = logging.getLogger(__name__)

# Initialize database
trivia_db = TriviaDatabase()


@app_commands.command(name="trivia", description="View trivia leaderboard and stats")
async def trivia_command(interaction: discord.Interaction):
    """Main trivia command to view leaderboard and stats"""
    try:
        logger.info(f"Trivia command triggered by {interaction.user}")

        # Get leaderboard
        leaderboard = trivia_db.get_leaderboard(10)

        if not leaderboard:
            embed = discord.Embed(
                title="🧠 Trivia Leaderboard",
                description="No trivia scores yet! Be the first to play daily trivia!",
                color=0x00923F,
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="How to Play",
                value="Daily trivia is posted every day at 8 PM PT. Look for the trivia post and click 'Start Trivia'!",
                inline=False,
            )
            await interaction.response.send_message(embed=embed)
            return

        # Create leaderboard embed
        embed = discord.Embed(
            title="🏆 Trivia Leaderboard",
            description="Top 10 trivia players",
            color=0xFFD700,
            timestamp=datetime.now(),
        )

        # Add leaderboard entries
        leaderboard_text = ""
        for i, user in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            accuracy = (
                (user["correct_answers"] / user["questions_answered"] * 100)
                if user["questions_answered"] > 0
                else 0
            )
            leaderboard_text += f"{medal} **{user['username']}** - {user['total_score']} pts ({accuracy:.1f}% accuracy)\n"

        embed.add_field(name="Rankings", value=leaderboard_text, inline=False)

        # Add user's stats if they have a score
        user_score = trivia_db.get_user_score(interaction.user.id)
        if user_score:
            user_rank = trivia_db.get_user_rank(interaction.user.id)
            embed.add_field(
                name="Your Stats",
                value=f"Rank: #{user_rank}\nScore: {user_score['total_score']} pts\n"
                f"Questions: {user_score['questions_answered']}\n"
                f"Accuracy: {(user_score['correct_answers'] / user_score['questions_answered'] * 100):.1f}%\n"
                f"Current Streak: {user_score['current_streak']}\n"
                f"Best Streak: {user_score['best_streak']}",
                inline=True,
            )
        else:
            embed.add_field(
                name="Your Stats",
                value="No trivia played yet!\nPlay daily trivia to get on the leaderboard.",
                inline=True,
            )

        embed.set_footer(text="Updated every 24 hours at 8 PM PT")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logger.error(f"Error in trivia command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while loading trivia data.", ephemeral=True
        )


@commands.command(name="trivia-admin")
async def trivia_admin_command(ctx, action: str = None):
    """Admin commands for trivia management - !trivia-admin <action>"""
    try:
        # Check admin permissions
        if not require_admin_permissions(ctx):
            return

        logger.info(f"Trivia admin command triggered by {ctx.author}: {action}")

        if not action:
            # Show help message
            embed = discord.Embed(
                title="🔧 Trivia Admin Commands",
                description="Available admin commands for trivia management",
                color=0x00923F,
            )
            embed.add_field(
                name="Usage",
                value="`!trivia-admin <action>`",
                inline=False,
            )
            embed.add_field(
                name="Available Actions",
                value="• `add` - Instructions for adding questions\n"
                "• `stats` - View trivia system statistics\n"
                "• `reset` - Reset daily trivia (emergency)",
                inline=False,
            )
            await ctx.send(embed=embed)
            return

        if action == "add":
            # For now, just show info about adding questions
            embed = discord.Embed(
                title="📝 Add Trivia Question",
                description="To add questions, edit the `trivia/data/questions.json` file and restart the bot.",
                color=0x00923F,
            )
            embed.add_field(
                name="Question Format",
                value='```json\n{\n  "question": "Your question here?",\n  "correct_answer": "Correct Answer",\n  "wrong_answers": ["Wrong 1", "Wrong 2", "Wrong 3"],\n  "category": "galaxy|dodgers|lakers|rams|kings|general",\n  "difficulty": "easy|medium|hard"\n}\n```',
                inline=False,
            )
            await ctx.send(embed=embed)

        elif action == "stats":
            # Show trivia statistics
            with trivia_db.get_connection() as conn:
                cursor = conn.cursor()

                # Get total questions
                cursor.execute("SELECT COUNT(*) FROM trivia_questions")
                total_questions = cursor.fetchone()[0]

                # Get total users
                cursor.execute("SELECT COUNT(*) FROM trivia_scores")
                total_users = cursor.fetchone()[0]

                # Get total attempts
                cursor.execute("SELECT COUNT(*) FROM trivia_attempts")
                total_attempts = cursor.fetchone()[0]

                # Get today's attempts
                cursor.execute(
                    "SELECT COUNT(*) FROM trivia_attempts WHERE date = date('now')"
                )
                today_attempts = cursor.fetchone()[0]

                # Get questions by category
                cursor.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM trivia_questions 
                    GROUP BY category
                """)
                category_stats = cursor.fetchall()

                # Get questions by difficulty
                cursor.execute("""
                    SELECT difficulty, COUNT(*) as count 
                    FROM trivia_questions 
                    GROUP BY difficulty
                """)
                difficulty_stats = cursor.fetchall()

            embed = discord.Embed(
                title="📊 Trivia Statistics",
                description="Current trivia system statistics",
                color=0x00923F,
                timestamp=datetime.now(),
            )

            embed.add_field(
                name="General Stats",
                value=f"Total Questions: {total_questions}\n"
                f"Total Users: {total_users}\n"
                f"Total Attempts: {total_attempts}\n"
                f"Today's Attempts: {today_attempts}",
                inline=True,
            )

            # Category breakdown
            category_text = ""
            for category, count in category_stats:
                category_text += f"{category.title()}: {count}\n"
            embed.add_field(
                name="Questions by Category", value=category_text, inline=True
            )

            # Difficulty breakdown
            difficulty_text = ""
            for difficulty, count in difficulty_stats:
                difficulty_text += f"{difficulty.title()}: {count}\n"
            embed.add_field(
                name="Questions by Difficulty", value=difficulty_text, inline=True
            )

            await ctx.send(embed=embed)

        elif action == "reset":
            # Reset daily trivia (emergency function)
            embed = discord.Embed(
                title="🔄 Reset Daily Trivia",
                description="This will allow trivia to be posted again today. Use only if there was an error.",
                color=0xFF0000,
            )
            embed.add_field(
                name="Warning",
                value="This action cannot be undone. Users who already played today will be able to play again.",
                inline=False,
            )

            # Create confirmation view
            view = ResetConfirmationView(trivia_db)
            await ctx.send(embed=embed, view=view, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in trivia admin command: {e}")
        await ctx.send("❌ An error occurred while processing the admin command.")


class ResetConfirmationView(discord.ui.View):
    """Confirmation view for resetting daily trivia"""

    def __init__(self, db: TriviaDatabase):
        super().__init__(timeout=30)
        self.db = db

    @discord.ui.button(label="✅ Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Confirm and execute the reset"""
        try:
            # Delete today's daily post record
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM trivia_daily_posts WHERE date = date('now')"
                )
                conn.commit()

            embed = discord.Embed(
                title="✅ Daily Trivia Reset",
                description="Daily trivia has been reset. A new trivia post can now be sent.",
                color=0x00FF00,
            )

            # Disable buttons
            for item in self.children:
                item.disabled = True

            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Error resetting daily trivia: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while resetting daily trivia.", ephemeral=True
            )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_reset(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Cancel the reset operation"""
        embed = discord.Embed(
            title="❌ Reset Cancelled",
            description="Daily trivia reset has been cancelled.",
            color=0xFF0000,
        )

        # Disable buttons
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)
