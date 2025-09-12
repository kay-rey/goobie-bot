"""
Local logo handler for goobie-bot
Handles pre-downloaded team logos stored in the container
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


# Path to the logos directory - works both locally and in Docker
def get_logos_dir():
    """Get the appropriate logos directory path"""
    if Path("/app").exists() and Path("/app").is_dir():
        return Path("/app/assets/logos")
    else:
        return Path("assets/logos")


LOGOS_DIR = get_logos_dir()
MANIFEST_PATH = LOGOS_DIR / "manifest.json"


class LocalLogoManager:
    """Manages local team logos and provides fast access"""

    def __init__(self):
        self.manifest = self._load_manifest()
        self.base_url = (
            "https://your-bot-domain.com"  # Will be replaced with actual domain
        )

    def _load_manifest(self) -> Dict:
        """Load the logo manifest file"""
        try:
            if MANIFEST_PATH.exists():
                with open(MANIFEST_PATH, "r") as f:
                    manifest = json.load(f)
                logger.info(
                    f"Loaded logo manifest with {len(manifest.get('teams', {}))} teams"
                )
                return manifest
            else:
                logger.warning("Logo manifest not found, using empty manifest")
                return {"teams": {}}
        except Exception as e:
            logger.error(f"Error loading logo manifest: {e}")
            return {"teams": {}}

    def get_team_logos(self, team_key: str) -> Optional[Dict[str, str]]:
        """Get logos for a team by key (galaxy, dodgers, lakers, rams, kings)"""
        team_data = self.manifest.get("teams", {}).get(team_key)
        if not team_data:
            logger.warning(f"No logo data found for team key: {team_key}")
            return None

        # Convert to URLs (Discord needs HTTP URLs, not local file paths)
        logos = {}
        for logo_type in [
            "logo",
            "logo_small",
        ]:
            if logo_type in team_data and team_data[logo_type]:
                # Check if local file exists for verification
                local_path = f"{LOGOS_DIR}/{team_key}/{logo_type}.png"
                if Path(local_path).exists():
                    # Use GitHub URL as primary (more reliable)
                    logos[logo_type] = team_data[logo_type]
                    logger.debug(
                        f"Using GitHub logo URL for {team_key} {logo_type}: {team_data[logo_type]}"
                    )
                else:
                    logger.warning(f"Local logo file not found: {local_path}")
                    # Fallback to TheSportsDB URL if local file missing
                    fallback_key = f"{logo_type}_fallback"
                    if fallback_key in team_data:
                        logos[logo_type] = team_data[fallback_key]
                        logger.debug(
                            f"Using fallback URL for {team_key} {logo_type}: {team_data[fallback_key]}"
                        )
                    else:
                        logos[logo_type] = team_data[logo_type]

        return logos

    def get_team_logos_by_name(self, team_name: str) -> Optional[Dict[str, str]]:
        """Get logos for a team by name (fallback for unknown teams)"""
        # Try to match against known teams
        for team_key, team_data in self.manifest.get("teams", {}).items():
            if team_name.lower() in team_data.get("team_name", "").lower():
                return self.get_team_logos(team_key)

        logger.warning(f"No logo found for team name: {team_name}")
        return None


# Global instance
local_logo_manager = LocalLogoManager()


def get_local_team_logos(team_key: str) -> Optional[Dict[str, str]]:
    """Get local team logos by key"""
    return local_logo_manager.get_team_logos(team_key)


def get_local_opponent_logo(opponent_name: str) -> Optional[str]:
    """Get local opponent logo by name"""
    return local_logo_manager.get_opponent_logo(opponent_name)


def get_local_team_logos_by_name(team_name: str) -> Optional[Dict[str, str]]:
    """Get local team logos by name"""
    return local_logo_manager.get_team_logos_by_name(team_name)


# Team key mappings for easy lookup
TEAM_KEY_MAPPING = {
    "galaxy": "galaxy",
    "dodgers": "dodgers",
    "lakers": "lakers",
    "rams": "rams",
    "kings": "kings",
}


def get_team_key_from_choice(team_choice: str) -> str:
    """Get team key from Discord choice value"""
    return TEAM_KEY_MAPPING.get(team_choice, team_choice)
