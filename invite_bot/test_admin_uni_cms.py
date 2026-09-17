"""
Verification script for Admin University & Course Management CMS.
Tests adding a new university, editing courses, custom DB overrides, and deleting custom entries.
"""

import asyncio
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from database import db
from university_courses_data import (
    load_university_courses,
    get_all_university_names,
    find_university_courses,
    register_custom_university_course,
    remove_custom_university,
)


async def main():
    print("--- Testing Admin University & Course Management CMS ---")
    await db.init_db()

    test_uni = "Ambo University (AU)"
    test_natural = ["Calculus I", "Physics I", "Logic", "English"]
    test_social = ["Economics", "Geography", "English"]

    print(f"\n1. Adding test university '{test_uni}'...")
    await db.save_custom_university_stream_courses(test_uni, "Natural", test_natural)
    await db.save_custom_university_stream_courses(test_uni, "Social", test_social)
    register_custom_university_course(test_uni, "Natural", test_natural)
    register_custom_university_course(test_uni, "Social", test_social)

    # Verify search
    res = find_university_courses("Ambo University")
    assert res is not None, "Ambo University should be found after adding!"
    official_name, streams = res
    assert "Calculus I" in streams["Natural"]
    assert "Economics" in streams["Social"]
    print(f"✅ Successfully added and verified '{official_name}':")
    print(f"   Natural: {streams['Natural']}")
    print(f"   Social: {streams['Social']}")

    # 2. Test Editing Stream Courses
    print(f"\n2. Editing courses for '{test_uni}' Natural Science...")
    updated_natural = ["Calculus I", "Physics I", "Logic", "English", "Emerging Tech"]
    await db.save_custom_university_stream_courses(test_uni, "Natural", updated_natural)
    register_custom_university_course(test_uni, "Natural", updated_natural)

    res_updated = find_university_courses("Ambo University")
    assert "Emerging Tech" in res_updated[1]["Natural"]
    print(f"✅ Successfully updated Natural stream courses to: {res_updated[1]['Natural']}")

    # 3. Test Deleting Custom University
    print(f"\n3. Deleting test university '{test_uni}'...")
    await db.delete_custom_university_courses(test_uni)
    remove_custom_university(test_uni)

    res_del = find_university_courses("Ambo University")
    assert res_del is None or res_del[0] != test_uni
    print("✅ Successfully deleted test university.")

    print("\n🎉 ALL ADMIN UNIVERSITY CMS TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
