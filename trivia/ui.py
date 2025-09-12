"""
Discord UI components for trivia
Handles buttons, embeds, and private trivia sessions
"""

import discord
import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .database import TriviaDatabase

logger = logging.getLogger(__name__)


class TriviaView(discord.ui.View):
    """View for daily trivia post with buttons"""

    def __init__(self, db: TriviaDatabase, question_id: int):
        super().__init__(timeout=None)  # No timeout for persistent buttons
        self.db = db
        self.question_id = question_id

    @discord.ui.button(
        label="🎯 Start Trivia",
        style=discord.ButtonStyle.primary,
        custom_id="start_trivia",
    )
    async def start_trivia(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Handle start trivia button click"""
        try:
            logger.info(
                f"🎯 Start trivia button clicked by {interaction.user} (ID: {interaction.user.id})"
            )

            # Check if user already played today
            has_played = self.db.has_user_played_today(interaction.user.id)
            logger.info(f"📊 User {interaction.user.id} has played today: {has_played}")

            if has_played:
                logger.info(
                    f"❌ User {interaction.user.id} already played today, blocking"
                )
                await interaction.response.send_message(
                    "❌ You've already played today's trivia! Come back tomorrow at 8 PM PT for a new question.",
                    ephemeral=True,
                )
                return

            # Create or update user score record
            logger.info(
                f"👤 Creating/updating user score for {interaction.user.display_name}"
            )
            user_created = self.db.create_user_score(
                interaction.user.id, interaction.user.display_name
            )
            logger.info(f"✅ User score created/updated: {user_created}")

            # Start private trivia session
            logger.info(f"🚀 Starting private trivia session for {interaction.user}")
            await self._start_private_trivia(interaction)

        except Exception as e:
            logger.error(
                f"❌ Error starting trivia for user {interaction.user.id}: {e}"
            )
            import traceback

            logger.error(f"❌ Full traceback: {traceback.format_exc()}")

            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while starting trivia. Please try again.",
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        "❌ An error occurred while starting trivia. Please try again.",
                        ephemeral=True,
                    )
            except Exception as followup_error:
                logger.error(f"❌ Error sending followup message: {followup_error}")

    @discord.ui.button(
        label="📊 Leaderboard",
        style=discord.ButtonStyle.secondary,
        custom_id="view_leaderboard",
    )
    async def view_leaderboard(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Handle leaderboard button click"""
        try:
            leaderboard = self.db.get_leaderboard(10)

            if not leaderboard:
                await interaction.response.send_message(
                    "📊 No trivia scores yet! Be the first to play!", ephemeral=True
                )
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
                medal = (
                    "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                )
                accuracy = (
                    (user["correct_answers"] / user["questions_answered"] * 100)
                    if user["questions_answered"] > 0
                    else 0
                )
                leaderboard_text += f"{medal} **{user['username']}** - {user['total_score']} pts ({accuracy:.1f}% accuracy)\n"

            embed.add_field(name="Rankings", value=leaderboard_text, inline=False)

            # Add user's rank if they have a score
            user_score = self.db.get_user_score(interaction.user.id)
            if user_score:
                user_rank = self.db.get_user_rank(interaction.user.id)
                embed.add_field(
                    name="Your Stats",
                    value=f"Rank: #{user_rank}\nScore: {user_score['total_score']} pts\nStreak: {user_score['current_streak']}",
                    inline=True,
                )

            embed.set_footer(text="Updated every 24 hours at 8 PM PT")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error showing leaderboard: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while loading the leaderboard.", ephemeral=True
            )

    @discord.ui.button(
        label="❓ How to Play",
        style=discord.ButtonStyle.secondary,
        custom_id="how_to_play",
    )
    async def how_to_play(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Handle how to play button click"""
        embed = discord.Embed(
            title="❓ How to Play Daily Trivia",
            description="Learn how to participate in daily trivia!",
            color=0x00923F,
        )

        embed.add_field(
            name="🎯 Getting Started",
            value="Click the 'Start Trivia' button to begin your private trivia session. You'll receive a DM with your question.",
            inline=False,
        )

        embed.add_field(
            name="⏰ Timing",
            value="You have 30 seconds to answer each question. Answer quickly for bonus points!",
            inline=False,
        )

        embed.add_field(
            name="🏆 Scoring",
            value="• Easy questions: 10 points base\n• Medium questions: 20 points base\n• Hard questions: 30 points base\n• Speed bonus: +1-5 points\n• Streak bonus: +10% for 3+ correct",
            inline=False,
        )

        embed.add_field(
            name="📊 Leaderboard",
            value="Compete with other players! Check your rank and stats anytime.",
            inline=False,
        )

        embed.add_field(
            name="🔄 Daily Reset",
            value="New trivia question every day at 8 PM PT. You can only play once per day.",
            inline=False,
        )

        embed.set_footer(text="Good luck and have fun!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _start_private_trivia(self, interaction: discord.Interaction):
        """Start private trivia session in DM"""
        try:
            logger.info(f"🔍 Getting random question for user {interaction.user.id}")

            # Get today's question
            question = self.db.get_random_question()
            logger.info(f"📝 Question retrieved: {question is not None}")

            if not question:
                logger.error(f"❌ No question available for user {interaction.user.id}")
                await interaction.response.send_message(
                    "❌ No trivia question available today. Please try again later.",
                    ephemeral=True,
                )
                return

            logger.info(
                f"📋 Question details: ID={question.get('id')}, Category={question.get('category')}, Difficulty={question.get('difficulty')}"
            )

            # Send initial response
            logger.info(f"💬 Sending initial response to user {interaction.user.id}")
            await interaction.response.send_message(
                "🎯 Starting your trivia session! Check your DMs for the question.",
                ephemeral=True,
            )

            # Create private trivia session
            logger.info(f"🎮 Creating private trivia session for {interaction.user}")
            session = PrivateTriviaSession(self.db, interaction.user, question)
            await session.start()
            logger.info(
                f"✅ Private trivia session started successfully for {interaction.user}"
            )

        except Exception as e:
            logger.error(
                f"❌ Error starting private trivia for user {interaction.user.id}: {e}"
            )
            import traceback

            logger.error(f"❌ Full traceback: {traceback.format_exc()}")

            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while starting trivia. Please try again.",
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        "❌ An error occurred while starting trivia. Please try again.",
                        ephemeral=True,
                    )
            except Exception as followup_error:
                logger.error(f"❌ Error sending followup message: {followup_error}")


class PrivateTriviaSession:
    """Handles private trivia sessions in DMs"""

    def __init__(
        self, db: TriviaDatabase, user: discord.User, question: Dict[str, Any]
    ):
        self.db = db
        self.user = user
        self.question = question
        self.start_time = None
        self.score = 0

    async def start(self):
        """Start the trivia session"""
        try:
            logger.info(
                f"🎯 Starting trivia session for user {self.user.id} ({self.user.display_name})"
            )
            logger.info(f"📋 Question: {self.question['question'][:50]}...")

            # Create question embed
            embed = discord.Embed(
                title="🧠 Daily Trivia Question",
                description=f"**Category:** {self.question['category'].title()}\n"
                f"**Difficulty:** {self.question['difficulty'].title()}\n\n"
                f"**Question:** {self.question['question']}",
                color=0x00923F,
                timestamp=datetime.now(),
            )

            # Create answer options
            options = [self.question["correct_answer"]] + self.question["wrong_answers"]
            random.shuffle(options)
            logger.info(f"🔀 Answer options shuffled: {len(options)} options")

            # Create view with answer buttons
            view = TriviaAnswerView(self.db, self.question, options, self.user)
            logger.info(
                f"🎮 Created trivia answer view with {len(view.children)} buttons"
            )

            # Set start time for timeout checking
            view.start_time = datetime.now()
            self.start_time = view.start_time
            logger.info(f"⏰ Timer started for user {self.user.id}")

            # Send question to user
            logger.info(f"📤 Sending DM to user {self.user.id}")
            message = await self.user.send(embed=embed, view=view)
            logger.info(f"✅ DM sent successfully to user {self.user.id}")

            # Start countdown
            view.countdown_task = asyncio.create_task(view.start_countdown(message))
            logger.info(f"⏰ Countdown started for user {self.user.id}")

        except Exception as e:
            logger.error(
                f"❌ Error starting trivia session for user {self.user.id}: {e}"
            )
            import traceback

            logger.error(f"❌ Full traceback: {traceback.format_exc()}")

            try:
                await self.user.send(
                    "❌ An error occurred while starting trivia. Please try again."
                )
            except Exception as dm_error:
                logger.error(
                    f"❌ Error sending error DM to user {self.user.id}: {dm_error}"
                )


class TriviaAnswerView(discord.ui.View):
    """View for trivia answer options"""

    def __init__(
        self,
        db: TriviaDatabase,
        question: Dict[str, Any],
        options: List[str],
        user: discord.User,
    ):
        super().__init__(timeout=30)  # 30 second timeout
        self.db = db
        self.question = question
        self.options = options
        self.user = user
        self.answered = False
        self.countdown_task = None
        self.start_time = None

        # Create buttons for each option
        for i, option in enumerate(options):
            button = discord.ui.Button(
                label=option,
                style=discord.ButtonStyle.secondary,
                custom_id=f"answer_{i}",
            )
            button.callback = self.create_answer_callback(i, option)
            self.add_item(button)

    async def start_countdown(self, original_message):
        """Start countdown messages at 30, 20, 10, and 5 seconds"""
        try:
            countdown_times = [
                20,
                10,
                5,
            ]  # Start with 20s since initial message shows 30s

            for remaining_time in countdown_times:
                if self.answered:
                    break  # Stop countdown if user already answered

                # Wait for the appropriate time
                if remaining_time == 20:
                    await asyncio.sleep(10)  # Wait 10s to reach 20s
                elif remaining_time == 10:
                    await asyncio.sleep(10)  # Wait 10s to reach 10s
                elif remaining_time == 5:
                    await asyncio.sleep(5)  # Wait 5s to reach 5s

                if not self.answered:
                    # Create countdown embed
                    embed = discord.Embed(
                        title=f"⏰ {remaining_time} seconds remaining!",
                        description=f"**Question:** {self.question['question']}\n\n"
                        f"⏰ **Time left:** {remaining_time} seconds\n"
                        f"🏷️ **Category:** {self.question['category'].title()}\n"
                        f"⚡ **Difficulty:** {self.question['difficulty'].title()}",
                        color=0xFFA500
                        if remaining_time > 10
                        else 0xFF0000,  # Orange for >10s, Red for ≤10s
                        timestamp=datetime.now(),
                    )

                    # Add answer options
                    options_text = ""
                    for i, option in enumerate(self.options, 1):
                        options_text += f"{i}. {option}\n"
                    embed.add_field(
                        name="Answer Options", value=options_text, inline=False
                    )

                    if remaining_time <= 5:
                        embed.set_footer(text="🚨 HURRY UP! Time is running out!")
                    else:
                        embed.set_footer(
                            text="Click an answer button to submit your response!"
                        )

                    # Update the message
                    try:
                        await original_message.edit(embed=embed, view=self)
                        logger.info(
                            f"⏰ Countdown update sent: {remaining_time} seconds remaining for user {self.user.id}"
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Could not update countdown message: {e}")

        except Exception as e:
            logger.error(f"❌ Error in countdown: {e}")

    def create_answer_callback(self, index: int, option: str):
        """Create callback for answer button"""

        async def answer_callback(interaction: discord.Interaction):
            if interaction.user != self.user:
                await interaction.response.send_message(
                    "❌ This trivia session is not yours!", ephemeral=True
                )
                return

            if self.answered:
                await interaction.response.send_message(
                    "❌ You already answered this question!", ephemeral=True
                )
                return

            # Check if time has expired (30 seconds)
            if hasattr(self, "start_time") and self.start_time:
                time_elapsed = (datetime.now() - self.start_time).total_seconds()
                if time_elapsed > 30:
                    await interaction.response.send_message(
                        "⏰ Time's up! You can't answer after 30 seconds.",
                        ephemeral=True,
                    )
                    return

            self.answered = True

            # Stop countdown if running
            if self.countdown_task and not self.countdown_task.done():
                self.countdown_task.cancel()
                logger.info(
                    f"⏰ Countdown stopped for user {self.user.id} - they answered"
                )

            # Calculate score
            is_correct = option == self.question["correct_answer"]
            time_taken = (
                datetime.now() - datetime.now()
            ).total_seconds()  # Placeholder for now

            # Calculate points based on difficulty and speed
            base_points = {"easy": 10, "medium": 20, "hard": 30}[
                self.question["difficulty"]
            ]
            speed_bonus = 5  # Placeholder - would calculate based on actual time
            total_points = base_points + speed_bonus if is_correct else 0

            # Update user score
            self.db.update_user_score(
                self.user.id, total_points, is_correct, time_taken
            )

            # Create result embed
            embed = discord.Embed(
                title="🎯 Trivia Result",
                color=0x00FF00 if is_correct else 0xFF0000,
                timestamp=datetime.now(),
            )

            if is_correct:
                embed.description = f"✅ **Correct!** You earned {total_points} points!"
                embed.add_field(
                    name="Answer",
                    value=f"**{self.question['correct_answer']}**",
                    inline=False,
                )
            else:
                embed.description = f"❌ **Incorrect!** The correct answer was:"
                embed.add_field(
                    name="Correct Answer",
                    value=f"**{self.question['correct_answer']}**",
                    inline=False,
                )

            # Add user stats
            user_score = self.db.get_user_score(self.user.id)
            if user_score:
                embed.add_field(
                    name="Your Stats",
                    value=f"Total Score: {user_score['total_score']} pts\n"
                    f"Questions Answered: {user_score['questions_answered']}\n"
                    f"Current Streak: {user_score['current_streak']}",
                    inline=False,
                )

            embed.set_footer(
                text="Thanks for playing! Come back tomorrow for a new question."
            )

            await interaction.response.send_message(embed=embed)

            # Disable all buttons
            for item in self.children:
                item.disabled = True

            # Update the message
            await interaction.edit_original_response(view=self)

        return answer_callback

    async def on_timeout(self):
        """Handle timeout when user doesn't answer in time"""
        if not self.answered:
            logger.info(f"⏰ Timeout triggered for user {self.user.id}")

            # Stop countdown if running
            if self.countdown_task and not self.countdown_task.done():
                self.countdown_task.cancel()
                logger.info(
                    f"⏰ Countdown cancelled due to timeout for user {self.user.id}"
                )

            # Mark as answered to prevent further interactions
            self.answered = True

            # Create timeout embed
            embed = discord.Embed(
                title="⏰ Time's Up!",
                description="You didn't answer in time. The correct answer was:",
                color=0xFF0000,
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="Correct Answer",
                value=f"**{self.question['correct_answer']}**",
                inline=False,
            )
            embed.set_footer(text="Come back tomorrow for a new question!")

            # Disable all buttons
            for item in self.children:
                item.disabled = True

            # Update the message
            try:
                await self.user.send(embed=embed, view=self)
                logger.info(f"✅ Timeout message sent to user {self.user.id}")
            except Exception as e:
                logger.error(f"❌ Error sending timeout message: {e}")
