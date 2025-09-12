"""
Cache module for goobie-bot
Provides TTL-based caching with statistics and management
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Cache duration constants (in seconds)
# Pi-optimized durations (shorter for memory efficiency)
CACHE_DURATIONS = {
    "game_data": 1800,  # 30 minutes (reduced from 1 hour for Pi)
    "team_logos": 86400,  # 1 day (reduced from 6 months for Pi)
    "venue_data": 86400,  # 1 day (reduced from 6 months for Pi)
    "team_metadata": 7200,  # 2 hours (reduced from 12 hours for Pi)
    "team_names": 86400,  # 1 day (reduced from 6 months for Pi)
}

# Pi-specific cache limits (can be overridden by environment variables)
DEFAULT_CACHE_SIZE_LIMIT = 100
DEFAULT_MEMORY_LIMIT_MB = 512

# Cache statistics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "deletes": 0,
    "clears": 0,
}

# Cache storage
_cache = {}
_cache_lock = asyncio.Lock()


class CacheEntry:
    """Represents a cache entry with TTL and metadata"""

    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.expires_at = self.created_at + ttl if ttl else None
        self.access_count = 0
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def access(self) -> Any:
        """Access the cache entry and update metadata"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value

    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary for statistics"""
        return {
            "value": self.value,
            "created_at": self.created_at,
            "ttl": self.ttl,
            "expires_at": self.expires_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "is_expired": self.is_expired(),
        }


class CacheManager:
    """Centralized cache manager with TTL support and statistics"""

    def __init__(self, max_entries: int = None, memory_limit_mb: int = None):
        self._cache = {}
        self._max_entries = max_entries or DEFAULT_CACHE_SIZE_LIMIT
        self._memory_limit_bytes = (
            (memory_limit_mb or DEFAULT_MEMORY_LIMIT_MB) * 1024 * 1024
        )
        self._current_memory_bytes = 0
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "clears": 0,
            "evictions": 0,
            "memory_warnings": 0,
        }
        self._lock = asyncio.Lock()
        logger.info("Cache manager initialized with TTL durations:")
        for cache_type, duration in CACHE_DURATIONS.items():
            if duration:
                hours = duration // 3600
                days = hours // 24
                if days > 0:
                    logger.info(f"  - {cache_type}: {days} days ({duration}s)")
                else:
                    logger.info(f"  - {cache_type}: {hours} hours ({duration}s)")
            else:
                logger.info(f"  - {cache_type}: No TTL (permanent)")

        logger.info(
            f"Cache limits - Max entries: {self._max_entries}, Memory limit: {self._memory_limit_bytes // 1024 // 1024}MB"
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        async with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                logger.debug(f"Cache miss for key: {key}")
                return None

            entry = self._cache[key]

            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._stats["misses"] += 1
                logger.info(f"Cache expired and removed for key: {key}")
                return None

            # Update access statistics
            value = entry.access()
            self._stats["hits"] += 1
            logger.info(
                f"Cache hit for key: {key} (access count: {entry.access_count})"
            )
            return value

    async def set(self, key: str, value: Any, cache_type: str = "default") -> None:
        """Set a value in cache with TTL based on cache type"""
        ttl = CACHE_DURATIONS.get(cache_type)
        entry = CacheEntry(value, ttl)

        async with self._lock:
            self._cache[key] = entry
            self._stats["sets"] += 1
            logger.info(f"Cache set for key: {key} (type: {cache_type}, TTL: {ttl}s)")

    async def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                logger.info(f"Cache deleted for key: {key}")
                return True
            logger.debug(f"Cache delete attempted for non-existent key: {key}")
            return False

    async def clear(self, cache_type: Optional[str] = None) -> int:
        """Clear cache entries, optionally by type"""
        async with self._lock:
            if cache_type is None:
                # Clear all cache
                count = len(self._cache)
                self._cache.clear()
                self._stats["clears"] += 1
                logger.info(f"Cleared all cache entries: {count}")
                return count
            else:
                # Clear by type (keys starting with cache_type)
                keys_to_delete = [
                    k for k in self._cache.keys() if k.startswith(f"{cache_type}_")
                ]
                for key in keys_to_delete:
                    del self._cache[key]
                self._stats["clears"] += 1
                logger.info(
                    f"Cleared {len(keys_to_delete)} entries for type: {cache_type}"
                )
                if keys_to_delete:
                    logger.debug(f"Cleared keys: {keys_to_delete}")
                return len(keys_to_delete)

    async def cleanup_expired(self) -> int:
        """Remove expired entries from cache"""
        async with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                logger.debug(f"Expired keys: {expired_keys}")
            else:
                logger.debug("No expired cache entries found during cleanup")

            return len(expired_keys)

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                (self._stats["hits"] / total_requests * 100)
                if total_requests > 0
                else 0
            )

            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "clears": self._stats["clears"],
                "hit_rate": round(hit_rate, 2),
                "total_entries": len(self._cache),
                "total_requests": total_requests,
            }

    async def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        async with self._lock:
            cache_info = {}
            for key, entry in self._cache.items():
                cache_info[key] = entry.to_dict()

            return cache_info

    async def warm_static_data(self) -> None:
        """Pre-populate cache with static data that rarely changes"""
        logger.info("Warming cache with static data...")

        # This will be called during bot startup
        # We'll implement specific warming logic later
        logger.info("Cache warming completed")


# Global cache manager instance
cache_manager = CacheManager()


def cache_result(cache_type: str, key_func: Optional[callable] = None):
    """
    Decorator for caching function results

    Args:
        cache_type: Type of cache (determines TTL)
        key_func: Optional function to generate cache key from args
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                if args:
                    key_parts.extend(str(arg) for arg in args)
                if kwargs:
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = "_".join(key_parts)

            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_manager.set(cache_key, result, cache_type)

            return result

        return wrapper

    return decorator


# Convenience functions for common cache operations
async def get_cached(key: str) -> Optional[Any]:
    """Get a value from cache"""
    logger.debug(f"Getting cached value for key: {key}")
    return await cache_manager.get(key)


async def set_cached(key: str, value: Any, cache_type: str = "default") -> None:
    """Set a value in cache"""
    logger.debug(f"Setting cached value for key: {key} (type: {cache_type})")
    await cache_manager.set(key, value, cache_type)


async def delete_cached(key: str) -> bool:
    """Delete a value from cache"""
    logger.debug(f"Deleting cached value for key: {key}")
    return await cache_manager.delete(key)


async def clear_cache(cache_type: Optional[str] = None) -> int:
    """Clear cache entries"""
    if cache_type:
        logger.info(f"Clearing cache entries for type: {cache_type}")
    else:
        logger.info("Clearing all cache entries")
    return await cache_manager.clear(cache_type)


async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    logger.debug("Retrieving cache statistics")
    return await cache_manager.get_stats()


async def cleanup_expired_cache() -> int:
    """Clean up expired cache entries"""
    logger.debug("Cleaning up expired cache entries")
    return await cache_manager.cleanup_expired()


# Cache key generators for common patterns
def game_data_key(team: str, sport: str, start_date: str, end_date: str) -> str:
    """Generate cache key for game data"""
    key = f"game_data_{team}_{sport}_{start_date}_{end_date}"
    logger.debug(f"Generated game data cache key: {key}")
    return key


def team_logos_key(team_id: str) -> str:
    """Generate cache key for team logos"""
    key = f"team_logos_{team_id}"
    logger.debug(f"Generated team logos cache key: {key}")
    return key


def team_logos_by_name_key(team_name: str) -> str:
    """Generate cache key for team logos by name"""
    key = f"team_logos_name_{team_name.lower().replace(' ', '_')}"
    logger.debug(f"Generated team logos by name cache key: {key}")
    return key


def venue_data_key(venue_name: str) -> str:
    """Generate cache key for venue data"""
    key = f"venue_data_{venue_name.lower().replace(' ', '_')}"
    logger.debug(f"Generated venue data cache key: {key}")
    return key


def team_metadata_key(team_name: str) -> str:
    """Generate cache key for team metadata"""
    key = f"team_metadata_{team_name.lower().replace(' ', '_')}"
    logger.debug(f"Generated team metadata cache key: {key}")
    return key


def team_name_key(team_ref: str) -> str:
    """Generate cache key for team name"""
    key = f"team_name_{team_ref}"
    logger.debug(f"Generated team name cache key: {key}")
    return key


# Background task for cache cleanup
async def cache_cleanup_task():
    """Background task to clean up expired cache entries"""
    logger.info("Starting cache cleanup background task (runs every 5 minutes)")
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            logger.debug("Running scheduled cache cleanup...")
            cleaned_count = await cleanup_expired_cache()
            if cleaned_count > 0:
                logger.info(
                    f"Scheduled cleanup removed {cleaned_count} expired entries"
                )
        except Exception as e:
            logger.error(f"Error in cache cleanup task: {e}")
            # Continue running even if there's an error
            await asyncio.sleep(60)  # Wait 1 minute before retrying


# Export main functions
__all__ = [
    "cache_manager",
    "cache_result",
    "get_cached",
    "set_cached",
    "delete_cached",
    "clear_cache",
    "get_cache_stats",
    "cleanup_expired_cache",
    "game_data_key",
    "team_logos_key",
    "team_logos_by_name_key",
    "venue_data_key",
    "team_metadata_key",
    "team_name_key",
    "cache_cleanup_task",
]
