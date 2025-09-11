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

# Common opponent teams we might encounter
COMMON_OPPONENTS = {
    "atlanta_falcons": {
        "team_name": "Atlanta Falcons",
        "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/1.png",
    },
    "san_francisco_49ers": {
        "team_name": "San Francisco 49ers",
        "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/25.png",
    },
    "seattle_seahawks": {
        "team_name": "Seattle Seahawks",
        "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/26.png",
    },
    "arizona_cardinals": {
        "team_name": "Arizona Cardinals",
        "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/22.png",
    },
    "golden_state_warriors": {
        "team_name": "Golden State Warriors",
        "logo": "https://a.espncdn.com/i/teamlogos/nba/500/9.png",
    },
    "phoenix_suns": {
        "team_name": "Phoenix Suns",
        "logo": "https://a.espncdn.com/i/teamlogos/nba/500/21.png",
    },
    "sacramento_kings": {
        "team_name": "Sacramento Kings",
        "logo": "https://a.espncdn.com/i/teamlogos/nba/500/23.png",
    },
    "clippers": {
        "team_name": "Los Angeles Clippers",
        "logo": "https://a.espncdn.com/i/teamlogos/nba/500/12.png",
    },
    "san_diego_padres": {
        "team_name": "San Diego Padres",
        "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/25.png",
    },
    "san_francisco_giants": {
        "team_name": "San Francisco Giants",
        "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/26.png",
    },
    "anaheim_ducks": {
        "team_name": "Anaheim Ducks",
        "logo": "https://a.espncdn.com/i/teamlogos/nhl/500/24.png",
    },
    "san_jose_sharks": {
        "team_name": "San Jose Sharks",
        "logo": "https://a.espncdn.com/i/teamlogos/nhl/500/28.png",
    },
    "vegas_golden_knights": {
        "team_name": "Vegas Golden Knights",
        "logo": "https://a.espncdn.com/i/teamlogos/nhl/500/142.png",
    },
    "seattle_sounders": {
        "team_name": "Seattle Sounders FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/977.png",
    },
    "portland_timbers": {
        "team_name": "Portland Timbers",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/978.png",
    },
    "vancouver_whitecaps": {
        "team_name": "Vancouver Whitecaps FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/979.png",
    },
    "real_salt_lake": {
        "team_name": "Real Salt Lake",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/980.png",
    },
    "colorado_rapids": {
        "team_name": "Colorado Rapids",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/981.png",
    },
    "fc_dallas": {
        "team_name": "FC Dallas",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/982.png",
    },
    "houston_dynamo": {
        "team_name": "Houston Dynamo FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/984.png",
    },
    "sporting_kc": {
        "team_name": "Sporting Kansas City",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/985.png",
    },
    "minnesota_united": {
        "team_name": "Minnesota United FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/986.png",
    },
    "chicago_fire": {
        "team_name": "Chicago Fire FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/987.png",
    },
    "columbus_crew": {
        "team_name": "Columbus Crew",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/988.png",
    },
    "dc_united": {
        "team_name": "D.C. United",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/989.png",
    },
    "inter_miami": {
        "team_name": "Inter Miami CF",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/990.png",
    },
    "atlanta_united": {
        "team_name": "Atlanta United FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/991.png",
    },
    "orlando_city": {
        "team_name": "Orlando City SC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/992.png",
    },
    "new_york_city": {
        "team_name": "New York City FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/993.png",
    },
    "new_york_red_bulls": {
        "team_name": "New York Red Bulls",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/994.png",
    },
    "philadelphia_union": {
        "team_name": "Philadelphia Union",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/995.png",
    },
    "toronto_fc": {
        "team_name": "Toronto FC",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/996.png",
    },
    "montreal_cf": {
        "team_name": "CF Montréal",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/997.png",
    },
    "new_england_revolution": {
        "team_name": "New England Revolution",
        "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/998.png",
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

        # Download common opponent logos
        opponents_dir = assets_dir / "opponents"
        opponents_dir.mkdir(parents=True, exist_ok=True)

        for opponent_key, opponent_data in COMMON_OPPONENTS.items():
            logger.info(f"Downloading logo for {opponent_data['team_name']}")
            url = opponent_data["logo"]
            filename = f"{opponent_key}.png"
            filepath = opponents_dir / filename
            await download_image(session, url, filepath)


def create_logo_manifest():
    """Create a manifest file with all logo mappings"""
    manifest = {
        "teams": TEAM_LOGOS,
        "opponents": COMMON_OPPONENTS,
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
