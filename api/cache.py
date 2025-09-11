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
CACHE_DURATIONS = {
    "game_data": 3600,  # 1 hour
    "team_logos": 15768000,  # 6 months (182.5 days)
    "venue_data": 15768000,  # 6 months
    "team_metadata": 43200,  # 12 hours
    "team_names": 15768000,  # 6 months
}

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

    def __init__(self):
        self._cache = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "clears": 0,
        }
        self._lock = asyncio.Lock()

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
                logger.debug(f"Cache expired for key: {key}")
                return None

            # Update access statistics
            value = entry.access()
            self._stats["hits"] += 1
            logger.debug(f"Cache hit for key: {key}")
            return value

    async def set(self, key: str, value: Any, cache_type: str = "default") -> None:
        """Set a value in cache with TTL based on cache type"""
        ttl = CACHE_DURATIONS.get(cache_type)
        entry = CacheEntry(value, ttl)

        async with self._lock:
            self._cache[key] = entry
            self._stats["sets"] += 1
            logger.debug(f"Cache set for key: {key} (TTL: {ttl}s)")

    async def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                logger.debug(f"Cache deleted for key: {key}")
                return True
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
    return await cache_manager.get(key)


async def set_cached(key: str, value: Any, cache_type: str = "default") -> None:
    """Set a value in cache"""
    await cache_manager.set(key, value, cache_type)


async def delete_cached(key: str) -> bool:
    """Delete a value from cache"""
    return await cache_manager.delete(key)


async def clear_cache(cache_type: Optional[str] = None) -> int:
    """Clear cache entries"""
    return await cache_manager.clear(cache_type)


async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return await cache_manager.get_stats()


async def cleanup_expired_cache() -> int:
    """Clean up expired cache entries"""
    return await cache_manager.cleanup_expired()


# Cache key generators for common patterns
def game_data_key(team: str, sport: str, start_date: str, end_date: str) -> str:
    """Generate cache key for game data"""
    return f"game_data_{team}_{sport}_{start_date}_{end_date}"


def team_logos_key(team_id: str) -> str:
    """Generate cache key for team logos"""
    return f"team_logos_{team_id}"


def team_logos_by_name_key(team_name: str) -> str:
    """Generate cache key for team logos by name"""
    return f"team_logos_name_{team_name.lower().replace(' ', '_')}"


def venue_data_key(venue_name: str) -> str:
    """Generate cache key for venue data"""
    return f"venue_data_{venue_name.lower().replace(' ', '_')}"


def team_metadata_key(team_name: str) -> str:
    """Generate cache key for team metadata"""
    return f"team_metadata_{team_name.lower().replace(' ', '_')}"


def team_name_key(team_ref: str) -> str:
    """Generate cache key for team name"""
    return f"team_name_{team_ref}"


# Background task for cache cleanup
async def cache_cleanup_task():
    """Background task to clean up expired cache entries"""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await cleanup_expired_cache()
        except Exception as e:
            logger.error(f"Error in cache cleanup task: {e}")


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
