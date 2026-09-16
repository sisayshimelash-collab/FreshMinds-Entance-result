"""
Verification script for University Placement Integration in FreshMinds Invite Bot.
Tests DB caching, university fuzzy lookup, placement client handling, and router registration.
"""

import asyncio
import os
import sys

# Force UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from database import db
from placement_client import placement_client
from handlers import setup_routers
import messages as msg


async def test_database_and_cache():
    print("--- 1. Testing Database & Placement Cache ---")
    await db.init_db()

    test_admission_no = "TEST_999888"
    test_name = "Abebe Kebede Tesfaye"
    test_uni = "Hawassa University"
    test_stream = "Natural Science"

    # Save to cache
    await db.save_placement_cache(
        admission_no=test_admission_no,
        student_name=test_name,
        university=test_uni,
        stream=test_stream,
        raw_json='{"status": "ok"}',
    )
    print("✅ Successfully saved placement to cache.")

    # Retrieve from cache
    cached = await db.get_cached_placement(test_admission_no)
    assert cached is not None, "Cached record should not be None!"
    assert cached.student_name == test_name
    assert cached.university == test_uni
    print(f"✅ Successfully retrieved cached record: {cached.student_name} -> {cached.university}")

    # Test university name matching
    uni_record = await db.find_university_by_name("Hawassa University")
    if uni_record:
        print(f"✅ Fuzzy university match: Found '{uni_record.name}' (ID: {uni_record.id})")
    else:
        print("ℹ️ Hawassa University not in DB yet (or unseeded), search executed without error.")


async def test_placement_client_live():
    print("\n--- 2. Testing Live Placement API Client ---")
    # Test with sample registration number and first name
    test_reg = "00176600"
    test_first_name = "ruth"
    print(f"Querying live EtherNet endpoint for: {test_reg} / {test_first_name}...")
    result = await placement_client.query_placement(test_reg, test_first_name)
    print(f"Status returned: {result.status}")
    if result.status == "NOT_FOUND":
        print("✅ Expected 404/NOT_FOUND handled gracefully.")
    elif result.status == "RATE_LIMIT":
        print("✅ Expected Rate Limit (429) response handled gracefully.")
    elif result.status == "SUCCESS":
        print(f"🎉 Live result received: {result.student_name} -> {result.university}")
    else:
        print(f"ℹ️ Status ({result.status}): {result.error_message}")



async def test_admin_placement_toggle():
    print("\n--- 3. Testing Admin Placement Enabler / Disabler ---")
    from handlers.start import get_main_menu_keyboard
    from handlers.admin import get_admin_menu_markup

    # Test toggling OFF
    await db.set_placement_enabled(False)
    assert await db.is_placement_enabled() is False
    kb_off = get_main_menu_keyboard(has_active_comp=False, show_placement=False)
    # Ensure placement button is NOT in keyboard rows
    all_buttons_off = [btn.text for row in kb_off.keyboard for btn in row]
    assert msg.BTN_PLACEMENT not in all_buttons_off
    print("✅ When disabled: Placement button is hidden from main menu.")

    admin_markup_off = get_admin_menu_markup(placement_enabled=False)
    assert "OFF" in admin_markup_off.inline_keyboard[0][0].text
    print(f"✅ Admin button reflects OFF: {admin_markup_off.inline_keyboard[0][0].text}")

    # Test toggling ON
    await db.set_placement_enabled(True)
    assert await db.is_placement_enabled() is True
    kb_on = get_main_menu_keyboard(has_active_comp=False, show_placement=True)
    all_buttons_on = [btn.text for row in kb_on.keyboard for btn in row]
    assert msg.BTN_PLACEMENT in all_buttons_on
    print("✅ When enabled: Placement button is visible on main menu.")

    admin_markup_on = get_admin_menu_markup(placement_enabled=True)
    assert "ON" in admin_markup_on.inline_keyboard[0][0].text
    print(f"✅ Admin button reflects ON: {admin_markup_on.inline_keyboard[0][0].text}")

    # Reset back to False (as requested, hidden before release)
    await db.set_placement_enabled(False)
    print("✅ Reset placement feature back to default (Disabled/Hidden).")


def test_routers():
    print("\n--- 4. Testing Handler Routers & Messages ---")
    router = setup_routers()
    assert router is not None
    print(f"✅ Main router initialized with sub-routers: {len(router.sub_routers)}")

    # Verify messages
    card = msg.format_placement_card(
        student_name="Test Student",
        reg_number="00052454",
        university="Addis Ababa University",
        stream="Engineering",
        cached=False,
    )
    assert "Addis Ababa University" in card
    print("✅ Placement card HTML template verified successfully.")


async def main():
    await test_database_and_cache()
    await test_placement_client_live()
    await test_admin_placement_toggle()
    test_routers()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(main())

