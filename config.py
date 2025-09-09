"""
Configuration module for goobie-bot
Handles environment variables, logging setup, and bot configuration
"""

import os
import sys
import logging
import discord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Create a new Discord bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True


def setup_logging():
    """Set up logging configuration for Docker container visibility"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def create_bot():
    """Create and configure the Discord bot instance"""
    return discord.ext.commands.Bot(command_prefix="!", intents=intents)
