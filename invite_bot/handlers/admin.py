"""
FreshMinds Invite Competition Bot — Admin Controls & Analytics
"""

import asyncio
import logging
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from database import db
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user ID is in configured ADMIN_IDS."""
    if not ADMIN_IDS:
        return True  # If not configured, allow local dev
    return user_id in ADMIN_IDS


@router.message(Command("admin_stats"))
async def cmd_admin_stats(message: Message):
    """View global campaign growth analytics."""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    total_users, total_joins, active_joins = await db.get_total_campaign_stats()
    churn_rate = (
        ((total_joins - active_joins) / total_joins * 100) if total_joins > 0 else 0
    )

    text = (
        "📈 <b>FreshMinds Invite Campaign Analytics</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 የተመዘገቡ ተሳታፊዎች (Bot Users): <b>{total_users:,}</b>\n"
        f"🚀 አጠቃላይ የተገኙ ሰብስክራይበሮች (Total Joins): <b>{total_joins:,}</b>\n"
        f"✅ ንቁ ሰብስክራይበሮች (Active in Channel): <b>{active_joins:,}</b>\n"
        f"📉 የለቀቁ (Left/Churned): <b>{total_joins - active_joins:,} ({churn_rate:.1f}%)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@router.message(Command("audit"))
async def cmd_audit_user(message: Message):
    """Audit a specific user's referrals for fraud checking: /audit <user_id>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("⚠️ <b>አጠቃቀም:</b> <code>/audit &lt;user_id&gt;</code>", parse_mode=ParseMode.HTML)
        return

    target_user_id = int(args[1])
    audit_rows = await db.get_audit_for_user(target_user_id)
    active_points, total_joins, rank = await db.get_user_stats(target_user_id)

    lines = [
        f"🔍 <b>Referral Audit Report: User <code>{target_user_id}</code></b>",
        f"📊 Active Points: <b>{active_points}</b> | Total Joins: <b>{total_joins}</b> | Rank: <b>#{rank}</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    if not audit_rows:
        lines.append("<i>ምንም የተጋበዘ ሰው አልተገኘም።</i>")
    else:
        for idx, row in enumerate(audit_rows[:25], start=1):
            status = "✅ Active" if row["is_active"] == 1 else "❌ Left"
            lines.append(
                f"{idx}. User <code>{row['referred_user_id']}</code> | {status} | 🕒 {row['joined_at']}"
            )
        if len(audit_rows) > 25:
            lines.append(f"... እና ተጨማሪ {len(audit_rows) - 25} ተጋባዦች።")

    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot):
    """Broadcast announcement to all bot users: /broadcast <text>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    broadcast_text = message.text.partition(" ")[2].strip()
    if not broadcast_text:
        await message.answer(
            "⚠️ <b>አጠቃቀም:</b> <code>/broadcast &lt;የማስታወቂያው ጽሑፍ&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    user_ids = await db.get_all_user_ids()
    status_msg = await message.answer(
        f"🚀 ብሮድካስት በመላክ ላይ ለ <b>{len(user_ids):,}</b> ተጠቃሚዎች...",
        parse_mode=ParseMode.HTML,
    )

    success_count = 0
    fail_count = 0

    for uid in user_ids:
        try:
            await bot.send_message(
                chat_id=uid,
                text=broadcast_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            success_count += 1
            await asyncio.sleep(0.05)  # Telegram rate limit compliance
        except Exception:
            fail_count += 1

    await status_msg.edit_text(
        f"✅ <b>ብሮድካስት ተጠናቋል!</b>\n"
        f"• በተሳካ ሁኔታ የተላከላቸው: <b>{success_count:,}</b>\n"
        f"• ያልደረሳቸው/Blocked: <b>{fail_count:,}</b>",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("reset_week"))
async def cmd_reset_week(message: Message):
    """Archive winners and reset points for a new weekly cycle: /reset_week <Cycle Name>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    cycle_name = message.text.partition(" ")[2].strip() or "Week 1"
    top_winners = await db.reset_weekly_competition(cycle_name)

    lines = [
        f"🎉 <b>የሳምንቱ ውድድር ተጠናቀቀ! ({cycle_name})</b>",
        "🏆 <b>የሳምንቱ አሸናፊዎች (Archived Winners):</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    for w in top_winners:
        name = w.first_name + (f" (@{w.username})" if w.username else "")
        lines.append(f"#{w.rank} <b>{name}</b> ➜ {w.points} ተጋባዥ (ID: <code>{w.user_id}</code>)")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("✅ ነጥቦች ለቀጣዩ ሳምንት ዜሮ (Reset) ሆነዋል!")

    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)
