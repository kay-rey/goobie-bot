#!/usr/bin/env python3
"""
Logo downloader script for goobie-bot
Downloads all team logos and stores them locally in the container
"""

import asyncio
import aiohttp
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Define all team logos we need
TEAM_LOGOS = {
    "galaxy": {
        "team_name": "LA Galaxy",
        "team_id": "134153",
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png",
        "logo_small": "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png",
        "jersey": "https://www.thesportsdb.com/images/media/team/equipment/ysyysr1420227188.png",
    },
    "dodgers": {
        "team_name": "Los Angeles Dodgers",
        "team_id": "135272",
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/p2oj631663889783.png",
        "logo_small": "https://r2.thesportsdb.com/images/media/team/badge/p2oj631663889783.png/small",
        "jersey": "https://r2.thesportsdb.com/images/media/team/equipment/l8j10w1725717341.png",
    },
    "lakers": {
        "team_name": "Los Angeles Lakers",
        "team_id": "134867",
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/d8uoxw1714254511.png",
        "logo_small": "https://r2.thesportsdb.com/images/media/team/badge/d8uoxw1714254511.png/small",
        "jersey": "https://r2.thesportsdb.com/images/media/team/equipment/xc022l1507047766.png",
    },
    "rams": {
        "team_name": "Los Angeles Rams",
        "team_id": "135907",
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/8e8v4i1599764614.png",
        "logo_small": "https://r2.thesportsdb.com/images/media/team/badge/8e8v4i1599764614.png/small",
        "jersey": "https://r2.thesportsdb.com/images/media/team/equipment/4nh10c1510252994.png",
    },
    "kings": {
        "team_name": "Los Angeles Kings",
        "team_id": "134852",
        "logo": "https://r2.thesportsdb.com/images/media/team/badge/w408rg1719220748.png",
        "logo_small": "https://r2.thesportsdb.com/images/media/team/badge/w408rg1719220748.png/small",
        "jersey": "https://r2.thesportsdb.com/images/media/team/equipment/2019-134852-Jersey.png",
    },
}


async def download_image(session, url, filepath):
    """Download an image from URL and save to filepath"""
    try:
        if not url or url == "":
            logger.warning(f"Empty URL provided, skipping download")
            return False

        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                # Ensure directory exists
                filepath.parent.mkdir(parents=True, exist_ok=True)
                # Write file
                with open(filepath, "wb") as f:
                    f.write(content)
                logger.info(f"Downloaded: {url} -> {filepath}")
                return True
            else:
                logger.warning(f"Failed to download {url}: HTTP {response.status}")
                return False
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False


async def download_team_logos():
    """Download all team logos"""
    assets_dir = Path("/app/assets/logos")
    assets_dir.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        # Download main team logos
        for team_key, team_data in TEAM_LOGOS.items():
            logger.info(f"Downloading logos for {team_data['team_name']}")
            team_dir = assets_dir / team_key
            team_dir.mkdir(parents=True, exist_ok=True)

            # Download each logo type
            logo_types = [
                "logo",
                "logo_small",
                "jersey",
            ]
            for logo_type in logo_types:
                if logo_type in team_data and team_data[logo_type]:
                    url = team_data[logo_type]
                    filename = f"{logo_type}.png"
                    filepath = team_dir / filename
                    await download_image(session, url, filepath)


def create_logo_manifest():
    """Create a manifest file with all logo mappings"""
    manifest = {
        "teams": TEAM_LOGOS,
        "version": "1.0.0",
        "generated_at": "2024-01-01T00:00:00Z",
    }

    import json

    manifest_path = Path("/app/assets/logos/manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    logger.info("Created logo manifest: %s", manifest_path)


async def main():
    """Main function"""
    logger.info("Starting logo download process...")

    # Download all logos
    await download_team_logos()

    # Create manifest
    create_logo_manifest()

    logger.info("Logo download process completed!")


if __name__ == "__main__":
    asyncio.run(main())
