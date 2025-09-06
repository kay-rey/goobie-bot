#!/usr/bin/env python3
"""
Test script to verify date filtering is working correctly
"""

import requests
from datetime import datetime, timedelta


def test_date_filtering():
    """Test the date filtering logic"""
    print("🗓️ Testing Date Filtering Logic")
    print("=" * 50)

    # Get current date
    today = datetime.now()
    print(f"Today: {today.strftime('%Y-%m-%d %H:%M')}")

    # Test 2-week window
    start_date = today.strftime("%Y%m%d")
    end_date = (today + timedelta(days=14)).strftime("%Y%m%d")
    print(f"2-week window: {start_date} to {end_date}")

    # ESPN API call
    url = "https://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
    params = {
        "limit": 10,
        "dates": f"{start_date}-{end_date}",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"API Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Number of events found: {len(data.get('items', []))}")

            if data.get("items"):
                print("\n--- Events in 2-week window ---")
                for i, item in enumerate(data["items"]):
                    event_ref = item.get("$ref")
                    if event_ref:
                        event_response = requests.get(event_ref, timeout=10)
                        if event_response.status_code == 200:
                            event_data = event_response.json()
                            event_date_str = event_data.get("date", "")

                            if event_date_str:
                                try:
                                    event_date = datetime.fromisoformat(
                                        event_date_str.replace("Z", "+00:00")
                                    )
                                    today_aware = today.replace(
                                        tzinfo=event_date.tzinfo
                                    )
                                    is_future = event_date > today_aware

                                    print(
                                        f"Event {i + 1}: {event_data.get('name', 'Unknown')}"
                                    )
                                    print(
                                        f"  Date: {event_date.strftime('%Y-%m-%d %H:%M')}"
                                    )
                                    print(f"  Is Future: {is_future}")
                                    print(
                                        f"  Days from now: {(event_date - today_aware).days}"
                                    )
                                    print()
                                except Exception as e:
                                    print(f"Error parsing date: {e}")
            else:
                print("No events found in 2-week window")
                print("This might be correct if there are no upcoming games soon")
        else:
            print(f"API Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_date_filtering()
