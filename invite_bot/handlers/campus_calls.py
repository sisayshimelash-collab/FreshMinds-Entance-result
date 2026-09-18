"""
FreshMinds University Campus Calls (የዩኒቨርሲቲ ጥሪ) Handler
Displays official forwarded campus arrival & registration call announcements for freshman students.
"""

import html
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from database import db
from config import TARGET_CHANNEL
from handlers.utils import (
    check_and_credit_membership,
    send_feature_lock_message,
)
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


def build_campus_calls_keyboard(calls: list) -> InlineKeyboardMarkup:
    """Constructs an interactive 1-column list of universities with active campus calls."""
    buttons = []
    for c in calls:
        uni_title = f"🏛️ {c.university_name}"
        buttons.append([
            InlineKeyboardButton(text=uni_title, callback_data=f"ccall_view_{c.id}")
        ])

    buttons.append([
        InlineKeyboardButton(text="🔄 አድስ (Refresh List)", callback_data="ccall_back_list")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_campus_calls_list(target: Message | CallbackQuery):
    """Renders the list of universities that have active campus call announcements."""
    calls = await db.get_all_campus_calls()

    if not calls:
        text = (
            "📢 <b>የኢትዮጵያ ዩኒቨርሲቲዎች ጥሪ (Campus Calls)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "ℹ️ <b>እስካሁን ምንም ዩኒቨርሲቲ ጥሪ አላደረገም!</b>\n\n"
            "ዩኒቨርሲቲዎች ለ 2017/2019 ዓ.ም የ Freshman ተማሪዎች ይፋዊ የመግቢያ ጥሪ እንዳወጡ ወዲያውኑ እዚህ ይለጠፋሉ።\n\n"
            f"🔔 አዳዲስ መረጃዎችን በፍጥነት ለማግኘት ቻናላችንን @{TARGET_CHANNEL} ይከታተሉ!"
        )
        refresh_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔄 አድስ (Refresh)", callback_data="ccall_back_list")]
            ]
        )
        if isinstance(target, CallbackQuery):
            try:
                await target.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=refresh_kb)
            except Exception:
                await target.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=refresh_kb)
        else:
            await target.answer(text, parse_mode=ParseMode.HTML, reply_markup=refresh_kb)
        return

    text = (
        "📢 <b>የኢትዮጵያ ዩኒቨርሲቲዎች ጥሪ (Freshman Campus Calls)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ለ 1ኛ አመት የዩኒቨርሲቲ ተማሪዎች ይፋዊ የካምፓስ መግቢያ ጥሪ ያደረጉ ዩኒቨርሲቲዎች:\n\n"
        f"📍 የተለጠፉ ጥሪዎች: <b>{len(calls)}</b>\n\n"
        "👇 <b>የተመደቡበትን ዩኒቨርሲቲ በመምረጥ ሙሉ ማስታወቂያውን፣ መግቢያ ቀኑንና የሚያስፈልጉ ነገሮችን ይመልከቱ:</b>"
    )
    keyboard = build_campus_calls_keyboard(calls)

    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except Exception:
            await target.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await target.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.message(F.text == msg.BTN_CAMPUS_CALLS)
@router.message(Command("campus_calls"))
@router.message(Command("calls"))
async def handle_campus_calls_entry(message: Message, bot: Bot):
    """Entry point for Campus Calls button from main menu."""
    if not await db.is_campus_calls_enabled():
        await message.answer(
            "ℹ️ <b>የዩኒቨርሲቲ ጥሪ አገልግሎት በጊዜያዊነት በአድሚን ተዘግቷል!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "አገልግሎቱ በቅርቡ የሚከፈት ይሆናል።",
            parse_mode=ParseMode.HTML,
        )
        return

    if not await check_and_credit_membership(bot, message.from_user):
        await send_feature_lock_message(
            message, "📢 የዩኒቨርሲቲ ጥሪ መረጃዎችን", "retry_feature_campus_calls"
        )
        return

    await show_campus_calls_list(message)


@router.callback_query(F.data == "retry_feature_campus_calls")
async def handle_retry_campus_calls(callback: CallbackQuery, bot: Bot):
    """Retry handler after forced join."""
    if not await db.is_campus_calls_enabled():
        await callback.answer("⚠️ የዩኒቨርሲቲ ጥሪ አገልግሎት በጊዜያዊነት ተዘግቷል!", show_alert=True)
        return

    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer(f"⚠️ እባክዎ መጀመሪያ @{TARGET_CHANNEL} ቻናልን ይቀላቀሉ!", show_alert=True)
        return

    await callback.answer("✅ እናመሰግናለን! የዩኒቨርሲቲ ጥሪዎች ዝርዝር እየተከፈተ ነው...")
    await show_campus_calls_list(callback)


@router.callback_query(F.data == "ccall_back_list")
async def cb_campus_calls_back_list(callback: CallbackQuery):
    """Back button to return to the list of universities."""
    await callback.answer()
    try:
        if callback.message.photo:
            await callback.message.delete()
            await show_campus_calls_list(callback.message)
            return
    except Exception:
        pass
    await show_campus_calls_list(callback)


@router.callback_query(F.data.startswith("ccall_view_"))
async def cb_view_single_call(callback: CallbackQuery, bot: Bot):
    """Renders single university campus call announcement with photo & caption."""
    call_id_str = callback.data.partition("ccall_view_")[2]
    if not call_id_str.isdigit():
        return

    await callback.answer()
    call = await db.get_campus_call_by_id(int(call_id_str))
    if not call:
        await callback.answer("⚠️ ይቅርታ፣ ይህ ማስታወቂያ አልተገኘም ወይም ተሰርዟል!", show_alert=True)
        return

    nav_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Back to Universities (ወደ ዝርዝሩ ተመለስ)",
                    callback_data="ccall_back_list",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 ቻናላችንን ተቀላቀሉ (Join Channel)",
                    url=f"https://t.me/{TARGET_CHANNEL}",
                )
            ],
        ]
    )

    caption_body = call.caption or "<i>ምንም ተጨማሪ ጽሑፍ አልተያያዘም።</i>"
    header = (
        f"📢 <b>ይፋዊ የካምፓስ ጥሪ ማስታወቂያ — {html.escape(call.university_name)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    footer = (
        "\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ <i>FreshMinds Academy • @{TARGET_CHANNEL}</i>"
    )

    full_text = f"{header}{caption_body}{footer}"

    # If photo exists
    if call.photo_file_id:
        try:
            await callback.message.delete()
        except Exception:
            pass

        if len(full_text) <= 1024:
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=call.photo_file_id,
                caption=full_text,
                parse_mode=ParseMode.HTML,
                reply_markup=nav_keyboard,
            )
        else:
            photo_caption = f"{header}<i>(ሙሉ ዝርዝር ከታች ተያይዟል 👇)</i>"
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=call.photo_file_id,
                caption=photo_caption,
                parse_mode=ParseMode.HTML,
            )
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=full_text,
                parse_mode=ParseMode.HTML,
                reply_markup=nav_keyboard,
            )
    else:
        # Text-only announcement
        try:
            await callback.message.edit_text(
                full_text,
                parse_mode=ParseMode.HTML,
                reply_markup=nav_keyboard,
                disable_web_page_preview=True,
            )
        except Exception:
            await callback.message.answer(
                full_text,
                parse_mode=ParseMode.HTML,
                reply_markup=nav_keyboard,
                disable_web_page_preview=True,
            )
