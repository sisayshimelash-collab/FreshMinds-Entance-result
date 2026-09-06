"""
FreshMinds University Directory — 1-Tap Formatted Campus Information
"""

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
from handlers.utils import check_channel_membership
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


def build_universities_list_keyboard(universities: list) -> InlineKeyboardMarkup:
    """Builds inline keyboard list of all available universities."""
    keyboard = []
    # 1 button per row for clean readability
    for u in universities:
        keyboard.append([
            InlineKeyboardButton(text=f"🏛️ {u.name}", callback_data=f"uni_view_{u.id}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(F.text == msg.BTN_UNIVERSITIES)
@router.message(Command("universities"))
@router.message(Command("uni"))
async def handle_universities_list(message: Message):
    """Displays the list of universities."""
    universities = await db.get_all_universities()

    if not universities:
        await message.answer(
            "🏛️ <b>የዩኒቨርሲቲዎች መረጃ ማዕከል</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<i>ይቅርታ፣ እስካሁን ምንም ዩኒቨርሲቲ አልተመዘገበም።</i>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = (
        "🏛️ <b>FreshMinds — የኢትዮጵያ ዩኒቨርሲቲዎች መረጃ ማዕከል</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ስለ ካምፓስ ህይወት፣ ዶርም፣ ካፌ፣ ተወዳጅ ዲፓርትመንቶችና ምክሮች መረጃ ለማግኘት "
        "የሚፈልጉትን ዩኒቨርሲቲ ይጫኑ:\n\n"
        f"📍 የተመዘገቡ ዩኒቨርሲቲዎች: <b>{len(universities)}</b>"
    )

    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_universities_list_keyboard(universities),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("uni_view_"))
async def handle_university_view(callback: CallbackQuery, bot: Bot):
    """Displays the complete formatted About card for the selected university with channel membership check."""
    uni_id = int(callback.data.partition("uni_view_")[2])
    uni = await db.get_university_by_id(uni_id)

    if not uni:
        await callback.answer("⚠️ ይቅርታ፣ ይህ ዩኒቨርሲቲ አልተገኘም!", show_alert=True)
        return

    # Check Channel Membership (Force-Subscription for Channel Growth)
    is_member = await check_channel_membership(bot, callback.from_user.id)
    if not is_member:
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናላችንን ይቀላቀሉ!", show_alert=True)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል (Join)",
                        url=f"https://t.me/{TARGET_CHANNEL}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ ተቀላቅያለሁ (Check & View)",
                        callback_data=f"uni_view_{uni_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 ወደ ዩኒቨርሲቲዎች ዝርዝር (Back)",
                        callback_data="uni_list_back",
                    )
                ],
            ]
        )
        lock_text = (
            f"🔒 <b>የ{uni.name}ን ሙሉ መረጃ ለማየት መጀመሪያ የቻናላችን ቤተሰብ ይሁኑ!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "ስለ ካምፓስ ህይወት፣ ዶርም፣ ካፌ፣ ተወዳጅ ዲፓርትመንቶችና የትምህርት ክፍሎች የተዘጋጀውን ዝርዝር መረጃ "
            f"ለማግኘት እባክዎ መጀመሪያ <b>@{TARGET_CHANNEL}</b> ቻናልን ይቀላቀሉ!\n\n"
            f"👇 ከታች <b>'ቻናል ተቀላቀል'</b> የሚለውን ተጭነው ከገቡ በኋላ <b>'ተቀላቅያለሁ'</b> የሚለውን ይጫኑ:"
        )
        await callback.message.edit_text(
            lock_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        return

    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 ወደ ዩኒቨርሲቲዎች ዝርዝር (Back)", callback_data="uni_list_back")]
        ]
    )

    await callback.message.edit_text(
        uni.about_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "uni_list_back")
async def handle_universities_back(callback: CallbackQuery):
    """Returns to the university list view."""
    await callback.answer()
    universities = await db.get_all_universities()

    text = (
        "🏛️ <b>FreshMinds — የኢትዮጵያ ዩኒቨርሲቲዎች መረጃ ማዕከል</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ስለ ካምፓስ ህይወት፣ ዶርም፣ ካፌ፣ ተወዳጅ ዲፓርትመንቶችና ምክሮች መረጃ ለማግኘት "
        "የሚፈልጉትን ዩኒቨርሲቲ ይጫኑ:\n\n"
        f"📍 የተመዘገቡ ዩኒቨርሲቲዎች: <b>{len(universities)}</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_universities_list_keyboard(universities),
        disable_web_page_preview=True,
    )
