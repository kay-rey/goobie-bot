"""
Local logo handler for goobie-bot
Handles pre-downloaded team logos stored in the container
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Path to the logos directory in the container
LOGOS_DIR = Path("/app/assets/logos")
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
                return {"teams": {}, "opponents": {}}
        except Exception as e:
            logger.error(f"Error loading logo manifest: {e}")
            return {"teams": {}, "opponents": {}}

    def get_team_logos(self, team_key: str) -> Optional[Dict[str, str]]:
        """Get logos for a team by key (galaxy, dodgers, lakers, rams, kings)"""
        team_data = self.manifest.get("teams", {}).get(team_key)
        if not team_data:
            logger.warning(f"No logo data found for team key: {team_key}")
            return None

        # Convert to local file paths
        logos = {}
        for logo_type in [
            "logo",
            "logo_small",
            "jersey",
        ]:
            if logo_type in team_data and team_data[logo_type]:
                # Use local file path instead of URL
                local_path = f"/app/assets/logos/{team_key}/{logo_type}.png"
                if Path(local_path).exists():
                    logos[logo_type] = local_path
                else:
                    logger.warning(f"Local logo file not found: {local_path}")
                    # Fallback to original URL if local file missing
                    logos[logo_type] = team_data[logo_type]

        return logos

    def get_opponent_logo(self, opponent_name: str) -> Optional[str]:
        """Get logo for a common opponent team"""
        # Try to find by team name
        for opponent_key, opponent_data in self.manifest.get("opponents", {}).items():
            if opponent_name.lower() in opponent_data.get("team_name", "").lower():
                local_path = f"/app/assets/logos/opponents/{opponent_key}.png"
                if Path(local_path).exists():
                    return local_path
                else:
                    # Fallback to original URL
                    return opponent_data.get("logo")

        logger.warning(f"No logo found for opponent: {opponent_name}")
        return None

    def get_team_logos_by_name(self, team_name: str) -> Optional[Dict[str, str]]:
        """Get logos for a team by name (fallback for unknown teams)"""
        # Try to match against known teams
        for team_key, team_data in self.manifest.get("teams", {}).items():
            if team_name.lower() in team_data.get("team_name", "").lower():
                return self.get_team_logos(team_key)

        # Try opponents
        for opponent_key, opponent_data in self.manifest.get("opponents", {}).items():
            if team_name.lower() in opponent_data.get("team_name", "").lower():
                logo_url = self.get_opponent_logo(opponent_data["team_name"])
                if logo_url:
                    return {
                        "logo": logo_url,
                        "logo_small": logo_url,
                        "jersey": "",
                    }

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
