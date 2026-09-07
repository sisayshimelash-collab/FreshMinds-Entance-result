import asyncio
import html
import logging
import re
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import db
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()


class AdminUniState(StatesGroup):
    waiting_for_name = State()
    waiting_for_about = State()


class AdminUniEditState(StatesGroup):
    waiting_for_new_about = State()


class AdminCourseState(StatesGroup):
    waiting_for_name = State()


class AdminMaterialState(StatesGroup):
    waiting_for_course = State()
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_file = State()
    waiting_for_batch_files = State()


CATEGORY_NAMES = {
    "module": "📖 Official Module (PDF)",
    "note": "📝 Summary Notes & Handouts",
    "midterm": "📑 Midterm Exam Bank",
    "final": "🎯 Final Exam Bank",
    "video": "🎥 Video Tutorial / Link",
}


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
                    text="🏛️ Manage Universities", callback_data="admin_unis_menu"
                ),
                InlineKeyboardButton(
                    text="📚 Courses & Materials", callback_data="admin_courses_menu"
                ),
            ],
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
                InlineKeyboardButton(
                    text="📢 Broadcast", callback_data="admin_hint_bc"
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
        display_name = html.escape(u.first_name)
        if u.username:
            user_link = f'<b>{display_name}</b> (<a href="https://t.me/{u.username}">@{u.username}</a>)'
        else:
            user_link = f'<b><a href="tg://user?id={u.user_id}">{display_name}</a></b>'
        lines.append(
            f"{medals.get(u.rank, '#')} {user_link} ➜ <b>{u.points}</b> pts (ID: <code>{u.user_id}</code>)"
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
        display_name = html.escape(u['first_name'])
        if u['username']:
            uname = f'<a href="https://t.me/{u["username"]}">@{u["username"]}</a>'
        else:
            uname = f'<a href="tg://user?id={u["user_id"]}">No @username</a>'
        lines.append(
            f"{idx}. <b>{display_name}</b> ({uname}) | ID: <code>{u['user_id']}</code> | <b>{u['active_points']}</b> pts"
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


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel any active admin FSM state: /cancel"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "ℹ️ <b>ምንም ንቁ ሂደት የለም።</b> (/cancel)",
            parse_mode=ParseMode.HTML,
        )
        return
    await state.clear()
    await message.answer(
        "✅ <b>ሂደቱ ተሰርዟል (Cancelled).</b>\n"
        "ወደ <code>/admin</code> ይመለሱ።",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("reset_week"))
async def cmd_reset_week(message: Message):
    """Archive top winners and reset competition: /reset_week <cycle_name>"""
    user = message.from_user
    if not user or not is_admin(user.id):
        return

    cycle_name = message.text.partition(" ")[2].strip()
    if not cycle_name:
        await message.answer(
            "⚠️ <b>Usage:</b> <code>/reset_week &lt;Cycle Name&gt;</code>\n"
            "Example: <code>/reset_week Week 1</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Show confirmation before the destructive reset
    top_users = await db.get_top_leaderboard(limit=4)
    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🎖️"}
    preview_lines = [f"🔄 <b>Reset Confirmation: '{html.escape(cycle_name)}'</b>"]
    preview_lines.append("━━━━━━━━━━━━━━━━━━━━")
    preview_lines.append("<b>Current Top 4 (will be archived):</b>")
    if top_users:
        for u in top_users:
            preview_lines.append(
                f"{medals.get(u.rank, '#')} <b>{html.escape(u.first_name)}</b> "
                f"(ID: <code>{u.user_id}</code>) ➜ <b>{u.points}</b> pts"
            )
    else:
        preview_lines.append("<i>No referrals yet.</i>")
    preview_lines.append("━━━━━━━━━━━━━━━━━━━━")
    preview_lines.append(
        "⚠️ <b>ማስጠንቀቂያ:</b> ይህ ድርጊት ሁሉንም ነጥቦች ያጠፋል እና ወደ ኋላ መመለስ አይቻልም!"
    )

    import urllib.parse
    safe_cycle = urllib.parse.quote(cycle_name)
    confirm_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ አዎ፣ አሁን Reset አድርግ!",
                    callback_data=f"admin_reset_confirm_{safe_cycle}",
                ),
                InlineKeyboardButton(
                    text="❌ ሰርዝ (Cancel)",
                    callback_data="admin_reset_abort",
                ),
            ]
        ]
    )
    await message.answer(
        "\n".join(preview_lines),
        parse_mode=ParseMode.HTML,
        reply_markup=confirm_markup,
    )


@router.callback_query(F.data.startswith("admin_reset_confirm_"))
async def cb_admin_reset_confirm(callback: CallbackQuery):
    """Execute the weekly competition reset after admin confirms."""
    if not is_admin(callback.from_user.id):
        return
    import urllib.parse
    safe_cycle = callback.data.partition("admin_reset_confirm_")[2]
    cycle_name = urllib.parse.unquote(safe_cycle)

    await callback.answer("⏳ Reset በሂደት ላይ...", show_alert=False)

    top_winners = await db.reset_weekly_competition(cycle_name)
    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🎖️"}
    lines = [
        f"🏆 <b>'{html.escape(cycle_name)}' ተጠናቋል — ውጤቶች ተቀምጠዋል!</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        "<b>Archived Winners:</b>",
    ]
    if top_winners:
        for w in top_winners:
            lines.append(
                f"{medals.get(w.rank, '#')} <b>{html.escape(w.first_name)}</b> "
                f"(ID: <code>{w.user_id}</code>) ➜ <b>{w.points}</b> pts"
            )
    else:
        lines.append("<i>No winners this cycle.</i>")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("✅ ሁሉም ነጥቦች ተሰርዘዋል — አዲስ ሳምንት ጀምሯል!")

    try:
        await callback.message.edit_text(
            "\n".join(lines), parse_mode=ParseMode.HTML
        )
    except Exception:
        await callback.message.answer("\n".join(lines), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "admin_reset_abort")
async def cb_admin_reset_abort(callback: CallbackQuery):
    """Abort the reset operation."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer("❌ Reset ተሰርዟል።", show_alert=True)
    try:
        await callback.message.delete()
    except Exception:
        pass




# ── Universities Management CMS ──────────────────────────────────────────────


@router.callback_query(F.data == "admin_unis_menu")
async def cb_admin_unis_menu(callback: CallbackQuery):
    """University management menu."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    universities = await db.get_all_universities()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add New University", callback_data="admin_add_uni")],
            [InlineKeyboardButton(text="📋 View & Copy Description", callback_data="admin_copy_uni_list")],
            [InlineKeyboardButton(text="✏️ Edit University", callback_data="admin_edit_uni_list")],
            [InlineKeyboardButton(text="🗑️ Delete a University", callback_data="admin_del_uni_list")],
            [InlineKeyboardButton(text="🔙 Back to Admin Menu", callback_data="admin_back_main")],
        ]
    )

    text = (
        "🏛️ <b>University Directory Management</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Currently Registered Universities: <b>{len(universities)}</b>\n\n"
        "You can add a new university by sending its Name and formatted About text, or delete existing ones."
    )
    await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.callback_query(F.data == "admin_add_uni")
async def cb_admin_add_uni(callback: CallbackQuery, state: FSMContext):
    """Start university creation flow."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    await state.set_state(AdminUniState.waiting_for_name)
    await callback.message.answer(
        "🏛️ <b>Step 1/2: Enter University Name</b>\n\n"
        "Please send the name of the university (e.g. <code>Bahir Dar University (BDU)</code>):",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminUniState.waiting_for_name)
async def state_admin_uni_name(message: Message, state: FSMContext):
    """Receive university name."""
    if not is_admin(message.from_user.id):
        return
    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(AdminUniState.waiting_for_about)
    await message.answer(
        f"🏛️ <b>Step 2/2: Send About Text for {name}</b>\n\n"
        "Send or paste the complete formatted guide/about text (supports HTML formatting, links, bold, bullet points):\n\n"
        "<i>(Tip: You can include location, dorm/cafe info, cutoffs, and group link in this single message)</i>",
        parse_mode=ParseMode.HTML,
    )


def _extract_admin_formatted_text(message: Message) -> str:
    """
    Extract formatted text preserving both:
    1) Raw HTML tags if the admin pasted raw HTML text (<b>, <i>, etc.)
    2) Telegram client rich-text entities (converted via message.html_text)
    """
    raw_text = message.text or ""
    has_html_tags = bool(re.search(r"<\/?(b|i|u|s|code|pre|a|blockquote)\b", raw_text, re.IGNORECASE))
    if has_html_tags and not message.entities:
        return raw_text
    return getattr(message, "html_text", None) or raw_text


@router.message(AdminUniState.waiting_for_about)
async def state_admin_uni_about(message: Message, state: FSMContext):
    """Receive university about text and save to DB."""
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    name = data["name"]
    about_text = _extract_admin_formatted_text(message)

    await db.add_university(name, about_text)
    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏛️ View Universities Menu", callback_data="admin_unis_menu")],
            [InlineKeyboardButton(text="👑 Admin Menu", callback_data="admin_back_main")],
        ]
    )
    await message.answer(
        f"✅ <b>Successfully Added University:</b>\n\n<b>{name}</b>\n\n"
        "Students can now browse and view this university from the bot menu!",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "admin_del_uni_list")
async def cb_admin_del_uni_list(callback: CallbackQuery):
    """List universities with delete buttons."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    universities = await db.get_all_universities()

    if not universities:
        await callback.message.answer("<i>No universities to delete.</i>", parse_mode=ParseMode.HTML)
        return

    keyboard = []
    for u in universities:
        keyboard.append([
            InlineKeyboardButton(text=f"🗑️ Delete: {u.name}", callback_data=f"admin_del_uni_do_{u.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_unis_menu")])

    await callback.message.answer(
        "🗑️ <b>Select a University to Delete:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("admin_del_uni_do_"))
async def cb_admin_del_uni_do(callback: CallbackQuery):
    """Confirm deletion of university."""
    if not is_admin(callback.from_user.id):
        return
    uni_id = int(callback.data.partition("admin_del_uni_do_")[2])
    await db.delete_university(uni_id)
    await callback.answer("✅ University deleted!", show_alert=True)
    await cb_admin_unis_menu(callback)


# ── View & Copy University Description Flow ───────────────────────────

@router.callback_query(F.data == "admin_copy_uni_list")
async def cb_admin_copy_uni_list(callback: CallbackQuery):
    """List all universities for viewing and copying full description."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    universities = await db.get_all_universities()

    if not universities:
        await callback.message.answer("<i>No universities found.</i>", parse_mode=ParseMode.HTML)
        return

    keyboard = []
    for u in universities:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📋 {u.name}",
                callback_data=f"admin_copy_uni_do_{u.id}",
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_unis_menu")])

    await callback.message.answer(
        "📋 <b>Select a University to View & Copy Full Description:</b>\n"
        "<i>Tap any university below to get its full description formatted in a 1-tap copy box.</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("admin_copy_uni_do_"))
async def cb_admin_copy_uni_do(callback: CallbackQuery):
    """Send the full university description in a 1-tap copyable code box."""
    if not is_admin(callback.from_user.id):
        return
    uni_id = int(callback.data.partition("admin_copy_uni_do_")[2])
    uni = await db.get_university_by_id(uni_id)
    if not uni:
        await callback.answer("⚠️ University not found!", show_alert=True)
        return
    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"✏️ Edit {uni.name}", callback_data=f"admin_edit_uni_do_{uni.id}")],
            [InlineKeyboardButton(text="📋 Copy Another University", callback_data="admin_copy_uni_list")],
            [InlineKeyboardButton(text="🏛️ Universities Menu", callback_data="admin_unis_menu")],
        ]
    )

    header = (
        f"🏛️ <b>{html.escape(uni.name)} — Full Description</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👇 <b>Tap the box below to copy the complete text (1-tap copy):</b>\n\n"
    )
    copy_box = f"<pre><code>{html.escape(uni.about_text)}</code></pre>"
    full_msg = header + copy_box

    if len(full_msg) <= 4000:
        await callback.message.answer(
            full_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    else:
        await callback.message.answer(header, parse_mode=ParseMode.HTML)
        await callback.message.answer(
            copy_box,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )


# ── Edit University Flow ──────────────────────────────────────────────

@router.callback_query(F.data == "admin_edit_uni_list")
async def cb_admin_edit_uni_list(callback: CallbackQuery):
    """List all universities with edit buttons."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    universities = await db.get_all_universities()

    if not universities:
        await callback.message.answer("<i>No universities to edit.</i>", parse_mode=ParseMode.HTML)
        return

    keyboard = []
    for u in universities:
        keyboard.append([
            InlineKeyboardButton(
                text=f"✏️ {u.name}",
                callback_data=f"admin_edit_uni_do_{u.id}",
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_unis_menu")])

    await callback.message.answer(
        "✏️ <b>Select a University to Edit:</b>\n"
        "<i>You will receive the full current text in a 1-tap copy box to easily copy, edit, and send back.</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("admin_edit_uni_do_"))
async def cb_admin_edit_uni_do(callback: CallbackQuery, state: FSMContext):
    """Show full copyable about text and prompt admin to send new text."""
    if not is_admin(callback.from_user.id):
        return
    uni_id = int(callback.data.partition("admin_edit_uni_do_")[2])
    uni = await db.get_university_by_id(uni_id)
    if not uni:
        await callback.answer("⚠️ University not found!", show_alert=True)
        return

    await state.update_data(edit_uni_id=uni_id, edit_uni_name=uni.name)
    await state.set_state(AdminUniEditState.waiting_for_new_about)
    await callback.answer()

    header = (
        f"✏️ <b>Editing: {html.escape(uni.name)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📋 <b>Current Full Description:</b>\n"
        "<i>👇 Tap the code box below to copy the complete text to your clipboard. Then paste it into your chat box, edit whatever you need, and send it back!</i>\n\n"
    )
    copy_box = f"<pre><code>{html.escape(uni.about_text)}</code></pre>"
    footer = "\n\n📝 <i>Send the new text when ready, or type /cancel to abort without saving.</i>"

    full_msg = header + copy_box + footer
    if len(full_msg) <= 4000:
        await callback.message.answer(full_msg, parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer(header, parse_mode=ParseMode.HTML)
        await callback.message.answer(copy_box, parse_mode=ParseMode.HTML)
        await callback.message.answer(footer, parse_mode=ParseMode.HTML)


@router.message(AdminUniEditState.waiting_for_new_about)
async def state_admin_uni_edit_about(message: Message, state: FSMContext):
    """Receive new about text and update university in DB."""
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    uni_id = data["edit_uni_id"]
    uni_name = data["edit_uni_name"]

    new_about = _extract_admin_formatted_text(message)

    updated = await db.update_university(uni_id, new_about)
    await state.clear()

    if updated:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Edit Another University", callback_data="admin_edit_uni_list")],
                [InlineKeyboardButton(text="🏙️ Universities Menu", callback_data="admin_unis_menu")],
                [InlineKeyboardButton(text="👑 Admin Menu", callback_data="admin_back_main")],
            ]
        )
        await message.answer(
            f"✅ <b>Successfully Updated:</b> <b>{html.escape(uni_name)}</b>\n\n"
            "Students will see the updated information immediately.",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            f"⚠️ <b>Update failed</b> — university ID {uni_id} not found in database.",
            parse_mode=ParseMode.HTML,
        )


# ── Courses & Materials Management CMS ───────────────────────────────────────


@router.callback_query(F.data == "admin_courses_menu")
async def cb_admin_courses_menu(callback: CallbackQuery):
    """Courses & materials management menu."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    courses = await db.get_all_courses()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add New Course", callback_data="admin_add_course")],
            [InlineKeyboardButton(text="📤 Upload Material (PDF / Notes)", callback_data="admin_upload_mat")],
            [InlineKeyboardButton(text="🗑️ Delete a Course", callback_data="admin_del_course_list")],
            [InlineKeyboardButton(text="🔙 Back to Admin Menu", callback_data="admin_back_main")],
        ]
    )

    text = (
        "📚 <b>Courses & Materials Management</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Currently Registered Courses: <b>{len(courses)}</b>\n\n"
        "Select an action to add courses, upload PDF modules/handouts, or delete courses."
    )
    await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.callback_query(F.data == "admin_add_course")
async def cb_admin_add_course(callback: CallbackQuery, state: FSMContext):
    """Start course creation flow."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    await state.set_state(AdminCourseState.waiting_for_name)
    await callback.message.answer(
        "📚 <b>Add New Course</b>\n\n"
        "Please send the name of the course (e.g. <code>Applied Mathematics II</code>):",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminCourseState.waiting_for_name)
async def state_admin_course_name(message: Message, state: FSMContext):
    """Receive course name and create course."""
    if not is_admin(message.from_user.id):
        return
    name = message.text.strip()
    await db.add_course(name)
    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Courses Menu", callback_data="admin_courses_menu")],
            [InlineKeyboardButton(text="👑 Admin Menu", callback_data="admin_back_main")],
        ]
    )
    await message.answer(
        f"✅ <b>Successfully Added Course:</b> <code>{name}</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "admin_upload_mat")
async def cb_admin_upload_mat(callback: CallbackQuery):
    """Select course for uploading material."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    courses = await db.get_all_courses()

    if not courses:
        await callback.message.answer("<i>No courses available. Please add a course first.</i>", parse_mode=ParseMode.HTML)
        return

    keyboard = []
    for c in courses:
        keyboard.append([
            InlineKeyboardButton(text=f"{c.icon} {c.name}", callback_data=f"admat_c_{c.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_courses_menu")])

    await callback.message.answer(
        "📤 <b>Select Course to Upload Material To:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("admat_c_"))
async def cb_admin_upload_select_course(callback: CallbackQuery, state: FSMContext):
    """Select category for material."""
    if not is_admin(callback.from_user.id):
        return
    course_id = int(callback.data.partition("admat_c_")[2])
    await state.update_data(course_id=course_id)
    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Official Module (PDF)", callback_data="admat_cat_module")],
            [InlineKeyboardButton(text="📝 Summary Notes & Handouts", callback_data="admat_cat_note")],
            [InlineKeyboardButton(text="📑 Midterm Exam Bank", callback_data="admat_cat_midterm")],
            [InlineKeyboardButton(text="🎯 Final Exam Bank", callback_data="admat_cat_final")],
            [InlineKeyboardButton(text="🎥 Video Tutorial / Link", callback_data="admat_cat_video")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_upload_mat")],
        ]
    )

    await callback.message.answer(
        "📁 <b>Select Category for this Material:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


def extract_material_title(message: Message, fallback_num: int = 1) -> str:
    """Extracts a clean, human-friendly title from a forwarded or uploaded message."""
    # 1. Check caption
    if message.caption and message.caption.strip():
        caption_lines = [l.strip() for l in message.caption.strip().split("\n") if l.strip()]
        if caption_lines:
            first_line = caption_lines[0]
            if len(first_line) > 2:
                return first_line[:120]

    # 2. Check document file_name
    if message.document and message.document.file_name:
        fname = message.document.file_name.strip()
        for ext in [".pdf", ".PDF", ".docx", ".DOCX", ".doc", ".DOC", ".pptx", ".PPTX", ".ppt", ".zip"]:
            if fname.endswith(ext):
                fname = fname[:-len(ext)]
                break
        clean_name = fname.replace("_", " ").strip()
        if clean_name:
            return clean_name[:120]

    # 3. Check video file_name
    if message.video and message.video.file_name:
        vname = message.video.file_name.strip()
        for ext in [".mp4", ".MP4", ".mkv", ".MKV", ".avi"]:
            if vname.endswith(ext):
                vname = vname[:-len(ext)]
                break
        clean_name = vname.replace("_", " ").strip()
        if clean_name:
            return clean_name[:120]

    # 4. Check audio title / file_name
    if message.audio:
        if message.audio.title:
            return message.audio.title.strip()[:120]
        if message.audio.file_name:
            aname = message.audio.file_name.strip()
            for ext in [".mp3", ".MP3", ".m4a", ".ogg"]:
                if aname.endswith(ext):
                    aname = aname[:-len(ext)]
                    break
            return aname.replace("_", " ").strip()[:120]

    # 5. Check text link
    if message.text:
        text = message.text.strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if len(lines) > 1 and not (lines[0].startswith("http://") or lines[0].startswith("https://")):
            return lines[0][:120]
        return text[:120]

    return f"Material #{fallback_num}"


async def finish_batch_upload(chat_id: int, state: FSMContext, bot: Bot):
    """Finalizes batch upload, clears state, and shows uploaded summary."""
    data = await state.get_data()
    course_id = data.get("course_id")
    category = data.get("category")
    batch_count = data.get("batch_count", 0)
    uploaded_titles = data.get("uploaded_titles", [])

    await state.clear()

    course = await db.get_course_by_id(course_id) if course_id else None
    c_name = course.name if course else "Course"
    cat_title = CATEGORY_NAMES.get(category, category.capitalize() if category else "Category")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Upload More (ሌላ ማቴሪያል ጫን)", callback_data="admin_upload_mat")],
            [InlineKeyboardButton(text="📚 Courses Menu", callback_data="admin_courses_menu")],
            [InlineKeyboardButton(text="👑 Admin Menu", callback_data="admin_back_main")],
        ]
    )

    if batch_count == 0:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"ℹ️ <b>Upload Finished:</b> No new files were added.\n\n"
                f"• Course: <b>{c_name}</b>\n"
                f"• Category: <b>{cat_title}</b>"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
        return

    titles_preview = "\n".join([f"  • {html.escape(t)}" for t in uploaded_titles[:10]])
    if len(uploaded_titles) > 10:
        titles_preview += f"\n  <i>...and {len(uploaded_titles) - 10} more</i>"

    await bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 <b>Batch Upload Successfully Completed!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"• Course: <b>{c_name}</b>\n"
            f"• Category: <b>{cat_title}</b>\n"
            f"• Total Added: <b>{batch_count} files/links</b>\n\n"
            f"📋 <b>Saved Materials:</b>\n{titles_preview}\n\n"
            f"✨ Students can now reveal and download all {batch_count} materials instantly from the bot!"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("admat_cat_"))
async def cb_admin_upload_select_category(callback: CallbackQuery, state: FSMContext):
    """Start batch upload / continuous forwarding mode for materials."""
    if not is_admin(callback.from_user.id):
        return
    category = callback.data.partition("admat_cat_")[2]
    data = await state.get_data()
    course_id = data.get("course_id")

    course = await db.get_course_by_id(course_id) if course_id else None
    c_name = course.name if course else "Course"
    cat_title = CATEGORY_NAMES.get(category, category.capitalize())

    await state.update_data(category=category, batch_count=0, uploaded_titles=[])
    await state.set_state(AdminMaterialState.waiting_for_batch_files)
    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Finished Uploading (ጨርሻለሁ)", callback_data="admat_done_batch")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_courses_menu")],
        ]
    )

    await callback.message.answer(
        f"📥 <b>Forward / Upload Mode Activated!</b>\n\n"
        f"• Course: <b>{c_name}</b>\n"
        f"• Category: <b>{cat_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>You can now forward as many PDFs, exams, or documents as you want!</b>\n\n"
        f"💡 <i>How it works:</i>\n"
        f"1️⃣ <b>Forward directly from your channel</b> (or chats/saved messages).\n"
        f"2️⃣ Or attach and upload PDFs/documents here.\n"
        f"3️⃣ You can also send Google Drive / YouTube links as text.\n"
        f"4️⃣ The title will be automatically extracted from the file name or caption.\n\n"
        f"👉 When you are done forwarding all files, tap <b>'✅ Finished Uploading (ጨርሻለሁ)'</b> below or send <code>/done</code>.",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "admat_done_batch")
async def cb_admin_mat_done(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Handles 'Finished Uploading' button click."""
    await callback.answer()
    await finish_batch_upload(callback.message.chat.id, state, bot)


@router.message(AdminMaterialState.waiting_for_batch_files, Command("done"))
async def state_admin_mat_done_cmd(message: Message, state: FSMContext, bot: Bot):
    """Handles /done command to finish batch upload."""
    await finish_batch_upload(message.chat.id, state, bot)


@router.message(AdminMaterialState.waiting_for_batch_files)
async def state_admin_mat_batch_files(message: Message, state: FSMContext):
    """Continuously receives forwarded or uploaded files/links for the selected course and category."""
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    course_id = data.get("course_id")
    category = data.get("category")
    batch_count = data.get("batch_count", 0)
    uploaded_titles = data.get("uploaded_titles", [])

    if not course_id or not category:
        await state.clear()
        await message.answer("⚠️ Session expired. Please start upload again from /admin.")
        return

    file_id = None
    external_url = None

    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.text and (message.text.startswith("http://") or message.text.startswith("https://")):
        external_url = message.text.strip()
    elif message.text and ("http://" in message.text or "https://" in message.text):
        for word in message.text.split():
            if word.startswith("http://") or word.startswith("https://"):
                external_url = word
                break

    if not file_id and not external_url:
        await message.answer(
            "⚠️ Please forward a PDF/Document, video, audio, or send a valid URL.\n"
            "If you have finished uploading, tap <b>'✅ Finished Uploading'</b> below or send <code>/done</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Extract title automatically
    title = extract_material_title(message, fallback_num=batch_count + 1)

    await db.add_material(
        course_id=course_id,
        category=category,
        title=title,
        file_id=file_id,
        external_url=external_url,
    )

    batch_count += 1
    uploaded_titles.append(title)
    await state.update_data(batch_count=batch_count, uploaded_titles=uploaded_titles)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ Finished Uploading ({batch_count} saved)", callback_data="admat_done_batch")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_courses_menu")],
        ]
    )

    await message.reply(
        f"✅ <b>[#{batch_count}] Saved:</b> <code>{html.escape(title)}</code>\n"
        f"<i>Keep forwarding more files, or tap Finished when done.</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "admin_del_course_list")
async def cb_admin_del_course_list(callback: CallbackQuery):
    """List courses with delete buttons."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    courses = await db.get_all_courses()

    if not courses:
        await callback.message.answer("<i>No courses to delete.</i>", parse_mode=ParseMode.HTML)
        return

    keyboard = []
    for c in courses:
        keyboard.append([
            InlineKeyboardButton(text=f"🗑️ Delete: {c.name}", callback_data=f"admin_del_course_do_{c.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_courses_menu")])

    await callback.message.answer(
        "🗑️ <b>Select a Course to Delete:</b>\n<i>(Warning: Deleting a course will also remove all its materials)</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("admin_del_course_do_"))
async def cb_admin_del_course_do(callback: CallbackQuery):
    """Confirm deletion of course."""
    if not is_admin(callback.from_user.id):
        return
    course_id = int(callback.data.partition("admin_del_course_do_")[2])
    await db.delete_course(course_id)
    await callback.answer("✅ Course deleted!", show_alert=True)
    await cb_admin_courses_menu(callback)


@router.callback_query(F.data == "admin_back_main")
async def cb_admin_back_main(callback: CallbackQuery):
    """Returns to the main admin control panel."""
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
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
    await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_admin_menu_markup())
