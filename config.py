"""
Configuration module for goobie-bot
Handles environment variables, logging setup, and bot configuration
"""

import os
import sys
import logging
import discord
import asyncio
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Try to import psutil for resource monitoring (optional)
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Get the channel ID for weekly notifications (optional)
WEEKLY_NOTIFICATIONS_CHANNEL_ID = os.getenv("WEEKLY_NOTIFICATIONS_CHANNEL_ID")
if WEEKLY_NOTIFICATIONS_CHANNEL_ID:
    try:
        WEEKLY_NOTIFICATIONS_CHANNEL_ID = int(WEEKLY_NOTIFICATIONS_CHANNEL_ID)
    except ValueError:
        WEEKLY_NOTIFICATIONS_CHANNEL_ID = None

# Get the channel ID for trivia notifications (optional)
TRIVIA_CHANNEL_ID = os.getenv("TRIVIA_CHANNEL_ID")
if TRIVIA_CHANNEL_ID:
    try:
        TRIVIA_CHANNEL_ID = int(TRIVIA_CHANNEL_ID)
    except ValueError:
        TRIVIA_CHANNEL_ID = None

# Get the channel ID for daily facts notifications (optional)
FACTS_CHANNEL_ID = os.getenv("FACTS_CHANNEL_ID")
if FACTS_CHANNEL_ID:
    try:
        FACTS_CHANNEL_ID = int(FACTS_CHANNEL_ID)
    except ValueError:
        FACTS_CHANNEL_ID = None

# Get admin user IDs (optional, comma-separated)
ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "")
if ADMIN_USER_IDS:
    try:
        ADMIN_USER_IDS = [
            int(user_id.strip())
            for user_id in ADMIN_USER_IDS.split(",")
            if user_id.strip()
        ]
    except ValueError:
        ADMIN_USER_IDS = []
else:
    ADMIN_USER_IDS = []

# Pi-specific configuration (optional)
PI_MODE = os.getenv("PI_MODE", "false").lower() == "true"
MEMORY_LIMIT_MB = int(os.getenv("MEMORY_LIMIT_MB", "512"))  # Default 512MB limit
CACHE_SIZE_LIMIT = int(os.getenv("CACHE_SIZE_LIMIT", "100"))  # Max cache entries
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Create a new Discord bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True


class ResourceMonitor:
    """Monitor system resources (optional, requires psutil)"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_warnings = 0
        self.max_memory_warnings = 5

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}

        try:
            memory = psutil.virtual_memory()
            return {
                "total_mb": round(memory.total / 1024 / 1024, 2),
                "available_mb": round(memory.available / 1024 / 1024, 2),
                "used_mb": round(memory.used / 1024 / 1024, 2),
                "percent": memory.percent,
                "is_low": memory.percent > 85,
            }
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return {"error": str(e)}

    def check_memory_health(self) -> bool:
        """Check if memory usage is healthy"""
        if not PSUTIL_AVAILABLE:
            return True  # Assume healthy if we can't check

        memory_info = self.get_memory_usage()

        if "error" in memory_info:
            return True  # Assume healthy if we can't check

        if memory_info["is_low"]:
            self.memory_warnings += 1
            self.logger.warning(
                f"High memory usage: {memory_info['percent']:.1f}% "
                f"({memory_info['used_mb']:.1f}MB used, {memory_info['available_mb']:.1f}MB available)"
            )

            if self.memory_warnings >= self.max_memory_warnings:
                self.logger.error("Too many memory warnings, consider restarting")
                return False

        return True

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        if not PSUTIL_AVAILABLE:
            return 0.0

        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"Error getting CPU usage: {e}")
            return 0.0

    def log_system_info(self):
        """Log system information for debugging"""
        if not PSUTIL_AVAILABLE:
            self.logger.info("Resource monitoring not available (psutil not installed)")
            return

        memory_info = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()

        self.logger.info(
            f"System Info - Memory: {memory_info.get('percent', 0):.1f}% "
            f"({memory_info.get('used_mb', 0):.1f}MB/{memory_info.get('total_mb', 0):.1f}MB), "
            f"CPU: {cpu_usage:.1f}%"
        )


# Global resource monitor
resource_monitor = ResourceMonitor()


def setup_logging():
    """Set up logging configuration for Docker container visibility"""
    # Determine log level
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce logging from noisy libraries
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    # Log Pi-specific information if in Pi mode
    if PI_MODE:
        resource_monitor.log_system_info()
        logger.info(
            f"Pi mode enabled - Memory limit: {MEMORY_LIMIT_MB}MB, Cache limit: {CACHE_SIZE_LIMIT} entries"
        )

    return logger


def create_bot():
    """Create and configure the Discord bot instance"""
    bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)

    # Add Pi-specific attributes if in Pi mode
    if PI_MODE:
        bot.pi_mode = PI_MODE
        bot.memory_limit_mb = MEMORY_LIMIT_MB
        bot.cache_size_limit = CACHE_SIZE_LIMIT
        bot.resource_monitor = resource_monitor

    return bot


async def monitor_resources_periodically(bot):
    """Background task to monitor system resources (Pi mode only)"""
    if not PI_MODE or not PSUTIL_AVAILABLE:
        return

    logger = logging.getLogger(__name__)

    while True:
        try:
            if hasattr(bot, "resource_monitor"):
                # Check memory health
                if not bot.resource_monitor.check_memory_health():
                    logger.error("Memory health check failed, bot may need restart")

                # Log system info every hour
                if hasattr(bot, "_last_system_log"):
                    import time

                    if time.time() - bot._last_system_log > 3600:  # 1 hour
                        bot.resource_monitor.log_system_info()
                        bot._last_system_log = time.time()
                else:
                    bot._last_system_log = time.time()

            # Wait 5 minutes before next check
            await asyncio.sleep(300)

        except Exception as e:
            logger.error(f"Error in resource monitoring: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying
