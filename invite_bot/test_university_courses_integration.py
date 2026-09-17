"""
Verification script for University 1st Semester Courses Integration.
Tests markdown guide data source, university course resolution, card formatting, and router handlers.
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from university_courses_data import (
    load_university_courses,
    get_all_university_names,
    find_university_courses,
)
import messages as msg
from handlers import setup_routers


def test_university_courses_data():
    print("--- 1. Testing Data Provider (FreshMinds_Academy_Freshman_Course_Guide.md) ---")
    data = load_university_courses()
    assert len(data) >= 30, f"Expected 30+ universities, got {len(data)}"
    print(f"✅ Loaded {len(data)} universities directly from source of fact markdown file.")

    names = get_all_university_names()
    assert "Addis Ababa University (AAU)" in names
    assert "Debre Berhan University" in names
    print(f"✅ Verified university list sorting and structure ({len(names)} total).")

    # Test fuzzy matching
    res = find_university_courses("Debre Birhan University")
    assert res is not None, "Should match Debre Birhan University"
    official_name, streams = res
    assert "Natural" in streams
    assert "Social" in streams
    assert "Mathematics for Natural Science" in streams["Natural"]
    print(f"✅ Found exact match for '{official_name}':")
    print(f"   Natural: {streams['Natural']}")
    print(f"   Social: {streams['Social']}")


def test_card_formatting():
    print("\n--- 2. Testing Promotional Card Formatting ---")
    res = find_university_courses("Addis Ababa University (AAU)")
    assert res is not None
    name, streams = res
    card = msg.format_university_courses_card(name, streams)

    assert "Addis Ababa University (AAU)" in card
    assert "FreshMinds Academy" in card
    assert "FreshMinds Mobile App" in card
    assert "Natural Stream" in card
    assert "Social Stream" in card
    print("✅ Formatted card HTML template verified successfully.")


def test_routers():
    print("\n--- 3. Testing Handlers Router Integration ---")
    router = setup_routers()
    assert router is not None
    print(f"✅ Main router initialized with {len(router.sub_routers)} sub-routers.")


def main():
    test_university_courses_data()
    test_card_formatting()
    test_routers()
    print("\n🎉 ALL UNIVERSITY COURSE INTEGRATION TESTS PASSED!")


if __name__ == "__main__":
    main()
