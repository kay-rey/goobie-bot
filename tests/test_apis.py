#!/usr/bin/env python3
"""
API Testing Script for goobie-bot

This script tests the TheSportsDB and ESPN APIs to understand their responses
and help debug logo and data issues.
"""

import requests
import json
import asyncio
from datetime import datetime, timedelta


def test_thesportsdb_search():
    """Test TheSportsDB team search API"""
    print("🔍 Testing TheSportsDB Team Search API")
    print("=" * 50)

    url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
    params = {"t": "LA Galaxy"}

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")

            if data.get("teams"):
                print(f"Number of teams found: {len(data['teams'])}")

                for i, team in enumerate(data["teams"]):
                    print(f"\n--- Team {i + 1} ---")
                    print(f"ID: {team.get('idTeam')}")
                    print(f"Name: {team.get('strTeam')}")
                    print(f"Sport: {team.get('strSport')}")
                    print(f"League: {team.get('strLeague')}")
                    print(f"Badge: {team.get('strTeamBadge')}")
                    print(f"Jersey: {team.get('strTeamJersey')}")
                    print(f"Stadium: {team.get('strStadium')}")
                    print(f"Stadium Thumb: {team.get('strStadiumThumb')}")

                    # Test if this is LA Galaxy
                    if "LA Galaxy" in team.get("strTeam", ""):
                        print("✅ Found LA Galaxy!")
                        return team
            else:
                print("❌ No teams found in response")
        else:
            print(f"❌ API Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    return None


def test_thesportsdb_lookup(team_id):
    """Test TheSportsDB team lookup API"""
    print(f"\n🔍 Testing TheSportsDB Team Lookup API for ID: {team_id}")
    print("=" * 50)

    url = f"https://www.thesportsdb.com/api/v1/json/123/lookupteam.php?id={team_id}"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")

            if data.get("teams") and len(data["teams"]) > 0:
                team = data["teams"][0]
                print(f"\n--- Team Details ---")
                print(f"ID: {team.get('idTeam')}")
                print(f"Name: {team.get('strTeam')}")
                print(f"Badge: {team.get('strTeamBadge')}")
                print(f"Jersey: {team.get('strTeamJersey')}")
                print(f"Stadium: {team.get('strStadium')}")
                print(f"Stadium Thumb: {team.get('strStadiumThumb')}")

                # Test logo URLs
                test_logo_urls(team)

                return team
            else:
                print("❌ No team data found")
        else:
            print(f"❌ API Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    return None


def test_logo_urls(team):
    """Test logo URL validity and different sizes"""
    print(f"\n🖼️ Testing Logo URLs")
    print("=" * 50)

    logo_fields = ["strTeamBadge", "strTeamJersey", "strStadiumThumb"]

    for field in logo_fields:
        url = team.get(field, "")
        if url:
            print(f"\n--- {field} ---")
            print(f"Original URL: {url}")

            # Test original URL
            test_url_status(url, "Original")

            # Test different sizes
            for size in ["/small", "/medium", "/tiny"]:
                sized_url = url + size
                test_url_status(sized_url, f"Size {size}")
        else:
            print(f"\n--- {field} ---")
            print("❌ No URL provided")


def test_url_status(url, label):
    """Test if a URL is accessible"""
    try:
        response = requests.head(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {label}: {response.status_code} - {url}")
    except Exception as e:
        print(f"❌ {label}: Error - {e}")


def test_espn_api():
    """Test ESPN API for LA Galaxy games"""
    print(f"\n🏈 Testing ESPN API for LA Galaxy")
    print("=" * 50)

    # Get current date range
    today = datetime.now()
    start_date = today.strftime("%Y%m%d")
    end_date = (today + timedelta(days=180)).strftime("%Y%m%d")

    url = "https://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
    params = {"limit": 5, "dates": f"{start_date}-{end_date}"}

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Date Range: {start_date} to {end_date}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")

            if data.get("items"):
                print(f"Number of events found: {len(data['items'])}")

                for i, item in enumerate(data["items"]):
                    print(f"\n--- Event {i + 1} ---")
                    print(f"Ref: {item.get('$ref')}")

                    # Fetch event details
                    event_ref = item.get("$ref")
                    if event_ref:
                        test_espn_event_details(event_ref, i + 1)
            else:
                print("❌ No events found")
        else:
            print(f"❌ API Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


def test_espn_event_details(event_ref, event_num):
    """Test ESPN event details API"""
    print(f"\n--- Event {event_num} Details ---")

    try:
        response = requests.get(event_ref, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            event_data = response.json()
            print(f"Event Keys: {list(event_data.keys())}")

            # Extract key information
            print(f"Event ID: {event_data.get('id')}")
            print(f"Event Name: {event_data.get('name')}")
            print(f"Event Date: {event_data.get('date')}")

            # Check if it's in the future
            event_date_str = event_data.get("date", "")
            if event_date_str:
                try:
                    event_date = datetime.fromisoformat(
                        event_date_str.replace("Z", "+00:00")
                    )
                    now = datetime.now()
                    is_future = event_date > now
                    print(
                        f"Is Future: {is_future} ({event_date.strftime('%Y-%m-%d %H:%M')})"
                    )
                except Exception as e:
                    print(f"Date parsing error: {e}")

            # Check competitions structure
            competitions = event_data.get("competitions", [])
            if competitions:
                comp = competitions[0]
                print(f"Competition Keys: {list(comp.keys())}")

                # Check competitors
                competitors = comp.get("competitors", [])
                print(f"Number of competitors: {len(competitors)}")

                for i, competitor in enumerate(competitors):
                    print(f"\n--- Competitor {i + 1} ---")
                    print(f"Competitor Keys: {list(competitor.keys())}")
                    print(f"Home/Away: {competitor.get('homeAway')}")

                    # Check team structure
                    team_ref = competitor.get("team", {}).get("$ref")
                    if team_ref:
                        print(f"Team Ref: {team_ref}")
                        test_espn_team_details(team_ref, i + 1)
        else:
            print(f"❌ Event API Error: {response.text}")

    except Exception as e:
        print(f"❌ Event Error: {e}")


def test_espn_team_details(team_ref, team_num):
    """Test ESPN team details API"""
    print(f"\n--- Team {team_num} Details ---")

    try:
        response = requests.get(team_ref, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            team_data = response.json()
            print(f"Team Keys: {list(team_data.keys())}")
            print(f"Team ID: {team_data.get('id')}")
            print(f"Team Name: {team_data.get('displayName')}")
            print(f"Team Short Name: {team_data.get('shortDisplayName')}")
            print(f"Team Abbreviation: {team_data.get('abbreviation')}")
        else:
            print(f"❌ Team API Error: {response.text}")

    except Exception as e:
        print(f"❌ Team Error: {e}")


def main():
    """Run all API tests"""
    print("🤖 Goobie-Bot API Testing Suite")
    print("=" * 60)

    # Test TheSportsDB search
    la_galaxy_team = test_thesportsdb_search()

    if la_galaxy_team:
        team_id = la_galaxy_team.get("idTeam")
        if team_id:
            # Test TheSportsDB lookup
            test_thesportsdb_lookup(team_id)

    # Test ESPN API
    test_espn_api()

    print("\n✅ API Testing Complete!")


if __name__ == "__main__":
    main()
