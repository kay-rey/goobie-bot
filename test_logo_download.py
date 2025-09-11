#!/usr/bin/env python3
"""
Test script for logo downloader
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.download_logos import main

if __name__ == "__main__":
    print("Testing logo downloader...")
    asyncio.run(main())
    print("Logo download test completed!")
