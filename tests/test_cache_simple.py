#!/usr/bin/env python3
"""
Simple Cache Testing Script for goobie-bot

This script tests basic cache functionality without requiring the full bot environment.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def test_basic_cache_operations():
    """Test basic cache operations"""
    print("🧪 Testing Basic Cache Operations")
    print("=" * 40)

    try:
        from api.cache import (
            get_cached,
            set_cached,
            delete_cached,
            clear_cache,
            get_cache_stats,
        )

        # Clear cache first
        await clear_cache()

        # Test 1: Set and get value
        test_key = "test_basic_1"
        test_value = {"data": "test", "number": 42}

        await set_cached(test_key, test_value, "default")
        cached_value = await get_cached(test_key)

        if cached_value == test_value:
            print("✅ Basic Set/Get: PASSED")
        else:
            print(
                f"❌ Basic Set/Get: FAILED - Expected: {test_value}, Got: {cached_value}"
            )
            return False

        # Test 2: Cache miss
        non_existent_key = "non_existent_key"
        cached_value = await get_cached(non_existent_key)

        if cached_value is None:
            print("✅ Cache Miss: PASSED")
        else:
            print(f"❌ Cache Miss: FAILED - Expected: None, Got: {cached_value}")
            return False

        # Test 3: Delete existing key
        delete_result = await delete_cached(test_key)
        cached_value_after_delete = await get_cached(test_key)

        if delete_result and cached_value_after_delete is None:
            print("✅ Delete Existing Key: PASSED")
        else:
            print(
                f"❌ Delete Existing Key: FAILED - Delete: {delete_result}, Value after delete: {cached_value_after_delete}"
            )
            return False

        # Test 4: Statistics
        stats = await get_cache_stats()
        print(f"📊 Cache Statistics:")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Hit Rate: {stats['hit_rate']}%")
        print(f"  Total Entries: {stats['total_entries']}")

        return True

    except Exception as e:
        print(f"❌ Error in basic cache operations: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_cache_performance():
    """Test cache performance"""
    print("\n🚀 Testing Cache Performance")
    print("=" * 40)

    try:
        from api.cache import get_cached, set_cached, clear_cache, team_metadata_key

        # Clear cache
        await clear_cache()

        # Test team data caching
        team_requests = [
            ("galaxy", "LA Galaxy"),
            ("dodgers", "Los Angeles Dodgers"),
            ("lakers", "Los Angeles Lakers"),
        ]

        # First round - cache misses
        start_time = time.time()
        for team_ref, team_name in team_requests:
            cache_key = team_metadata_key(team_ref)
            # Simulate API call delay
            await asyncio.sleep(0.05)
            # Simulate team data
            team_data = {
                "id": f"team_{team_ref}",
                "name": team_name,
                "sport": "soccer"
                if team_ref == "galaxy"
                else "baseball"
                if team_ref == "dodgers"
                else "basketball",
            }
            await set_cached(cache_key, team_data, "team_metadata")

        first_round_time = time.time() - start_time
        print(f"First round (cache misses): {first_round_time:.3f}s")

        # Second round - cache hits
        start_time = time.time()
        for team_ref, team_name in team_requests:
            cache_key = team_metadata_key(team_ref)
            cached_data = await get_cached(cache_key)
            if not cached_data:
                print(f"❌ Cache miss for {team_ref}!")
                return False

        second_round_time = time.time() - start_time
        print(f"Second round (cache hits): {second_round_time:.3f}s")

        speedup = (
            first_round_time / second_round_time
            if second_round_time > 0
            else float("inf")
        )
        print(f"Speedup: {speedup:.1f}x faster")

        return True

    except Exception as e:
        print(f"❌ Error in cache performance test: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_cache_key_generators():
    """Test cache key generation"""
    print("\n🔑 Testing Cache Key Generators")
    print("=" * 40)

    try:
        from api.cache import (
            game_data_key,
            team_logos_key,
            team_metadata_key,
            venue_data_key,
            team_name_key,
        )

        # Test game data key
        game_key = game_data_key("galaxy", "soccer", "20240101", "20240107")
        expected_game_key = "game_data_galaxy_soccer_20240101_20240107"

        if game_key == expected_game_key:
            print("✅ Game Data Key: PASSED")
        else:
            print(
                f"❌ Game Data Key: FAILED - Expected: {expected_game_key}, Got: {game_key}"
            )
            return False

        # Test team logos key
        team_logos_key_result = team_logos_key("134153")
        expected_team_logos_key = "team_logos_134153"

        if team_logos_key_result == expected_team_logos_key:
            print("✅ Team Logos Key: PASSED")
        else:
            print(
                f"❌ Team Logos Key: FAILED - Expected: {expected_team_logos_key}, Got: {team_logos_key_result}"
            )
            return False

        # Test team metadata key
        team_metadata_key_result = team_metadata_key("LA Galaxy")
        expected_team_metadata_key = "team_metadata_la_galaxy"

        if team_metadata_key_result == expected_team_metadata_key:
            print("✅ Team Metadata Key: PASSED")
        else:
            print(
                f"❌ Team Metadata Key: FAILED - Expected: {expected_team_metadata_key}, Got: {team_metadata_key_result}"
            )
            return False

        return True

    except Exception as e:
        print(f"❌ Error in cache key generators test: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test runner"""
    print("🧪 Goobie-Bot Simple Cache Testing")
    print("=" * 50)

    tests = [
        ("Basic Cache Operations", test_basic_cache_operations),
        ("Cache Performance", test_cache_performance),
        ("Cache Key Generators", test_cache_key_generators),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")

    if failed == 0:
        print("\n🎉 All cache tests passed!")
        return True
    else:
        print(f"\n⚠️ {failed} cache test(s) failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
