"""
FreshMinds Invite Competition Bot — Comprehensive Admin Control Center
"""

import asyncio
import logging
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from database import db
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user ID is authorized as Admin."""
    if not ADMIN_IDS:
        return True  # If empty in dev, allow
    return user_id in ADMIN_IDS


def get_admin_menu_markup() -> InlineKeyboardMarkup:
    """Interactive Admin Panel Keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Campaign Stats", callback_data="admin_stats"
                ),
                InlineKeyboardButton(
                    text="🏆 Top 4 Leaders", callback_data="admin_top"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 List Participants", callback_data="admin_users"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="➕ Add Points: /add_points",
                    callback_data="admin_hint_add",
                ),
                InlineKeyboardButton(
                    text="➖ Remove: /remove_points",
                    callback_data="admin_hint_sub",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Audit: /audit <id>",
                    callback_data="admin_hint_audit",
                ),
                InlineKeyboardButton(
                    text="📢 Broadcast: /broadcast",
                    callback_data="admin_hint_bc",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Reset Week: /reset_week",
                    callback_data="admin_hint_reset",
                ),
            ],
        ]
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Open interactive Admin Control Center: /admin"""
    user = message.from_user
    if not user:
        return

    if not is_admin(user.id):
        await message.answer(
            f"⚠️ <b>Access Denied (የአድሚን ፍቃድ የለዎትም)</b>\n\n"
            f"👤 Your Telegram User ID: <code>{user.id}</code>\n\n"
            f"💡 To enable Admin access, add your ID to <code>ADMIN_IDS={user.id}</code> inside <code>invite_bot/.env</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    text = (
        "👑 <b>FreshMinds Invite Bot — Admin Control Center</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Select an action or use direct commands:\n\n"
        "• <code>/admin_stats</code> ➜ View global growth analytics\n"
        "• <code>/audit &lt;user_id&gt;</code> ➜ View a user's invited members\n"
        "• <code>/add_points &lt;user_id&gt; &lt;points&gt;</code> ➜ Add manual bonus\n"
        "• <code>/remove_points &lt;user_id&gt; &lt;points&gt;</code> ➜ Deduct points\n"
        "• <code>/broadcast &lt;text&gt;</code> ➜ Send announcement to all\n"
        "• <code>/reset_week &lt;name&gt;</code> ➜ Archive Top 4 and reset"
    )
    await message.answer(
        text, parse_mode=ParseMode.HTML, reply_markup=get_admin_menu_markup()
    )


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Callback for admin stats."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    total_users, total_joins, active_joins = await db.get_total_campaign_stats()
    churn_rate = (
        ((total_joins - active_joins) / total_joins * 100) if total_joins > 0 else 0
    )

    text = (
        "📈 <b>FreshMinds Campaign Analytics</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 የተመዘገቡ ተሳታፊዎች (Bot Users): <b>{total_users:,}</b>\n"
        f"🚀 አጠቃላይ የተገኙ ሰብስክራይበሮች (Total Joins): <b>{total_joins:,}</b>\n"
        f"✅ ንቁ ሰብስክራይበሮች (Active in Channel): <b>{active_joins:,}</b>\n"
        f"📉 የለቀቁ (Left/Churned): <b>{total_joins - active_joins:,} ({churn_rate:.1f}%)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await callback.message.answer(
        text, parse_mode=ParseMode.HTML, reply_markup=get_admin_menu_markup()
    )


@router.callback_query(F.data == "admin_top")
async def cb_admin_top(callback: CallbackQuery):
    """Callback for Top 4 leaders."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    top_users = await db.get_top_leaderboard(limit=4)
    lines = [
        "🏆 <b>Top 4 Competition Leaders:</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]
    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🎖️"}
    for u in top_users:
        name = u.first_name + (f" (@{u.username})" if u.username else "")
        lines.append(
            f"{medals.get(u.rank, '#')} <b>{name}</b> ➜ <b>{u.points}</b> pts (ID: <code>{u.user_id}</code>)"
        )
    if not top_users:
        lines.append("<i>No referrals yet.</i>")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    await callback.message.answer(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_menu_markup(),
    )


@router.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery):
    """Callback to list participants."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    users = await db.list_all_participants(limit=25)
    lines = [
        f"👥 <b>Latest Registered Participants ({len(users)}):</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]
    for idx, u in enumerate(users, start=1):
        uname = f"@{u['username']}" if u["username"] else "No @username"
        lines.append(
            f"{idx}. <b>{u['first_name']}</b> ({uname}) | ID: <code>{u['user_id']}</code> | <b>{u['active_points']}</b> pts"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    await callback.message.answer(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_menu_markup(),
    )


@router.callback_query(F.data.startswith("admin_hint_"))
async def cb_admin_hints(callback: CallbackQuery):
    """Helpful prompts when tapping command buttons."""
    hints = {
        "admin_hint_add": "💡 To add points: Send <code>/add_points &lt;user_id&gt; &lt;points&gt;</code> (e.g. <code>/add_points 12345678 5</code>)",
        "admin_hint_sub": "💡 To deduct points: Send <code>/remove_points &lt;user_id&gt; &lt;points&gt;</code> (e.g. <code>/remove_points 12345678 2</code>)",
        "admin_hint_audit": "💡 To audit a user: Send <code>/audit &lt;user_id&gt;</code> (e.g. <code>/audit 12345678</code>)",
        "admin_hint_bc": "💡 To broadcast: Send <code>/broadcast &lt;Your Announcement Text&gt;</code>",
        "admin_hint_reset": "💡 To reset weekly competition: Send <code>/reset_week Week 1</code>",
    }
    hint_text = hints.get(callback.data, "Use the command directly in chat.")
    await callback.answer(hint_text, show_alert=True)


# ── Direct Admin Commands ────────────────────────────────────────────────────


@router.message(Command("add_points"))
async def cmd_add_points(message: Message):
    """Add points manually: /add_points <user_id> <points>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    args = message.text.split()
    if len(args) < 3 or not args[1].isdigit() or not args[2].isdigit():
        await message.answer(
            "⚠️ <b>Usage:</b> <code>/add_points &lt;user_id&gt; &lt;points&gt;</code>\nExample: <code>/add_points 12345678 5</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    target_id = int(args[1])
    points = int(args[2])

    new_total = await db.add_manual_points(target_id, points)
    await message.answer(
        f"✅ <b>Successfully added +{points} points to user <code>{target_id}</code>!</b>\nNew Active Total: <b>{new_total}</b> points.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("remove_points"))
async def cmd_remove_points(message: Message):
    """Deduct points manually: /remove_points <user_id> <points>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    args = message.text.split()
    if len(args) < 3 or not args[1].isdigit() or not args[2].isdigit():
        await message.answer(
            "⚠️ <b>Usage:</b> <code>/remove_points &lt;user_id&gt; &lt;points&gt;</code>\nExample: <code>/remove_points 12345678 2</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    target_id = int(args[1])
    points = int(args[2])

    new_total = await db.remove_manual_points(target_id, points)
    await message.answer(
        f"✅ <b>Successfully deducted -{points} points from user <code>{target_id}</code>!</b>\nNew Active Total: <b>{new_total}</b> points.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("admin_stats"))
async def cmd_admin_stats(message: Message):
    """View global campaign growth analytics: /admin_stats"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    total_users, total_joins, active_joins = await db.get_total_campaign_stats()
    churn_rate = (
        ((total_joins - active_joins) / total_joins * 100) if total_joins > 0 else 0
    )

    text = (
        "📈 <b>FreshMinds Campaign Analytics</b>\n"
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
    """Audit a specific user's referrals: /audit <user_id>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer(
            "⚠️ <b>Usage:</b> <code>/audit &lt;user_id&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
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
            "⚠️ <b>Usage:</b> <code>/broadcast &lt;Announcement Text&gt;</code>",
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
            await asyncio.sleep(0.05)
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
    """Archive Top 4 winners and reset points: /reset_week <Cycle Name>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    cycle_name = message.text.partition(" ")[2].strip() or "Week 1"
    top_winners = await db.reset_weekly_competition(cycle_name)

    lines = [
        f"🎉 <b>የሳምንቱ ውድድር ተጠናቀቀ! ({cycle_name})</b>",
        "🏆 <b>የሳምንቱ ከፍተኛ 4 አሸናፊዎች (Archived Winners):</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🎖️"}
    for w in top_winners:
        name = w.first_name + (f" (@{w.username})" if w.username else "")
        medal = medals.get(w.rank, f"#{w.rank}")
        lines.append(
            f"{medal} <b>{name}</b> ➜ <b>{w.points}</b> ተጋባዥ (ID: <code>{w.user_id}</code>)"
        )

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("✅ ነጥቦች ለቀጣዩ ሳምንት ዜሮ (Reset) ሆነዋል!")

    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)
