"""
Unit & Flow Test Suite for invite_bot
"""

import asyncio
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Test DB in temporary memory/scratch location
test_db_path = Path(__file__).resolve().parent / "test_invite.db"
if test_db_path.exists():
    os.remove(test_db_path)

from database import Database
import messages as msg


async def run_tests():
    print("🧪 Running invite_bot Test Suite...")
    test_db = Database(db_path=test_db_path)

    # 1. Test Database Initialization
    await test_db.init_db()
    print("  ✅ 1. Database schema initialized successfully.")

    # 2. Test User Registration
    u1 = await test_db.get_or_create_user(1001, "abebe_dev", "Abebe")
    u2 = await test_db.get_or_create_user(1002, None, "Sara")  # No username
    u3 = await test_db.get_or_create_user(1003, "chala_k", "Chala")

    assert u1.user_id == 1001 and u1.first_name == "Abebe"
    assert u2.user_id == 1002 and u2.username is None and u2.first_name == "Sara"
    print("  ✅ 2. User registration (with and without @username) passed.")

    # 3. Test Link Assignment & Lookup
    link1 = "https://t.me/+AbCdEf1001"
    link2 = "https://t.me/+GhIjKl1002"
    await test_db.set_user_invite_link(1001, link1)
    await test_db.set_user_invite_link(1002, link2)

    found_u1 = await test_db.get_user_by_invite_link(link1)
    assert found_u1 and found_u1.user_id == 1001
    print("  ✅ 3. Unique invite link generation & mapping passed.")

    # 4. Test Referrals & Anti-Cheat
    # Abebe invites 3 real friends
    c1 = await test_db.record_referral(1001, 2001, link1)
    c2 = await test_db.record_referral(1001, 2002, link1)
    c3 = await test_db.record_referral(1001, 2003, link1)
    assert c1 and c2 and c3

    # Self-referral attempt (must fail)
    self_ref = await test_db.record_referral(1001, 1001, link1)
    assert not self_ref, "Self-referral must be blocked"

    # Duplicate referral attempt (user 2001 joins again via Sara's link link2 - must fail)
    dup_ref = await test_db.record_referral(1002, 2001, link2)
    assert not dup_ref, "Duplicate user join must not give multiple credits"

    # Test Pending Referrer flow
    await test_db.set_pending_referrer(5001, 1001)
    pending = await test_db.get_pending_referrer(5001)
    assert pending == 1001
    await test_db.clear_pending_referrer(5001)
    assert await test_db.get_pending_referrer(5001) is None

    # Sara invites 5 real friends
    for friend_id in range(3001, 3006):
        await test_db.record_referral(1002, friend_id, link2)

    print("  ✅ 4. Referral tracking & Anti-Cheat enforcement passed.")

    # 5. Test Leaderboard & Rankings
    top_list = await test_db.get_top_leaderboard(limit=10)
    assert len(top_list) == 2
    assert top_list[0].user_id == 1002 and top_list[0].points == 5  # Sara: 1st
    assert top_list[1].user_id == 1001 and top_list[1].points == 3  # Abebe: 2nd

    # Test user rank lookup
    pts_sara, _, rank_sara = await test_db.get_user_stats(1002)
    pts_abebe, _, rank_abebe = await test_db.get_user_stats(1001)
    assert rank_sara == 1 and pts_sara == 5
    assert rank_abebe == 2 and pts_abebe == 3
    print("  ✅ 5. Real-time Leaderboard and ranking calculation passed.")

    # 6. Test Member Leave Deduction
    deducted_referrer = await test_db.handle_member_leave(3005)  # Sara's friend leaves
    assert deducted_referrer == 1002

    pts_sara_after, _, _ = await test_db.get_user_stats(1002)
    assert pts_sara_after == 4  # Sara drops to 4
    print("  ✅ 6. Member departure deduction (Anti-Churn) passed.")

    # 7. Test Message Formatting
    promo_post = msg.format_promotional_post(link1)
    assert link1 in promo_post
    assert "FreshMinds Academy" in promo_post

    link_card = msg.format_link_card(link1)
    assert f"<code>{link1}</code>" in link_card

    # Test regular user leaderboard (unclickable & private)
    lb_user = msg.format_leaderboard(top_list, rank_abebe, pts_abebe, is_admin=False)
    assert "🥇" in lb_user
    assert "@" not in lb_user

    # Test admin leaderboard (clickable username/profile)
    lb_admin = msg.format_leaderboard(top_list, rank_abebe, pts_abebe, is_admin=True)
    assert "🥇" in lb_admin
    assert "https://t.me/" in lb_admin

    print("  ✅ 7. Amharic & English message templates formatting verified.")

    # 8. Test Universities CRUD & Seeding
    unis = await test_db.get_all_universities()
    assert len(unis) >= 5, "Default universities should be seeded"
    assert any("Addis Ababa University" in u.name for u in unis)

    new_uni_id = await test_db.add_university("Gondar University (UoG)", "About Gondar...")
    gondar = await test_db.get_university_by_id(new_uni_id)
    assert gondar and gondar.name == "Gondar University (UoG)"
    await test_db.delete_university(new_uni_id)
    assert await test_db.get_university_by_id(new_uni_id) is None
    print("  ✅ 8. Universities directory CRUD & default seeding passed.")

    # 9. Test Courses & Materials CRUD & Seeding
    courses = await test_db.get_all_courses()
    assert len(courses) >= 10, "Default freshman courses should be seeded"
    assert "Applied Mathematics I" in courses[0].name

    c1_id = courses[0].id
    m1_id = await test_db.add_material(
        course_id=c1_id,
        category="midterm",
        title="2016 Midterm Exam with Solutions",
        file_id="tg_doc_12345",
    )
    materials = await test_db.get_materials_by_course(c1_id, "midterm")
    assert len(materials) == 1 and materials[0].title == "2016 Midterm Exam with Solutions"
    await test_db.delete_material(m1_id)
    assert len(await test_db.get_materials_by_course(c1_id, "midterm")) == 0
    print("  ✅ 9. Courses & Materials explorer CRUD passed.")

    # 10. Test GPA Calculator Math Engine
    # Student has 5 courses filled and 3 unfilled courses (Course 6, 7, 8 are None)
    test_courses_data = {
        1: {"ch": 4, "grade": "A"},    # 4 * 4.0 = 16.0
        2: {"ch": 3, "grade": "A-"},   # 3 * 3.75 = 11.25
        3: {"ch": 3, "grade": "B+"},   # 3 * 3.5 = 10.5
        4: {"ch": 3, "grade": "A"},    # 3 * 4.0 = 12.0
        5: {"ch": 2, "grade": "B"},    # 2 * 3.0 = 6.0
        6: {"ch": None, "grade": None}, # Unfilled - must be ignored!
        7: {"ch": None, "grade": None}, # Unfilled - must be ignored!
        8: {"ch": None, "grade": None}, # Unfilled - must be ignored!
    }
    # Total CH = 4 + 3 + 3 + 3 + 2 = 15
    # Total Pts = 16.0 + 11.25 + 10.5 + 12.0 + 6.0 = 55.75
    # GPA = 55.75 / 15 = 3.71666... -> 3.72
    gpa, total_ch, total_pts, breakdown = msg.calculate_gpa(test_courses_data)
    assert total_ch == 15
    assert total_pts == 55.75
    assert gpa == 3.72
    assert len(breakdown) == 5

    gpa_card = msg.format_gpa_result_card(gpa, total_ch, total_pts, breakdown)
    assert "3.72 / 4.00" in gpa_card
    assert "Great Distinction" in gpa_card
    print("  ✅ 10. GPA Calculator math engine (ignoring unfilled courses) passed.")

    # Clean up test DB
    if test_db_path.exists():
        os.remove(test_db_path)

    print("\n🎉 ALL 10 TEST SUITES PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    asyncio.run(run_tests())

