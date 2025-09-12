#!/usr/bin/env python3
"""
Docker test script for weekly command optimizations
This script tests the weekly command functionality within the Docker container
"""

import asyncio
import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, "/app")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def test_weekly_optimizations_docker():
    """Test the weekly command optimizations in Docker environment"""
    print("🐳 Testing Weekly Command Optimizations in Docker")
    print("=" * 60)

    try:
        # Import the optimized weekly functions
        from commands.weekly import (
            get_weekly_cache_key,
            WEEKLY_TEAMS,
            get_weekly_matches_optimized,
            create_optimized_weekly_embed,
        )

        # Test 1: Cache key generation
        print("\n1. Testing cache key generation...")
        try:
            cache_key = await get_weekly_cache_key()
            print(f"   ✅ Cache key: {cache_key}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

        # Test 2: Team configuration
        print("\n2. Testing team configuration...")
        try:
            for team in WEEKLY_TEAMS:
                print(
                    f"   {team['emoji']} {team['name']}: {team['sport']} ({team['league']})"
                )
            print("   ✅ Team configuration loaded successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

        # Test 3: Optimized data fetching
        print("\n3. Testing optimized data fetching...")
        print("   ⚠️  This will make real API calls to ESPN...")

        try:
            start_time = asyncio.get_event_loop().time()
            team_games, metadata = await get_weekly_matches_optimized()
            duration = asyncio.get_event_loop().time() - start_time

            print(f"   ✅ Data fetched in {duration:.2f}s")
            print(f"   📊 Cache hit: {metadata.get('cache_hit', False)}")
            print(
                f"   🎮 Total games: {sum(len(games) for games in team_games.values())}"
            )

            # Show games per team
            for team_name, games in team_games.items():
                print(f"   {team_name}: {len(games)} games")

            # Test 4: Embed creation
            print("\n4. Testing embed creation...")
            try:
                embed = await create_optimized_weekly_embed(team_games, metadata)
                print(f"   ✅ Embed created successfully")
                print(f"   📝 Embed title: {embed.title}")
                print(f"   📊 Embed fields: {len(embed.fields)}")
            except Exception as e:
                print(f"   ❌ Error creating embed: {e}")
                return False

        except Exception as e:
            print(f"   ❌ Error fetching data: {e}")
            import traceback

            traceback.print_exc()
            return False

        print("\n🎉 All weekly optimization tests passed!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this inside the Docker container")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    success = await test_weekly_optimizations_docker()

    if success:
        print("\n✅ Weekly command optimizations are working correctly in Docker!")
        sys.exit(0)
    else:
        print("\n❌ Weekly command optimizations have issues in Docker!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
