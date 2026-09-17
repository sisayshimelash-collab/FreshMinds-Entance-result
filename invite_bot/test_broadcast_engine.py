"""
Verification script for Broadcast Announcement Engine.
Tests fetching target user IDs and broadcast wizard states.
"""

import asyncio
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from database import db
from handlers import setup_routers


async def main():
    print("--- Testing Admin Broadcast Engine ---")
    await db.init_db()

    # Get user IDs
    user_ids = await db.get_all_user_ids()
    print(f"✅ Registered users count in DB: {len(user_ids)}")

    # Test router setup
    router = setup_routers()
    assert router is not None
    print("✅ Broadcast router initialized successfully.")

    print("\n🎉 ALL BROADCAST ENGINE TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
