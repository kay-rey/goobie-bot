"""
HTTP Client module for goobie-bot
Provides async HTTP functionality using aiohttp
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class HTTPClient:
    """Async HTTP client using aiohttp with connection pooling and proper error handling"""

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with connection pooling"""
        if self._session is None or self._session.closed:
            # Create connector with connection pooling
            self._connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Max connections per host
                ttl_dns_cache=300,  # DNS cache TTL in seconds
                use_dns_cache=True,
            )

            # Create session with timeout and connector
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=timeout,
                headers={
                    "User-Agent": "goobie-bot/1.0 (Discord Bot)",
                    "Accept": "application/json",
                },
            )
            logger.info("Created new aiohttp session with connection pooling")

        return self._session

    async def get(
        self, url: str, params: Dict[str, Any] = None, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make async GET request and return JSON data"""
        try:
            session = await self.get_session()
            logger.debug(f"Making GET request to: {url} with params: {params}")

            async with session.get(url, params=params, **kwargs) as response:
                # Log response status
                logger.debug(f"Response status: {response.status} for {url}")

                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Successfully fetched data from {url}")
                    return data
                elif response.status == 429:
                    logger.warning(f"Rate limited by {url} (429)")
                    return None
                elif response.status == 404:
                    logger.warning(f"Resource not found at {url} (404)")
                    return None
                else:
                    logger.warning(f"Unexpected status {response.status} from {url}")
                    return None

        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error for {url}: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout error for {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return None

    async def head(self, url: str, **kwargs) -> bool:
        """Make async HEAD request to check if resource exists"""
        try:
            session = await self.get_session()
            logger.debug(f"Making HEAD request to: {url}")

            async with session.head(url, **kwargs) as response:
                logger.debug(f"HEAD response status: {response.status} for {url}")
                return response.status == 200

        except Exception as e:
            logger.error(f"HEAD request error for {url}: {e}")
            return False

    async def close(self):
        """Close the HTTP session and connector"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Closed aiohttp session")

        if self._connector and not self._connector.closed:
            await self._connector.close()
            logger.info("Closed aiohttp connector")

    @asynccontextmanager
    async def request_context(self):
        """Context manager for HTTP requests"""
        try:
            yield self
        finally:
            # Don't close here - let the global client manage the session
            pass


# Global HTTP client instance
http_client = HTTPClient()


async def cleanup_http_client():
    """Cleanup function to close HTTP client on bot shutdown"""
    await http_client.close()


# Convenience functions for backward compatibility
async def get_json(
    url: str, params: Dict[str, Any] = None, **kwargs
) -> Optional[Dict[str, Any]]:
    """Convenience function for GET requests returning JSON"""
    return await http_client.get(url, params, **kwargs)


async def check_url_exists(url: str, **kwargs) -> bool:
    """Convenience function to check if URL exists"""
    return await http_client.head(url, **kwargs)
