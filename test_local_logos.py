#!/usr/bin/env python3
"""
Test script for local logo system
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api.local_logos import get_local_team_logos, get_team_key_from_choice


def test_local_logos():
    """Test the local logo system"""
    print("Testing local logo system...")

    # Test each team
    teams = ["galaxy", "dodgers", "lakers", "rams", "kings"]

    for team in teams:
        print(f"\nTesting {team}:")
        team_key = get_team_key_from_choice(team)
        logos = get_local_team_logos(team_key)

        if logos:
            print(f"  ✓ Found logos for {team}")
            for logo_type, logo_path in logos.items():
                if logo_path and Path(logo_path).exists():
                    print(f"    ✓ {logo_type}: {logo_path}")
                else:
                    print(f"    ✗ {logo_type}: {logo_path} (file not found)")
        else:
            print(f"  ✗ No logos found for {team}")

    print("\nLocal logo test completed!")


if __name__ == "__main__":
    test_local_logos()
