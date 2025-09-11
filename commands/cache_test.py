"""
Cache testing command for goobie-bot
Allows testing cache functionality directly from Discord
"""

import discord
from discord import app_commands
import logging
import asyncio
import time
from api.cache import (
    get_cached,
    set_cached,
    clear_cache,
    get_cache_stats,
    team_metadata_key,
    team_logos_key,
    game_data_key,
)

logger = logging.getLogger(__name__)


@app_commands.command(name="cachetest", description="Test cache functionality")
@app_commands.choices(
    test_type=[
        app_commands.Choice(name="basic", value="basic"),
        app_commands.Choice(name="performance", value="performance"),
        app_commands.Choice(name="stress", value="stress"),
        app_commands.Choice(name="integration", value="integration"),
    ]
)
async def cache_test_command(
    interaction: discord.Interaction, test_type: app_commands.Choice[str]
):
    """Test cache functionality"""
    logger.info(
        f"Cache test command triggered by {interaction.user} for test: {test_type.value}"
    )
    await interaction.response.defer(ephemeral=True)

    try:
        if test_type.value == "basic":
            await run_basic_cache_test(interaction)
        elif test_type.value == "performance":
            await run_performance_cache_test(interaction)
        elif test_type.value == "stress":
            await run_stress_cache_test(interaction)
        elif test_type.value == "integration":
            await run_integration_cache_test(interaction)
        else:
            await interaction.followup.send("❌ Unknown test type", ephemeral=True)

    except Exception as e:
        logger.error(f"Error in cache test command: {e}")
        import traceback

        traceback.print_exc()
        await interaction.followup.send(
            "❌ An error occurred during cache testing", ephemeral=True
        )


async def run_basic_cache_test(interaction: discord.Interaction):
    """Run basic cache functionality tests"""
    embed = discord.Embed(
        title="🧪 Basic Cache Test",
        color=0x00BFFF,
        timestamp=discord.utils.utcnow(),
    )

    # Clear cache first
    await clear_cache()

    # Test 1: Set and get
    test_key = "test_basic_1"
    test_value = {"data": "test", "number": 42}

    await set_cached(test_key, test_value, "default")
    cached_value = await get_cached(test_key)

    set_get_success = cached_value == test_value
    embed.add_field(
        name="✅ Set/Get Test",
        value=f"**Status:** {'PASS' if set_get_success else 'FAIL'}\n"
        f"**Expected:** {test_value}\n"
        f"**Got:** {cached_value}",
        inline=False,
    )

    # Test 2: Cache miss
    non_existent_key = "non_existent_key"
    cached_value = await get_cached(non_existent_key)

    miss_success = cached_value is None
    embed.add_field(
        name="✅ Cache Miss Test",
        value=f"**Status:** {'PASS' if miss_success else 'FAIL'}\n"
        f"**Expected:** None\n"
        f"**Got:** {cached_value}",
        inline=False,
    )

    # Test 3: Statistics
    stats = await get_cache_stats()
    embed.add_field(
        name="📊 Cache Statistics",
        value=f"**Hits:** {stats['hits']}\n"
        f"**Misses:** {stats['misses']}\n"
        f"**Hit Rate:** {stats['hit_rate']}%\n"
        f"**Total Entries:** {stats['total_entries']}",
        inline=False,
    )

    # Overall result
    overall_success = set_get_success and miss_success
    embed.color = 0x00FF00 if overall_success else 0xFF0000
    embed.set_footer(text="Basic cache test completed")

    await interaction.followup.send(embed=embed, ephemeral=True)


async def run_performance_cache_test(interaction: discord.Interaction):
    """Run cache performance tests"""
    embed = discord.Embed(
        title="🚀 Cache Performance Test",
        color=0x00BFFF,
        timestamp=discord.utils.utcnow(),
    )

    # Clear cache first
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

    # Second round - cache hits
    start_time = time.time()
    for team_ref, team_name in team_requests:
        cache_key = team_metadata_key(team_ref)
        cached_data = await get_cached(cache_key)

    second_round_time = time.time() - start_time

    speedup = (
        first_round_time / second_round_time if second_round_time > 0 else float("inf")
    )

    embed.add_field(
        name="⏱️ Performance Results",
        value=f"**First Round (Misses):** {first_round_time:.3f}s\n"
        f"**Second Round (Hits):** {second_round_time:.3f}s\n"
        f"**Speedup:** {speedup:.1f}x faster",
        inline=False,
    )

    # Test game data caching
    game_requests = [
        ("galaxy", "soccer", "20240101", "20240107"),
        ("dodgers", "baseball", "20240101", "20240107"),
    ]

    # First round - cache misses
    start_time = time.time()
    for team, sport, start_date, end_date in game_requests:
        cache_key = game_data_key(team, sport, start_date, end_date)
        await asyncio.sleep(0.1)
        game_data = {
            "team": team,
            "sport": sport,
            "start_date": start_date,
            "end_date": end_date,
            "games": [f"game_{i}" for i in range(3)],
        }
        await set_cached(cache_key, game_data, "game_data")

    first_round_time = time.time() - start_time

    # Second round - cache hits
    start_time = time.time()
    for team, sport, start_date, end_date in game_requests:
        cache_key = game_data_key(team, sport, start_date, end_date)
        cached_data = await get_cached(cache_key)

    second_round_time = time.time() - start_time

    speedup = (
        first_round_time / second_round_time if second_round_time > 0 else float("inf")
    )

    embed.add_field(
        name="🎮 Game Data Performance",
        value=f"**First Round (Misses):** {first_round_time:.3f}s\n"
        f"**Second Round (Hits):** {second_round_time:.3f}s\n"
        f"**Speedup:** {speedup:.1f}x faster",
        inline=False,
    )

    # Final statistics
    stats = await get_cache_stats()
    embed.add_field(
        name="📊 Final Statistics",
        value=f"**Hit Rate:** {stats['hit_rate']}%\n"
        f"**Total Entries:** {stats['total_entries']}\n"
        f"**Total Requests:** {stats['total_requests']}",
        inline=False,
    )

    # Performance rating
    if stats["hit_rate"] >= 70:
        performance_rating = "🟢 Excellent"
        embed.color = 0x00FF00
    elif stats["hit_rate"] >= 40:
        performance_rating = "🟡 Good"
        embed.color = 0xFFFF00
    else:
        performance_rating = "🔴 Needs Improvement"
        embed.color = 0xFF0000

    embed.add_field(
        name="📈 Performance Rating", value=performance_rating, inline=False
    )

    embed.set_footer(text="Cache performance test completed")
    await interaction.followup.send(embed=embed, ephemeral=True)


async def run_stress_cache_test(interaction: discord.Interaction):
    """Run cache stress tests"""
    embed = discord.Embed(
        title="💪 Cache Stress Test",
        color=0x00BFFF,
        timestamp=discord.utils.utcnow(),
    )

    # Clear cache
    await clear_cache()

    # Stress test with concurrent operations
    async def stress_worker(worker_id: int, operations: int):
        """Worker function for stress testing"""
        success_count = 0
        for i in range(operations):
            key = f"stress_{worker_id}_{i}"
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
                logger.error(f"Stress worker {worker_id} error: {e}")

        return success_count

    # Run stress test
    num_workers = 5
    operations_per_worker = 20

    embed.add_field(
        name="🔧 Test Configuration",
        value=f"**Workers:** {num_workers}\n"
        f"**Operations per Worker:** {operations_per_worker}\n"
        f"**Total Operations:** {num_workers * operations_per_worker}",
        inline=False,
    )

    start_time = time.time()
    tasks = [stress_worker(i, operations_per_worker) for i in range(num_workers)]
    results = await asyncio.gather(*tasks)
    stress_time = time.time() - start_time

    total_operations = num_workers * operations_per_worker
    successful_operations = sum(results)
    success_rate = (successful_operations / total_operations) * 100

    embed.add_field(
        name="📊 Stress Test Results",
        value=f"**Duration:** {stress_time:.3f}s\n"
        f"**Successful Operations:** {successful_operations}/{total_operations}\n"
        f"**Success Rate:** {success_rate:.1f}%\n"
        f"**Operations/sec:** {total_operations / stress_time:.1f}",
        inline=False,
    )

    # Final cache statistics
    stats = await get_cache_stats()
    embed.add_field(
        name="📈 Cache Statistics",
        value=f"**Total Entries:** {stats['total_entries']}\n"
        f"**Hit Rate:** {stats['hit_rate']}%\n"
        f"**Cache Sets:** {stats['sets']}",
        inline=False,
    )

    # Overall result
    if success_rate >= 95:
        stress_rating = "🟢 Excellent"
        embed.color = 0x00FF00
    elif success_rate >= 80:
        stress_rating = "🟡 Good"
        embed.color = 0xFFFF00
    else:
        stress_rating = "🔴 Needs Improvement"
        embed.color = 0xFF0000

    embed.add_field(name="💪 Stress Test Rating", value=stress_rating, inline=False)

    embed.set_footer(text="Cache stress test completed")
    await interaction.followup.send(embed=embed, ephemeral=True)


async def run_integration_cache_test(interaction: discord.Interaction):
    """Run cache integration tests"""
    embed = discord.Embed(
        title="🔗 Cache Integration Test",
        color=0x00BFFF,
        timestamp=discord.utils.utcnow(),
    )

    # Clear cache
    await clear_cache()

    # Simulate realistic API calls with caching
    async def simulate_api_call(endpoint: str, params: dict, cache_type: str):
        """Simulate an API call with caching"""
        cache_key = f"{endpoint}_{hash(str(params))}"

        # Check cache first
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            return cached_result, True  # Return cached result and hit flag

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

        return result, False  # Return fresh result and miss flag

    # Test multiple calls to same endpoint
    params1 = {"team": "galaxy", "sport": "soccer"}
    params2 = {"team": "dodgers", "sport": "baseball"}

    # First calls (should miss cache)
    result1_first, hit1_first = await simulate_api_call(
        "teams", params1, "team_metadata"
    )
    result2_first, hit2_first = await simulate_api_call(
        "teams", params2, "team_metadata"
    )

    # Second calls (should hit cache)
    result1_second, hit1_second = await simulate_api_call(
        "teams", params1, "team_metadata"
    )
    result2_second, hit2_second = await simulate_api_call(
        "teams", params2, "team_metadata"
    )

    embed.add_field(
        name="🔄 API Call Simulation",
        value=f"**First Call 1:** {'HIT' if hit1_first else 'MISS'}\n"
        f"**First Call 2:** {'HIT' if hit2_first else 'MISS'}\n"
        f"**Second Call 1:** {'HIT' if hit1_second else 'MISS'}\n"
        f"**Second Call 2:** {'HIT' if hit2_second else 'MISS'}",
        inline=False,
    )

    # Test different cache types
    game_result, game_hit = await simulate_api_call(
        "games", {"team": "galaxy"}, "game_data"
    )
    logo_result, logo_hit = await simulate_api_call(
        "logos", {"team": "galaxy"}, "team_logos"
    )

    embed.add_field(
        name="🎯 Different Cache Types",
        value=f"**Game Data Call:** {'HIT' if game_hit else 'MISS'}\n"
        f"**Logo Data Call:** {'HIT' if logo_hit else 'MISS'}\n"
        f"**Game Endpoint:** {game_result['endpoint']}\n"
        f"**Logo Endpoint:** {logo_result['endpoint']}",
        inline=False,
    )

    # Verify cache consistency
    consistency_check = (
        result1_first["data"] == result1_second["data"]
        and result2_first["data"] == result2_second["data"]
    )

    embed.add_field(
        name="✅ Cache Consistency",
        value=f"**Status:** {'PASS' if consistency_check else 'FAIL'}\n"
        f"**Data Consistency:** {'Verified' if consistency_check else 'Failed'}",
        inline=False,
    )

    # Final statistics
    stats = await get_cache_stats()
    embed.add_field(
        name="📊 Integration Statistics",
        value=f"**Hit Rate:** {stats['hit_rate']}%\n"
        f"**Total Entries:** {stats['total_entries']}\n"
        f"**Cache Hits:** {stats['hits']}\n"
        f"**Cache Misses:** {stats['misses']}",
        inline=False,
    )

    # Overall result
    overall_success = consistency_check and hit1_second and hit2_second
    embed.color = 0x00FF00 if overall_success else 0xFF0000

    embed.set_footer(text="Cache integration test completed")
    await interaction.followup.send(embed=embed, ephemeral=True)


# Export the command
cache_test_command = cache_test_command
