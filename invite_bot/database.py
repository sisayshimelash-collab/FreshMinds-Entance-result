"""
FreshMinds Invite Competition Bot — Async SQLite Database Layer
"""

import aiosqlite
import logging
from typing import Optional, NamedTuple
from datetime import datetime
from config import DB_PATH

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
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Referrals Table (1 credit per referred user ID)
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

            # Indexes for fast leaderboard & lookup queries
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_link ON users(invite_link);"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id, is_active);"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_user_id);"
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

    async def get_user_by_invite_link(self, invite_link: str) -> Optional[UserRecord]:
        """Find the referrer user who owns a given invite link."""
        if not invite_link:
            return None
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT user_id, username, first_name, invite_link, created_at FROM users WHERE invite_link = ?",
                (invite_link.strip(),),
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


# Global database instance
db = Database()
