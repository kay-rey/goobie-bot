#!/usr/bin/env python3
"""
Cache Performance Testing Script for goobie-bot

This script tests cache performance and provides real-world usage scenarios.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.cache import (
    get_cached,
    set_cached,
    clear_cache,
    get_cache_stats,
    team_metadata_key,
    team_logos_key,
    game_data_key,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def test_cache_performance():
    """Test cache performance with realistic scenarios"""
    print("🚀 Cache Performance Test")
    print("=" * 50)

    # Clear cache first
    await clear_cache()

    # Test 1: Simulate repeated team data requests
    print("\n📊 Test 1: Team Data Caching")
    print("-" * 30)

    team_requests = [
        ("galaxy", "LA Galaxy"),
        ("dodgers", "Los Angeles Dodgers"),
        ("lakers", "Los Angeles Lakers"),
        ("rams", "Los Angeles Rams"),
        ("kings", "Los Angeles Kings"),
    ]

    # First round - should all be cache misses
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
            else "basketball"
            if team_ref == "lakers"
            else "football"
            if team_ref == "rams"
            else "hockey",
            "logo": f"https://example.com/{team_ref}_logo.png",
        }
        await set_cached(cache_key, team_data, "team_metadata")

    first_round_time = time.time() - start_time
    print(f"First round (cache misses): {first_round_time:.3f}s")

    # Second round - should all be cache hits
    start_time = time.time()
    for team_ref, team_name in team_requests:
        cache_key = team_metadata_key(team_ref)
        cached_data = await get_cached(cache_key)
        if not cached_data:
            print(f"❌ Cache miss for {team_ref}!")

    second_round_time = time.time() - start_time
    print(f"Second round (cache hits): {second_round_time:.3f}s")

    speedup = (
        first_round_time / second_round_time if second_round_time > 0 else float("inf")
    )
    print(f"Speedup: {speedup:.1f}x faster")

    # Test 2: Simulate game data requests with different time ranges
    print("\n🎮 Test 2: Game Data Caching")
    print("-" * 30)

    game_requests = [
        ("galaxy", "soccer", "20240101", "20240107"),
        ("dodgers", "baseball", "20240101", "20240107"),
        ("lakers", "basketball", "20240101", "20240107"),
        ("galaxy", "soccer", "20240108", "20240114"),  # Different week
        ("dodgers", "baseball", "20240108", "20240114"),  # Different week
    ]

    # First round - cache misses
    start_time = time.time()
    for team, sport, start_date, end_date in game_requests:
        cache_key = game_data_key(team, sport, start_date, end_date)
        # Simulate API call delay
        await asyncio.sleep(0.1)
        # Simulate game data
        game_data = {
            "team": team,
            "sport": sport,
            "start_date": start_date,
            "end_date": end_date,
            "games": [f"game_{i}" for i in range(3)],  # Simulate 3 games per week
        }
        await set_cached(cache_key, game_data, "game_data")

    first_round_time = time.time() - start_time
    print(f"First round (cache misses): {first_round_time:.3f}s")

    # Second round - cache hits
    start_time = time.time()
    for team, sport, start_date, end_date in game_requests:
        cache_key = game_data_key(team, sport, start_date, end_date)
        cached_data = await get_cached(cache_key)
        if not cached_data:
            print(f"❌ Cache miss for {team} {sport}!")

    second_round_time = time.time() - start_time
    print(f"Second round (cache hits): {second_round_time:.3f}s")

    speedup = (
        first_round_time / second_round_time if second_round_time > 0 else float("inf")
    )
    print(f"Speedup: {speedup:.1f}x faster")

    # Test 3: Simulate logo requests (long TTL)
    print("\n🖼️ Test 3: Logo Data Caching")
    print("-" * 30)

    logo_requests = [
        ("134153", "LA Galaxy"),
        ("1416", "Los Angeles Dodgers"),
        ("134154", "Los Angeles Lakers"),
        ("135907", "Los Angeles Rams"),
        ("134852", "Los Angeles Kings"),
    ]

    # First round - cache misses
    start_time = time.time()
    for team_id, team_name in logo_requests:
        cache_key = team_logos_key(team_id)
        # Simulate API call delay
        await asyncio.sleep(0.08)
        # Simulate logo data
        logo_data = {
            "team_id": team_id,
            "team_name": team_name,
            "logo": f"https://example.com/{team_id}_logo.png",
            "logo_small": f"https://example.com/{team_id}_logo_small.png",
            "jersey": f"https://example.com/{team_id}_jersey.png",
            "stadium": f"{team_name} Stadium",
            "stadium_thumb": f"https://example.com/{team_id}_stadium.png",
        }
        await set_cached(cache_key, logo_data, "team_logos")

    first_round_time = time.time() - start_time
    print(f"First round (cache misses): {first_round_time:.3f}s")

    # Second round - cache hits
    start_time = time.time()
    for team_id, team_name in logo_requests:
        cache_key = team_logos_key(team_id)
        cached_data = await get_cached(cache_key)
        if not cached_data:
            print(f"❌ Cache miss for {team_name}!")

    second_round_time = time.time() - start_time
    print(f"Second round (cache hits): {second_round_time:.3f}s")

    speedup = (
        first_round_time / second_round_time if second_round_time > 0 else float("inf")
    )
    print(f"Speedup: {speedup:.1f}x faster")

    # Test 4: Mixed workload simulation
    print("\n🔄 Test 4: Mixed Workload Simulation")
    print("-" * 30)

    # Simulate realistic bot usage pattern
    async def simulate_bot_usage():
        """Simulate realistic bot usage patterns"""
        tasks = []

        # Multiple users requesting same team data
        for i in range(5):
            tasks.append(get_cached(team_metadata_key("galaxy")))
            tasks.append(get_cached(team_logos_key("134153")))

        # Different users requesting different teams
        for team_ref in ["dodgers", "lakers", "rams", "kings"]:
            tasks.append(get_cached(team_metadata_key(team_ref)))

        # Game data requests
        for team in ["galaxy", "dodgers", "lakers"]:
            tasks.append(
                get_cached(
                    game_data_key(
                        team,
                        "soccer"
                        if team == "galaxy"
                        else "baseball"
                        if team == "dodgers"
                        else "basketball",
                        "20240101",
                        "20240107",
                    )
                )
            )

        await asyncio.gather(*tasks)

    start_time = time.time()
    await simulate_bot_usage()
    mixed_workload_time = time.time() - start_time
    print(f"Mixed workload (all cache hits): {mixed_workload_time:.3f}s")

    # Get final statistics
    stats = await get_cache_stats()
    print(f"\n📈 Final Cache Statistics:")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Cache Hits: {stats['hits']}")
    print(f"  Cache Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']}%")
    print(f"  Total Requests: {stats['total_requests']}")

    return stats


async def test_cache_stress():
    """Test cache under stress conditions"""
    print("\n💪 Cache Stress Test")
    print("=" * 50)

    # Clear cache
    await clear_cache()

    # Stress test with many concurrent operations
    async def stress_worker(worker_id: int, operations: int):
        """Worker function for stress testing"""
        for i in range(operations):
            key = f"stress_{worker_id}_{i}"
            value = f"value_{worker_id}_{i}"

            # Set value
            await set_cached(key, value, "default")

            # Get value
            cached_value = await get_cached(key)

            # Verify
            if cached_value != value:
                print(f"❌ Worker {worker_id}: Value mismatch for key {key}")
                return False

        return True

    # Run stress test with multiple workers
    num_workers = 10
    operations_per_worker = 50

    print(
        f"Running stress test with {num_workers} workers, {operations_per_worker} operations each..."
    )

    start_time = time.time()
    tasks = [stress_worker(i, operations_per_worker) for i in range(num_workers)]
    results = await asyncio.gather(*tasks)
    stress_time = time.time() - start_time

    success_count = sum(1 for result in results if result)
    print(f"Stress test completed in {stress_time:.3f}s")
    print(f"Successful workers: {success_count}/{num_workers}")

    # Get final statistics
    stats = await get_cache_stats()
    print(f"Final cache entries: {stats['total_entries']}")
    print(f"Hit rate: {stats['hit_rate']}%")

    return success_count == num_workers


async def main():
    """Main test runner"""
    print("🧪 Goobie-Bot Cache Performance Testing")
    print("=" * 60)

    try:
        # Run performance tests
        stats = await test_cache_performance()

        # Run stress test
        stress_success = await test_cache_stress()

        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        print(f"Hit Rate: {stats['hit_rate']}%")
        print(f"Total Entries: {stats['total_entries']}")
        print(f"Stress Test: {'✅ PASSED' if stress_success else '❌ FAILED'}")

        if stats["hit_rate"] >= 70:
            print("🎉 Excellent cache performance!")
        elif stats["hit_rate"] >= 40:
            print("👍 Good cache performance")
        else:
            print("⚠️ Cache performance needs improvement")

    except Exception as e:
        logger.error(f"Performance test error: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
