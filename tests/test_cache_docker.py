#!/usr/bin/env python3
"""
Docker-specific Cache Testing Script for goobie-bot

This script tests cache functionality specifically designed for Docker container environment.
It doesn't require Discord bot initialization and focuses on core cache functionality.
"""

import asyncio
import logging
import sys
import time
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging for Docker environment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def test_docker_cache_basic():
    """Test basic cache functionality in Docker environment"""
    print("🐳 Testing Docker Cache Basic Operations")
    print("=" * 50)

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

        # Test 1: Basic set/get operations
        test_data = {
            "test_key": "test_value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        await set_cached("docker_test_1", test_data, "default")
        cached_result = await get_cached("docker_test_1")

        if cached_result == test_data:
            print("✅ Docker Set/Get: PASSED")
        else:
            print(f"❌ Docker Set/Get: FAILED")
            return False

        # Test 2: Cache miss
        miss_result = await get_cached("non_existent_key")
        if miss_result is None:
            print("✅ Docker Cache Miss: PASSED")
        else:
            print("❌ Docker Cache Miss: FAILED")
            return False

        # Test 3: Statistics
        stats = await get_cache_stats()
        print(
            f"📊 Docker Cache Stats: {stats['hits']} hits, {stats['misses']} misses, {stats['hit_rate']}% hit rate"
        )

        return True

    except Exception as e:
        print(f"❌ Docker cache basic test error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_docker_cache_ttl():
    """Test TTL functionality in Docker environment"""
    print("\n⏰ Testing Docker Cache TTL")
    print("=" * 50)

    try:
        from api.cache import get_cached, set_cached, clear_cache, cleanup_expired_cache

        # Clear cache
        await clear_cache()

        # Test different cache types with different TTLs
        cache_tests = [
            ("game_data_test", "game_data", "Game data with 1 hour TTL"),
            ("team_logos_test", "team_logos", "Team logos with 6 months TTL"),
            ("venue_data_test", "venue_data", "Venue data with 6 months TTL"),
        ]

        for key, cache_type, description in cache_tests:
            test_value = f"test_value_{key}"
            await set_cached(key, test_value, cache_type)

            # Immediately retrieve - should be a hit
            cached_value = await get_cached(key)
            if cached_value == test_value:
                print(f"✅ {description}: PASSED")
            else:
                print(f"❌ {description}: FAILED")
                return False

        # Test cleanup (should not remove non-expired entries)
        cleaned_count = await cleanup_expired_cache()
        if cleaned_count == 0:
            print("✅ TTL Cleanup: PASSED (no expired entries)")
        else:
            print(f"⚠️ TTL Cleanup: {cleaned_count} entries cleaned (unexpected)")

        return True

    except Exception as e:
        print(f"❌ Docker cache TTL test error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_docker_cache_concurrency():
    """Test concurrent cache operations in Docker environment"""
    print("\n🔄 Testing Docker Cache Concurrency")
    print("=" * 50)

    try:
        from api.cache import get_cached, set_cached, clear_cache, get_cache_stats

        # Clear cache
        await clear_cache()

        async def concurrent_worker(worker_id: int, operations: int):
            """Worker function for concurrent testing"""
            success_count = 0
            for i in range(operations):
                key = f"docker_concurrent_{worker_id}_{i}"
                value = f"value_{worker_id}_{i}"

                try:
                    # Set value
                    await set_cached(key, value, "default")

                    # Get value
                    cached_value = await get_cached(key)

                    # Verify
                    if cached_value == value:
                        success_count += 1
                except Exception as e:
                    print(f"❌ Worker {worker_id} error: {e}")

            return success_count

        # Run concurrent operations
        num_workers = 5
        operations_per_worker = 10

        print(
            f"Running {num_workers} workers with {operations_per_worker} operations each..."
        )

        start_time = time.time()
        tasks = [
            concurrent_worker(i, operations_per_worker) for i in range(num_workers)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_operations = num_workers * operations_per_worker
        successful_operations = sum(results)
        success_rate = (successful_operations / total_operations) * 100

        print(f"Concurrent test completed in {end_time - start_time:.3f}s")
        print(
            f"Success rate: {success_rate:.1f}% ({successful_operations}/{total_operations})"
        )

        if success_rate >= 95:
            print("✅ Docker Concurrency: PASSED")
            return True
        else:
            print("❌ Docker Concurrency: FAILED")
            return False

    except Exception as e:
        print(f"❌ Docker cache concurrency test error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_docker_cache_integration():
    """Test cache integration with simulated API calls in Docker environment"""
    print("\n🔗 Testing Docker Cache Integration")
    print("=" * 50)

    try:
        from api.cache import (
            get_cached,
            set_cached,
            clear_cache,
            team_metadata_key,
            game_data_key,
        )

        # Clear cache
        await clear_cache()

        # Simulate realistic API calls
        async def simulate_api_call(endpoint: str, params: dict, cache_type: str):
            """Simulate API call with caching"""
            cache_key = f"{endpoint}_{hash(str(params))}"

            # Check cache first
            cached_result = await get_cached(cache_key)
            if cached_result is not None:
                return cached_result, True  # Hit

            # Simulate API delay
            await asyncio.sleep(0.05)

            # Simulate API response
            result = {
                "endpoint": endpoint,
                "params": params,
                "data": f"response_{hash(str(params))}",
                "timestamp": time.time(),
            }

            # Cache the result
            await set_cached(cache_key, result, cache_type)
            return result, False  # Miss

        # Test team data caching
        team_params = {"team": "galaxy", "sport": "soccer"}

        # First call - should miss
        result1, hit1 = await simulate_api_call("teams", team_params, "team_metadata")

        # Second call - should hit
        result2, hit2 = await simulate_api_call("teams", team_params, "team_metadata")

        if not hit1 and hit2 and result1["data"] == result2["data"]:
            print("✅ Docker API Integration: PASSED")
        else:
            print(
                f"❌ Docker API Integration: FAILED - First: {'HIT' if hit1 else 'MISS'}, Second: {'HIT' if hit2 else 'MISS'}"
            )
            return False

        # Test cache key generators
        team_key = team_metadata_key("LA Galaxy")
        game_key = game_data_key("galaxy", "soccer", "20240101", "20240107")

        if (
            team_key == "team_metadata_la_galaxy"
            and game_key == "game_data_galaxy_soccer_20240101_20240107"
        ):
            print("✅ Docker Key Generators: PASSED")
        else:
            print("❌ Docker Key Generators: FAILED")
            return False

        return True

    except Exception as e:
        print(f"❌ Docker cache integration test error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_docker_environment():
    """Test Docker environment specific features"""
    print("\n🐳 Testing Docker Environment")
    print("=" * 50)

    try:
        # Check if we're running in Docker
        if os.path.exists("/.dockerenv"):
            print("✅ Running inside Docker container")
        else:
            print("⚠️ Not running inside Docker container (test may not be accurate)")

        # Check Python version
        python_version = sys.version_info
        print(
            f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # Check if we can import required modules
        try:
            from api.cache import cache_manager

            print("✅ Cache module imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import cache module: {e}")
            return False

        # Check working directory
        cwd = os.getcwd()
        print(f"✅ Working directory: {cwd}")

        return True

    except Exception as e:
        print(f"❌ Docker environment test error: {e}")
        return False


async def main():
    """Main Docker test runner"""
    print("🐳 Goobie-Bot Docker Cache Testing Suite")
    print("=" * 60)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    tests = [
        ("Docker Environment", test_docker_environment),
        ("Docker Cache Basic", test_docker_cache_basic),
        ("Docker Cache TTL", test_docker_cache_ttl),
        ("Docker Cache Concurrency", test_docker_cache_concurrency),
        ("Docker Cache Integration", test_docker_cache_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"Running {test_name}...")
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED\n")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED\n")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}\n")
            failed += 1

    # Print summary
    print("=" * 60)
    print("📊 DOCKER TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    print(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if failed == 0:
        print("\n🎉 All Docker cache tests passed!")
        print("Cache implementation is working correctly in Docker environment.")
        return True
    else:
        print(f"\n⚠️ {failed} Docker cache test(s) failed!")
        print("Please check the output above for details.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
