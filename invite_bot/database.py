"""
FreshMinds Invite Competition Bot — Async SQLite Database Layer
"""

import aiosqlite
import logging
from typing import Optional, NamedTuple
from datetime import datetime
from config import (
    DB_PATH,
    COMPETITION_TITLE,
    PRIZE_1ST,
    PRIZE_2ND,
    PRIZE_3RD,
    PRIZE_4TH,
)

logger = logging.getLogger(__name__)


class UserRecord(NamedTuple):
    user_id: int
    username: Optional[str]
    first_name: str
    invite_link: Optional[str]
    created_at: str


class LeaderboardEntry(NamedTuple):
    rank: int
    user_id: int
    first_name: str
    username: Optional[str]
    points: int


class UniversityRecord(NamedTuple):
    id: int
    name: str
    about_text: str
    sort_order: int


class CourseRecord(NamedTuple):
    id: int
    name: str
    code: str
    icon: str
    sort_order: int


class MaterialRecord(NamedTuple):
    id: int
    course_id: int
    category: str
    title: str
    file_id: Optional[str]
    external_url: Optional[str]


class CompetitionRecord(NamedTuple):
    id: int
    title: str
    prizes_text: str
    end_date_str: str
    is_active: int
    created_at: str


class Database:
    """Async SQLite database manager for user links, referrals, and leaderboards."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Create database tables and performance indexes."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")

            # 1. Users Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT NOT NULL,
                    invite_link TEXT UNIQUE,
                    pending_referrer_id INTEGER,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure pending_referrer_id column exists if table was created previously
            try:
                await db.execute("ALTER TABLE users ADD COLUMN pending_referrer_id INTEGER;")
            except Exception:
                pass  # Already exists
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referred_user_id INTEGER NOT NULL UNIQUE,
                    invite_link TEXT,
                    is_active INTEGER DEFAULT 1,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    left_at TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(user_id)
                );
            """)

            # 3. Weekly Archives
            await db.execute("""
                CREATE TABLE IF NOT EXISTS weekly_archives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_name TEXT NOT NULL,
                    ended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    winners_json TEXT NOT NULL
                );
            """)

            # 4. Universities Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS universities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    about_text TEXT NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 5. Courses Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    code TEXT,
                    icon TEXT DEFAULT '📚',
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 6. Course Materials Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS course_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    file_id TEXT,
                    external_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                );
            """)

            # Indexes for fast lookup queries
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_link ON users(invite_link);"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id, is_active);"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_user_id);"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_materials_course ON course_materials(course_id, category);"
            )

            # Seed default courses if empty
            cursor = await db.execute("SELECT COUNT(*) FROM courses")
            if (await cursor.fetchone())[0] == 0:
                default_courses = [
                    ("Applied Mathematics I", "MATH1011", "📐", 1),
                    ("General Physics", "PHYS1011", "⚡", 2),
                    ("General Chemistry", "CHEM1011", "🧪", 3),
                    ("Logic & Critical Thinking", "PHIL1011", "🧠", 4),
                    ("Introduction to Emerging Tech", "EMTE1011", "💻", 5),
                    ("Geography of Ethiopia & Horn", "GEOG1011", "🌍", 6),
                    ("Communicative English Skills I", "ENGL1011", "🗣️", 7),
                    ("Inclusiveness", "INCL1011", "🤝", 8),
                    ("Social Anthropology", "ANTH1011", "🏛️", 9),
                    ("General Psychology", "PSYC1011", "🧘", 10),
                ]
                await db.executemany(
                    "INSERT INTO courses (name, code, icon, sort_order) VALUES (?, ?, ?, ?)",
                    default_courses,
                )

            # Seed default universities if empty
            cursor = await db.execute("SELECT COUNT(*) FROM universities")
            if (await cursor.fetchone())[0] == 0:
                try:
                    from seed_universities import UNIVERSITIES_DATA
                    default_unis = UNIVERSITIES_DATA
                except Exception:
                    default_unis = []
                if default_unis:
                    await db.executemany(
                        "INSERT INTO universities (name, about_text, sort_order) VALUES (?, ?, ?)",
                        default_unis,
                    )

            # 7. Competitions Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS competitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    prizes_text TEXT NOT NULL,
                    end_date_str TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Seed default competition if empty
            cursor = await db.execute("SELECT COUNT(*) FROM competitions")
            if (await cursor.fetchone())[0] == 0:
                default_prizes = (
                    f"🥇 1ኛ: {PRIZE_1ST}\n"
                    f"🥈 2ኛ: {PRIZE_2ND}\n"
                    f"🥉 3ኛ: {PRIZE_3RD}\n"
                    f"🎖️ 4ኛ: {PRIZE_4TH}"
                )
                await db.execute(
                    """
                    INSERT INTO competitions (title, prizes_text, end_date_str, is_active)
                    VALUES (?, ?, ?, 1)
                    """,
                    (COMPETITION_TITLE, default_prizes, "የመስከረም 15 2019 ዓ.ም"),
                )

            await db.commit()
            logger.info("Database initialized successfully.")

    async def get_or_create_user(
        self, user_id: int, username: Optional[str], first_name: str
    ) -> UserRecord:
        """Fetch existing user or create a new user entry."""
        clean_first_name = first_name.strip() if first_name else "Student"
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT user_id, username, first_name, invite_link, created_at FROM users WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()

            if row:
                # Update username or first_name if changed
                if row["username"] != username or row["first_name"] != clean_first_name:
                    await db.execute(
                        "UPDATE users SET username = ?, first_name = ? WHERE user_id = ?",
                        (username, clean_first_name, user_id),
                    )
                    await db.commit()
                return UserRecord(
                    user_id=row["user_id"],
                    username=username,
                    first_name=clean_first_name,
                    invite_link=row["invite_link"],
                    created_at=str(row["created_at"]),
                )

            # Insert new user
            await db.execute(
                "INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, username, clean_first_name),
            )
            await db.commit()
            return UserRecord(
                user_id=user_id,
                username=username,
                first_name=clean_first_name,
                invite_link=None,
                created_at=datetime.utcnow().isoformat(),
            )

    async def set_user_invite_link(self, user_id: int, invite_link: str):
        """Save unique generated direct channel invite link for user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET invite_link = ? WHERE user_id = ?",
                (invite_link.strip(), user_id),
            )
            await db.commit()

    async def set_pending_referrer(self, user_id: int, referrer_id: int):
        """Set a pending referrer for a user before they join the channel."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, first_name, pending_referrer_id)
                VALUES (?, 'Student', ?)
                ON CONFLICT(user_id) DO UPDATE SET pending_referrer_id = excluded.pending_referrer_id
                """,
                (user_id, referrer_id),
            )
            await db.commit()

    async def get_pending_referrer(self, user_id: int) -> Optional[int]:
        """Get pending referrer for a user."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT pending_referrer_id FROM users WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row and row[0] else None

    async def clear_pending_referrer(self, user_id: int):
        """Clear pending referrer for a user after referral credit is processed."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET pending_referrer_id = NULL WHERE user_id = ?",
                (user_id,),
            )
            await db.commit()

    async def get_user_by_invite_link(self, invite_link: str) -> Optional[UserRecord]:
        """Find the referrer user who owns a given invite link with flexible matching."""
        if not invite_link:
            return None
        clean_link = invite_link.strip().rstrip('/')
        link_hash = clean_link.split('/')[-1]

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT user_id, username, first_name, invite_link, created_at FROM users WHERE invite_link = ? OR invite_link LIKE ?",
                (clean_link, f"%{link_hash}%"),
            )
            row = await cursor.fetchone()
            if row:
                return UserRecord(
                    user_id=row["user_id"],
                    username=row["username"],
                    first_name=row["first_name"],
                    invite_link=row["invite_link"],
                    created_at=str(row["created_at"]),
                )
            return None

    async def add_manual_points(self, referrer_id: int, points: int) -> int:
        """Add manual bonus referral credits to a user (Admin)."""
        import time
        async with aiosqlite.connect(self.db_path) as db:
            for i in range(points):
                fake_ref_id = int(time.time() * 1000) + i
                try:
                    await db.execute(
                        "INSERT INTO referrals (referrer_id, referred_user_id, invite_link, is_active) VALUES (?, ?, 'manual_bonus', 1)",
                        (referrer_id, fake_ref_id),
                    )
                except Exception:
                    pass
            await db.commit()
            cursor = await db.execute(
                "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_active = 1",
                (referrer_id,),
            )
            return (await cursor.fetchone())[0]

    async def remove_manual_points(self, referrer_id: int, points: int) -> int:
        """Deduct points from a user (Admin)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE referrals 
                SET is_active = 0, left_at = CURRENT_TIMESTAMP 
                WHERE id IN (
                    SELECT id FROM referrals WHERE referrer_id = ? AND is_active = 1 LIMIT ?
                )
                """,
                (referrer_id, points),
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_active = 1",
                (referrer_id,),
            )
            return (await cursor.fetchone())[0]

    async def list_all_participants(self, limit: int = 50) -> list[dict]:
        """List participants with their active invite counts."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT 
                    u.user_id,
                    u.first_name,
                    u.username,
                    u.invite_link,
                    COUNT(r.id) as active_points
                FROM users u
                LEFT JOIN referrals r ON u.user_id = r.referrer_id AND r.is_active = 1
                GROUP BY u.user_id
                ORDER BY active_points DESC, u.created_at ASC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def record_referral(
        self, referrer_id: int, referred_user_id: int, invite_link: str
    ) -> bool:
        """
        Record a verified new member referral.
        Returns True if referral is successfully credited, False if already credited before or self-referral.
        """
        # Anti-cheat: self-referral check
        if referrer_id == referred_user_id:
            return False

        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """
                    INSERT INTO referrals (referrer_id, referred_user_id, invite_link, is_active)
                    VALUES (?, ?, ?, 1)
                    """,
                    (referrer_id, referred_user_id, invite_link),
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                # User was already referred by someone in the past (1 credit per lifetime account)
                return False

    async def handle_member_leave(self, referred_user_id: int) -> Optional[int]:
        """
        Mark a referral as inactive if a member leaves the channel.
        Returns the referrer_id if a point was deducted, or None.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT referrer_id FROM referrals WHERE referred_user_id = ? AND is_active = 1",
                (referred_user_id,),
            )
            row = await cursor.fetchone()
            if row:
                referrer_id = row["referrer_id"]
                await db.execute(
                    """
                    UPDATE referrals 
                    SET is_active = 0, left_at = CURRENT_TIMESTAMP 
                    WHERE referred_user_id = ?
                    """,
                    (referred_user_id,),
                )
                await db.commit()
                return referrer_id
            return None

    async def get_user_stats(self, user_id: int) -> tuple[int, int, int]:
        """
        Get user statistics: (active_points, total_joins, rank).
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Active points (currently in channel)
            cursor = await db.execute(
                "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_active = 1",
                (user_id,),
            )
            active_points = (await cursor.fetchone())[0]

            # Total joins ever
            cursor = await db.execute(
                "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?",
                (user_id,),
            )
            total_joins = (await cursor.fetchone())[0]

            # Calculate Rank
            cursor = await db.execute(
                """
                SELECT COUNT(*) + 1 
                FROM (
                    SELECT referrer_id, COUNT(*) as pts 
                    FROM referrals 
                    WHERE is_active = 1 
                    GROUP BY referrer_id 
                    HAVING pts > ?
                )
                """,
                (active_points,),
            )
            rank = (await cursor.fetchone())[0]

            return active_points, total_joins, rank

    async def get_top_leaderboard(self, limit: int = 10) -> list[LeaderboardEntry]:
        """Fetch top inviters ordered by active verified points."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT 
                    u.user_id,
                    u.first_name,
                    u.username,
                    COUNT(r.id) as points
                FROM referrals r
                JOIN users u ON r.referrer_id = u.user_id
                WHERE r.is_active = 1
                GROUP BY r.referrer_id
                HAVING points > 0
                ORDER BY points DESC, r.id ASC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            leaderboard = []
            for idx, row in enumerate(rows, start=1):
                leaderboard.append(
                    LeaderboardEntry(
                        rank=idx,
                        user_id=row["user_id"],
                        first_name=row["first_name"],
                        username=row["username"],
                        points=row["points"],
                    )
                )
            return leaderboard

    async def get_all_user_ids(self) -> list[int]:
        """Fetch all registered user IDs for broadcast announcements."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM users WHERE is_active = 1")
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

    async def get_audit_for_user(self, user_id: int) -> list[dict]:
        """Detailed list of members invited by a specific user for fraud checking."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT referred_user_id, is_active, joined_at, left_at 
                FROM referrals 
                WHERE referrer_id = ? 
                ORDER BY joined_at DESC
                """,
                (user_id,),
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_total_campaign_stats(self) -> tuple[int, int, int]:
        """Total participants, total channel joins generated, active members."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await cursor.fetchone())[0]

            cursor = await db.execute("SELECT COUNT(*) FROM referrals")
            total_joins = (await cursor.fetchone())[0]

            cursor = await db.execute(
                "SELECT COUNT(*) FROM referrals WHERE is_active = 1"
            )
            active_joins = (await cursor.fetchone())[0]

            return total_users, total_joins, active_joins

    async def reset_weekly_competition(self, cycle_name: str) -> list[LeaderboardEntry]:
        """Archive current week's leaderboard and reset referral points."""
        import json

        top_winners = await self.get_top_leaderboard(limit=10)
        winners_data = [
            {
                "rank": w.rank,
                "user_id": w.user_id,
                "first_name": w.first_name,
                "username": w.username,
                "points": w.points,
            }
            for w in top_winners
        ]

        async with aiosqlite.connect(self.db_path) as db:
            # Save archive
            await db.execute(
                "INSERT INTO weekly_archives (cycle_name, winners_json) VALUES (?, ?)",
                (cycle_name, json.dumps(winners_data)),
            )
            # Clear referrals table for fresh week
            await db.execute("DELETE FROM referrals")
            await db.commit()

        return top_winners

    # ── Universities CRUD ────────────────────────────────────────────────────
    async def get_all_universities(self) -> list[UniversityRecord]:
        """Fetch all universities ordered alphabetically by name."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, name, about_text, sort_order FROM universities ORDER BY name ASC"
            )
            rows = await cursor.fetchall()
            return [
                UniversityRecord(
                    id=r["id"],
                    name=r["name"],
                    about_text=r["about_text"],
                    sort_order=r["sort_order"],
                )
                for r in rows
            ]

    async def get_university_by_id(self, uni_id: int) -> Optional[UniversityRecord]:
        """Fetch single university by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, name, about_text, sort_order FROM universities WHERE id = ?",
                (uni_id,),
            )
            row = await cursor.fetchone()
            if row:
                return UniversityRecord(
                    id=row["id"],
                    name=row["name"],
                    about_text=row["about_text"],
                    sort_order=row["sort_order"],
                )
            return None

    async def add_university(self, name: str, about_text: str) -> int:
        """Add new university."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO universities (name, about_text) VALUES (?, ?)",
                (name.strip(), about_text.strip()),
            )
            await db.commit()
            return cursor.lastrowid

    async def delete_university(self, uni_id: int) -> bool:
        """Delete a university by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM universities WHERE id = ?", (uni_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def update_university(self, uni_id: int, about_text: str) -> bool:
        """Update the about text of an existing university by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "UPDATE universities SET about_text = ? WHERE id = ?",
                (about_text.strip(), uni_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    # ── Courses CRUD ─────────────────────────────────────────────────────────
    async def get_all_courses(self) -> list[CourseRecord]:
        """Fetch all courses ordered by sort_order and name."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, name, code, icon, sort_order FROM courses ORDER BY sort_order ASC, name ASC"
            )
            rows = await cursor.fetchall()
            return [
                CourseRecord(
                    id=r["id"],
                    name=r["name"],
                    code=r["code"] or "",
                    icon=r["icon"] or "📚",
                    sort_order=r["sort_order"],
                )
                for r in rows
            ]

    async def get_course_by_id(self, course_id: int) -> Optional[CourseRecord]:
        """Fetch single course by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, name, code, icon, sort_order FROM courses WHERE id = ?",
                (course_id,),
            )
            row = await cursor.fetchone()
            if row:
                return CourseRecord(
                    id=row["id"],
                    name=row["name"],
                    code=row["code"] or "",
                    icon=row["icon"] or "📚",
                    sort_order=row["sort_order"],
                )
            return None

    async def add_course(self, name: str, code: str = "", icon: str = "📚") -> int:
        """Add new course."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO courses (name, code, icon) VALUES (?, ?, ?)",
                (name.strip(), code.strip(), icon.strip() or "📚"),
            )
            await db.commit()
            return cursor.lastrowid

    async def delete_course(self, course_id: int) -> bool:
        """Delete a course and its materials."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM course_materials WHERE course_id = ?", (course_id,))
            cursor = await db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            await db.commit()
            return cursor.rowcount > 0

    # ── Course Materials CRUD ────────────────────────────────────────────────
    async def get_materials_by_course(
        self, course_id: int, category: Optional[str] = None
    ) -> list[MaterialRecord]:
        """Fetch materials for a specific course and optional category."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if category:
                cursor = await db.execute(
                    """
                    SELECT id, course_id, category, title, file_id, external_url
                    FROM course_materials
                    WHERE course_id = ? AND category = ?
                    ORDER BY id DESC
                    """,
                    (course_id, category),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT id, course_id, category, title, file_id, external_url
                    FROM course_materials
                    WHERE course_id = ?
                    ORDER BY id DESC
                    """,
                    (course_id,),
                )
            rows = await cursor.fetchall()
            return [
                MaterialRecord(
                    id=r["id"],
                    course_id=r["course_id"],
                    category=r["category"],
                    title=r["title"],
                    file_id=r["file_id"],
                    external_url=r["external_url"],
                )
                for r in rows
            ]

    async def get_material_by_id(self, material_id: int) -> Optional[MaterialRecord]:
        """Fetch single material by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, course_id, category, title, file_id, external_url FROM course_materials WHERE id = ?",
                (material_id,),
            )
            row = await cursor.fetchone()
            if row:
                return MaterialRecord(
                    id=row["id"],
                    course_id=row["course_id"],
                    category=row["category"],
                    title=row["title"],
                    file_id=row["file_id"],
                    external_url=row["external_url"],
                )
            return None

    async def add_material(
        self,
        course_id: int,
        category: str,
        title: str,
        file_id: Optional[str] = None,
        external_url: Optional[str] = None,
    ) -> int:
        """Add new material file or link for a course."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO course_materials (course_id, category, title, file_id, external_url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (course_id, category, title.strip(), file_id, external_url),
            )
            await db.commit()
            return cursor.lastrowid

    async def delete_material(self, material_id: int) -> bool:
        """Delete material by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM course_materials WHERE id = ?", (material_id,))
            await db.commit()
            return cursor.rowcount > 0

    # ── Competitions CRUD ────────────────────────────────────────────────────
    async def get_active_competition(self) -> Optional[CompetitionRecord]:
        """Fetch the currently active competition, if any."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, title, prizes_text, end_date_str, is_active, created_at
                FROM competitions
                WHERE is_active = 1
                ORDER BY id DESC
                LIMIT 1
                """
            )
            row = await cursor.fetchone()
            if row:
                return CompetitionRecord(
                    id=row["id"],
                    title=row["title"],
                    prizes_text=row["prizes_text"],
                    end_date_str=row["end_date_str"],
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                )
            return None

    async def create_competition(
        self, title: str, prizes_text: str, end_date_str: str
    ) -> int:
        """Create a new active competition, deactivating any existing active ones and clearing active referrals."""
        async with aiosqlite.connect(self.db_path) as db:
            # Deactivate any currently active competitions
            await db.execute("UPDATE competitions SET is_active = 0 WHERE is_active = 1")
            # Clear old referrals to start fresh
            await db.execute("DELETE FROM referrals")
            # Insert new competition
            cursor = await db.execute(
                """
                INSERT INTO competitions (title, prizes_text, end_date_str, is_active)
                VALUES (?, ?, ?, 1)
                """,
                (title.strip(), prizes_text.strip(), end_date_str.strip()),
            )
            await db.commit()
            return cursor.lastrowid

    async def end_active_competition(
        self, cycle_name: Optional[str] = None
    ) -> list[LeaderboardEntry]:
        """Archive current leaderboard, deactivate the active competition, and clear referrals."""
        import json

        active_comp = await self.get_active_competition()
        comp_title = cycle_name or (active_comp.title if active_comp else "Competition Cycle")

        top_winners = await self.get_top_leaderboard(limit=10)
        winners_data = [
            {
                "rank": w.rank,
                "user_id": w.user_id,
                "first_name": w.first_name,
                "username": w.username,
                "points": w.points,
            }
            for w in top_winners
        ]

        async with aiosqlite.connect(self.db_path) as db:
            # Save archive
            await db.execute(
                "INSERT INTO weekly_archives (cycle_name, winners_json) VALUES (?, ?)",
                (comp_title, json.dumps(winners_data)),
            )
            # Deactivate active competitions
            await db.execute("UPDATE competitions SET is_active = 0 WHERE is_active = 1")
            # Clear referrals
            await db.execute("DELETE FROM referrals")
            await db.commit()

        return top_winners

    async def get_all_competitions(self) -> list[CompetitionRecord]:
        """Fetch all competitions ordered by id descending."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, title, prizes_text, end_date_str, is_active, created_at
                FROM competitions
                ORDER BY id DESC
                """
            )
            rows = await cursor.fetchall()
            return [
                CompetitionRecord(
                    id=r["id"],
                    title=r["title"],
                    prizes_text=r["prizes_text"],
                    end_date_str=r["end_date_str"],
                    is_active=r["is_active"],
                    created_at=r["created_at"],
                )
                for r in rows
            ]


# Global database instance
db = Database()

