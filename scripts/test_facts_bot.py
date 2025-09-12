#!/usr/bin/env python3
"""
Test script for the daily facts bot integration
Tests that the bot can start and load the facts feature
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_bot_imports():
    """Test that all bot imports work correctly"""
    try:
        logger.info("🧪 Testing bot imports...")

        # Test config import
        from config import FACTS_CHANNEL_ID

        logger.info(
            f"✅ Config import successful - FACTS_CHANNEL_ID: {FACTS_CHANNEL_ID}"
        )

        # Test facts imports
        from facts.database import FactsDatabase
        from facts.scheduler import schedule_daily_facts
        from facts.commands import (
            fact_command,
            fact_stats_command,
            fact_text_command,
            fact_stats_text_command,
        )

        logger.info("✅ Facts module imports successful")

        # Test database initialization
        db = FactsDatabase()
        logger.info("✅ Facts database initialization successful")

        # Test getting a fact
        fact = db.get_random_fact()
        if fact:
            logger.info(
                f"✅ Can retrieve fact: {fact['category']} - {fact['fact'][:50]}..."
            )
        else:
            logger.error("❌ Cannot retrieve facts")
            return False

        logger.info("🎉 All bot integration tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Bot integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("🚀 Starting facts bot integration tests...")

    # Test imports and basic functionality
    success = asyncio.run(test_bot_imports())

    if success:
        logger.info("🎉 All tests passed! Facts feature is ready for bot integration.")
        logger.info("📝 To use the facts feature:")
        logger.info("   1. Set FACTS_CHANNEL_ID in your .env file")
        logger.info("   2. Restart the bot")
        logger.info("   3. Use /fact or !fact commands")
        logger.info("   4. Daily facts will be posted at 12 PM PT")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the logs.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
