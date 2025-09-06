#!/usr/bin/env python3
"""
Test script to verify Pacific Time conversion
"""

from datetime import datetime, timezone, timedelta


def test_timezone_conversion():
    """Test the timezone conversion logic"""
    print("🕐 Testing Pacific Time Conversion")
    print("=" * 50)

    # Test with the September 7th game time from our earlier test
    # Original: 2025-09-07 00:30 UTC
    test_dates = [
        "2025-09-07T00:30Z",  # September 7th game (should be PDT)
        "2025-09-14T00:30Z",  # September 14th game (should be PDT)
        "2025-12-15T20:00Z",  # December game (should be PST)
    ]

    for date_str in test_dates:
        print(f"\n--- Testing: {date_str} ---")

        try:
            # Parse the UTC date
            game_date_utc = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            print(f"UTC: {game_date_utc}")

            # Convert to Pacific Time
            pacific_tz = timezone(timedelta(hours=-8))
            game_date_pacific = game_date_utc.astimezone(pacific_tz)

            # Determine if it's PST or PDT based on the month
            month = game_date_pacific.month
            if 3 <= month <= 10:  # Roughly March to October for PDT
                timezone_name = "PDT"
                # Adjust for PDT (UTC-7)
                pacific_tz = timezone(timedelta(hours=-7))
                game_date_pacific = game_date_utc.astimezone(pacific_tz)
            else:
                timezone_name = "PST"

            # Format for display
            formatted_date = game_date_pacific.strftime(
                f"%A, %B %d, %Y at %I:%M %p {timezone_name}"
            )
            print(f"Pacific: {game_date_pacific} ({timezone_name})")
            print(f"Formatted: {formatted_date}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    test_timezone_conversion()
