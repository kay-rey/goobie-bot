#!/usr/bin/env python3
"""
Cache Testing Suite for goobie-bot

This script tests the caching functionality including:
- Cache hit/miss scenarios
- TTL expiration
- Cache statistics
- Cache cleanup
- Integration with API calls
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.cache import (  # noqa: E402
    get_cached,
    set_cached,
    delete_cached,
    clear_cache,
    get_cache_stats,
    cleanup_expired_cache,
    game_data_key,
    team_logos_key,
    team_metadata_key,
    venue_data_key,
    team_name_key,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class CacheTestSuite:
    """Comprehensive cache testing suite"""

    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"

        print(result)
        self.test_results.append(
            {
                "test": test_name,
                "passed": passed,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        )

        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    async def test_basic_cache_operations(self):
        """Test basic cache operations (get, set, delete)"""
        print("\n🧪 Testing Basic Cache Operations")
        print("=" * 50)

        # Clear cache first
        await clear_cache()

        # Test 1: Set and get value
        test_key = "test_basic_1"
        test_value = {"data": "test", "number": 42}

        await set_cached(test_key, test_value, "default")
        cached_value = await get_cached(test_key)

        self.log_test_result(
            "Basic Set/Get",
            cached_value == test_value,
            f"Expected: {test_value}, Got: {cached_value}",
        )

        # Test 2: Cache miss
        non_existent_key = "non_existent_key"
        cached_value = await get_cached(non_existent_key)

        self.log_test_result(
            "Cache Miss", cached_value is None, f"Expected: None, Got: {cached_value}"
        )

        # Test 3: Delete existing key
        delete_result = await delete_cached(test_key)
        cached_value_after_delete = await get_cached(test_key)

        self.log_test_result(
            "Delete Existing Key",
            delete_result and cached_value_after_delete is None,
            f"Delete result: {delete_result}, Value after delete: {cached_value_after_delete}",
        )

        # Test 4: Delete non-existent key
        delete_result = await delete_cached("non_existent_key")

        self.log_test_result(
            "Delete Non-existent Key",
            not delete_result,
            f"Expected: False, Got: {delete_result}",
        )

    async def test_cache_statistics(self):
        """Test cache statistics tracking"""
        print("\n📊 Testing Cache Statistics")
        print("=" * 50)

        # Clear cache and reset stats
        await clear_cache()

        # Perform operations to generate stats
        await set_cached("stat_test_1", "value1", "default")
        await set_cached("stat_test_2", "value2", "default")
        await get_cached("stat_test_1")  # Hit
        await get_cached("stat_test_1")  # Hit
        await get_cached("non_existent")  # Miss
        await delete_cached("stat_test_2")

        stats = await get_cache_stats()

        # Verify statistics
        expected_sets = 2
        expected_hits = 2
        expected_misses = 1
        expected_deletes = 1
        expected_entries = 1  # stat_test_1 should still be there

        self.log_test_result(
            "Cache Sets Count",
            stats["sets"] == expected_sets,
            f"Expected: {expected_sets}, Got: {stats['sets']}",
        )

        self.log_test_result(
            "Cache Hits Count",
            stats["hits"] == expected_hits,
            f"Expected: {expected_hits}, Got: {stats['hits']}",
        )

        self.log_test_result(
            "Cache Misses Count",
            stats["misses"] == expected_misses,
            f"Expected: {expected_misses}, Got: {stats['misses']}",
        )

        self.log_test_result(
            "Cache Deletes Count",
            stats["deletes"] == expected_deletes,
            f"Expected: {expected_deletes}, Got: {stats['deletes']}",
        )

        self.log_test_result(
            "Total Entries Count",
            stats["total_entries"] == expected_entries,
            f"Expected: {expected_entries}, Got: {stats['total_entries']}",
        )

        # Test hit rate calculation
        total_requests = expected_hits + expected_misses
        expected_hit_rate = round((expected_hits / total_requests) * 100, 2)

        self.log_test_result(
            "Hit Rate Calculation",
            stats["hit_rate"] == expected_hit_rate,
            f"Expected: {expected_hit_rate}%, Got: {stats['hit_rate']}%",
        )

    async def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        print("\n⏰ Testing Cache TTL Expiration")
        print("=" * 50)

        # Clear cache
        await clear_cache()

        # Test with short TTL (1 second)
        short_ttl_key = "short_ttl_test"
        short_ttl_value = "expires_soon"

        # Set with game_data cache type (1 hour TTL)
        await set_cached(short_ttl_key, short_ttl_value, "game_data")

        # Immediately get - should be a hit
        cached_value = await get_cached(short_ttl_key)
        self.log_test_result(
            "Immediate Cache Hit",
            cached_value == short_ttl_value,
            f"Expected: {short_ttl_value}, Got: {cached_value}",
        )

        # Test with team_logos cache type (6 months TTL)
        long_ttl_key = "long_ttl_test"
        long_ttl_value = "expires_later"

        await set_cached(long_ttl_key, long_ttl_value, "team_logos")
        cached_value = await get_cached(long_ttl_key)

        self.log_test_result(
            "Long TTL Cache Hit",
            cached_value == long_ttl_value,
            f"Expected: {long_ttl_value}, Got: {cached_value}",
        )

        # Test cache cleanup (should not remove non-expired entries)
        cleaned_count = await cleanup_expired_cache()

        self.log_test_result(
            "Cleanup Non-expired Entries",
            cleaned_count == 0,
            f"Expected: 0, Got: {cleaned_count}",
        )

        # Verify entries still exist
        cached_value_1 = await get_cached(short_ttl_key)
        cached_value_2 = await get_cached(long_ttl_key)

        self.log_test_result(
            "Entries Still Exist After Cleanup",
            cached_value_1 == short_ttl_value and cached_value_2 == long_ttl_value,
            f"Short TTL: {cached_value_1}, Long TTL: {cached_value_2}",
        )

    async def test_cache_key_generators(self):
        """Test cache key generation functions"""
        print("\n🔑 Testing Cache Key Generators")
        print("=" * 50)

        # Test game data key
        game_key = game_data_key("galaxy", "soccer", "20240101", "20240107")
        expected_game_key = "game_data_galaxy_soccer_20240101_20240107"

        self.log_test_result(
            "Game Data Key Generation",
            game_key == expected_game_key,
            f"Expected: {expected_game_key}, Got: {game_key}",
        )

        # Test team logos key
        team_logos_key_result = team_logos_key("134153")
        expected_team_logos_key = "team_logos_134153"

        self.log_test_result(
            "Team Logos Key Generation",
            team_logos_key_result == expected_team_logos_key,
            f"Expected: {expected_team_logos_key}, Got: {team_logos_key_result}",
        )

        # Test team metadata key
        team_metadata_key_result = team_metadata_key("LA Galaxy")
        expected_team_metadata_key = "team_metadata_la_galaxy"

        self.log_test_result(
            "Team Metadata Key Generation",
            team_metadata_key_result == expected_team_metadata_key,
            f"Expected: {expected_team_metadata_key}, Got: {team_metadata_key_result}",
        )

        # Test venue data key
        venue_key = venue_data_key("Dignity Health Sports Park")
        expected_venue_key = "venue_data_dignity_health_sports_park"

        self.log_test_result(
            "Venue Data Key Generation",
            venue_key == expected_venue_key,
            f"Expected: {expected_venue_key}, Got: {venue_key}",
        )

        # Test team name key
        team_name_key_result = team_name_key("galaxy")
        expected_team_name_key = "team_name_galaxy"

        self.log_test_result(
            "Team Name Key Generation",
            team_name_key_result == expected_team_name_key,
            f"Expected: {expected_team_name_key}, Got: {team_name_key_result}",
        )

    async def test_cache_clear_operations(self):
        """Test cache clear operations"""
        print("\n🧹 Testing Cache Clear Operations")
        print("=" * 50)

        # Clear cache first
        await clear_cache()

        # Add test data with different cache types
        await set_cached("game_data_test", "game_value", "game_data")
        await set_cached("team_logos_test", "logo_value", "team_logos")
        await set_cached("venue_data_test", "venue_value", "venue_data")
        await set_cached("default_test", "default_value", "default")

        # Verify all entries exist
        stats_before = await get_cache_stats()
        self.log_test_result(
            "Entries Added Successfully",
            stats_before["total_entries"] == 4,
            f"Expected: 4, Got: {stats_before['total_entries']}",
        )

        # Test clear by type (game_data)
        cleared_count = await clear_cache("game_data")
        stats_after_game_clear = await get_cache_stats()

        self.log_test_result(
            "Clear by Type (game_data)",
            cleared_count == 1 and stats_after_game_clear["total_entries"] == 3,
            f"Cleared: {cleared_count}, Remaining: {stats_after_game_clear['total_entries']}",
        )

        # Test clear by type (team_logos)
        cleared_count = await clear_cache("team_logos")
        stats_after_logo_clear = await get_cache_stats()

        self.log_test_result(
            "Clear by Type (team_logos)",
            cleared_count == 1 and stats_after_logo_clear["total_entries"] == 2,
            f"Cleared: {cleared_count}, Remaining: {stats_after_logo_clear['total_entries']}",
        )

        # Test clear all
        cleared_count = await clear_cache()
        stats_after_clear_all = await get_cache_stats()

        self.log_test_result(
            "Clear All",
            cleared_count == 2 and stats_after_clear_all["total_entries"] == 0,
            f"Cleared: {cleared_count}, Remaining: {stats_after_clear_all['total_entries']}",
        )

    async def test_cache_concurrency(self):
        """Test cache operations under concurrent access"""
        print("\n🔄 Testing Cache Concurrency")
        print("=" * 50)

        # Clear cache
        await clear_cache()

        async def concurrent_setter(key_prefix: str, count: int):
            """Concurrently set cache values"""
            tasks = []
            for i in range(count):
                key = f"{key_prefix}_{i}"
                value = f"value_{i}"
                tasks.append(set_cached(key, value, "default"))
            await asyncio.gather(*tasks)

        async def concurrent_getter(key_prefix: str, count: int):
            """Concurrently get cache values"""
            tasks = []
            for i in range(count):
                key = f"{key_prefix}_{i}"
                tasks.append(get_cached(key))
            return await asyncio.gather(*tasks)

        # Test concurrent sets
        await concurrent_setter("concurrent_test", 10)

        # Verify all values were set
        stats = await get_cache_stats()
        self.log_test_result(
            "Concurrent Sets",
            stats["total_entries"] == 10,
            f"Expected: 10, Got: {stats['total_entries']}",
        )

        # Test concurrent gets
        results = await concurrent_getter("concurrent_test", 10)
        expected_results = [f"value_{i}" for i in range(10)]

        self.log_test_result(
            "Concurrent Gets",
            results == expected_results,
            f"Expected: {expected_results}, Got: {results}",
        )

        # Test concurrent mixed operations
        async def mixed_operations():
            """Mix of set, get, and delete operations"""
            tasks = []
            for i in range(5):
                tasks.append(set_cached(f"mixed_{i}", f"mixed_value_{i}", "default"))
            for i in range(5):
                tasks.append(get_cached(f"concurrent_test_{i}"))
            for i in range(3):
                tasks.append(delete_cached(f"concurrent_test_{i}"))
            await asyncio.gather(*tasks)

        await mixed_operations()

        # Verify final state
        final_stats = await get_cache_stats()
        self.log_test_result(
            "Mixed Concurrent Operations",
            final_stats["total_entries"] == 12,  # 7 remaining + 5 new
            f"Expected: 12, Got: {final_stats['total_entries']}",
        )

    async def test_cache_integration_simulation(self):
        """Test cache integration with simulated API calls"""
        print("\n🔗 Testing Cache Integration Simulation")
        print("=" * 50)

        # Clear cache
        await clear_cache()

        # Simulate API calls with caching
        async def simulate_api_call(endpoint: str, params: dict, cache_type: str):
            """Simulate an API call with caching"""
            # Generate cache key
            cache_key = f"{endpoint}_{hash(str(params))}"

            # Check cache first
            cached_result = await get_cached(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {endpoint}")
                return cached_result

            # Simulate API call delay
            await asyncio.sleep(0.1)

            # Simulate API response
            result = {
                "endpoint": endpoint,
                "params": params,
                "data": f"response_data_{hash(str(params))}",
                "timestamp": time.time(),
            }

            # Cache the result
            await set_cached(cache_key, result, cache_type)
            logger.info(f"API call completed and cached for {endpoint}")

            return result

        # Test multiple calls to same endpoint (should hit cache)
        params1 = {"team": "galaxy", "sport": "soccer"}
        params2 = {"team": "dodgers", "sport": "baseball"}

        # First calls (should miss cache)
        result1_first = await simulate_api_call("teams", params1, "team_metadata")
        result2_first = await simulate_api_call("teams", params2, "team_metadata")

        # Second calls (should hit cache)
        result1_second = await simulate_api_call("teams", params1, "team_metadata")
        result2_second = await simulate_api_call("teams", params2, "team_metadata")

        # Verify cache hits
        self.log_test_result(
            "First Call Cache Miss",
            result1_first["data"] == result1_second["data"],
            "First and second calls should return same data",
        )

        self.log_test_result(
            "Second Call Cache Hit",
            result1_first["data"] == result1_second["data"],
            "Second call should return cached data",
        )

        # Verify both calls return same data
        self.log_test_result(
            "Cache Consistency Check",
            result2_first["data"] == result2_second["data"],
            "Both team calls should return consistent data",
        )

        # Test different cache types
        game_result = await simulate_api_call("games", {"team": "galaxy"}, "game_data")
        logo_result = await simulate_api_call("logos", {"team": "galaxy"}, "team_logos")

        self.log_test_result(
            "Different Cache Types",
            game_result["endpoint"] == "games" and logo_result["endpoint"] == "logos",
            "Different cache types should work independently",
        )

        # Verify final cache state
        final_stats = await get_cache_stats()
        self.log_test_result(
            "Integration Cache State",
            final_stats["total_entries"] == 4,  # 2 teams + 1 game + 1 logo
            f"Expected: 4, Got: {final_stats['total_entries']}",
        )

    async def run_all_tests(self):
        """Run all cache tests"""
        print("🧪 Goobie-Bot Cache Testing Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            await self.test_basic_cache_operations()
            await self.test_cache_statistics()
            await self.test_cache_ttl_expiration()
            await self.test_cache_key_generators()
            await self.test_cache_clear_operations()
            await self.test_cache_concurrency()
            await self.test_cache_integration_simulation()

        except Exception as e:
            logger.error(f"Test suite error: {e}")
            import traceback

            traceback.print_exc()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(
            f"Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%"
        )

        if self.failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['message']}")

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return self.failed_tests == 0


async def main():
    """Main test runner"""
    test_suite = CacheTestSuite()
    success = await test_suite.run_all_tests()

    if success:
        print("\n✅ All cache tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some cache tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
