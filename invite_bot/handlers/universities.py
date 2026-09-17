"""
FreshMinds University Directory & 1st Semester Course Guide Handler
Source of Fact: FreshMinds_Academy_Freshman_Course_Guide.md
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
from university_courses_data import (
    get_all_university_names,
    find_university_courses,
    UNIVERSITY_COURSES_DB,
)
from handlers.utils import (
    check_channel_membership,
    check_and_credit_membership,
    send_feature_lock_message,
)
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


def build_universities_list_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Builds 2-column grid of all universities from the markdown guide."""
    uni_names = get_all_university_names()
    keyboard = []

    # 2 buttons per row
    row = []
    for idx, name in enumerate(uni_names):
        # Shorten display name for compact grid
        short_name = name.replace("University", "Uni").replace("Science & Technology", "Sci-Tech")
        btn = InlineKeyboardButton(text=f"🏛️ {short_name}", callback_data=f"unicourse_idx_{idx}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_university_course_card_keyboard(uni_idx: int) -> InlineKeyboardMarkup:
    """Builds CTA buttons attached to a university course guide card."""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል (Join Channel)",
                url=f"https://t.me/{TARGET_CHANNEL}",
            )
        ],
        [
            InlineKeyboardButton(
                text="📚 የ 1st Year ኮርሶችና ሞጁሎች (Materials)",
                callback_data="courses_list_back",
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 ሌላ ዩኒቨርሲቲ ለመምረጥ (Select Another Uni)",
                callback_data="uni_list_back",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_universities_list(message: Message, edit: bool = False):
    """Renders the university course guide selection grid."""
    uni_names = get_all_university_names()
    text = (
        "🎓 <b>FreshMinds — የኢትዮጵያ ዩኒቨርሲቲዎች 1ኛ ሴሚስተር ኮርሶች</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "በ 2018/2019 ዓ.ም በትምህርት ሚኒስቴር የተመደቡበትን ዩኒቨርሲቲ በመምረጥ "
        "የ 1ኛ ሴሚስተር የ Natural Science እና Social Science ኮርሶች ዝርዝር ያግኙ:\n\n"
        f"📍 የተካተቱ ዩኒቨርሲቲዎች: <b>{len(uni_names)}</b>"
    )
    keyboard = build_universities_list_keyboard()

    if edit:
        await message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    else:
        await message.answer(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )


@router.message(F.text == msg.BTN_UNIVERSITIES)
@router.message(Command("universities"))
@router.message(Command("uni"))
async def handle_universities_list(message: Message, bot: Bot):
    """Displays the list of universities — gated behind channel membership."""
    if not await check_and_credit_membership(bot, message.from_user):
        await send_feature_lock_message(message, "🏛️ የዩኒቨርሲቲዎች 1ኛ ሴሚስተር ኮርሶችን", "retry_feature_universities")
        return
    await show_universities_list(message, edit=False)


@router.callback_query(F.data == "retry_feature_universities")
async def handle_retry_universities(callback: CallbackQuery, bot: Bot):
    """Retry handler for universities after user joins channel."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    if isinstance(callback.message, Message):
        await show_universities_list(callback.message, edit=True)


@router.callback_query(F.data.startswith("unicourse_idx_"))
async def handle_unicourse_by_idx(callback: CallbackQuery, bot: Bot):
    """Displays the 1st semester course breakdown card for a selected university index."""
    if not isinstance(callback.message, Message):
        return

    idx = int(callback.data.partition("unicourse_idx_")[2])
    uni_names = get_all_university_names()

    if idx < 0 or idx >= len(uni_names):
        await callback.answer("⚠️ ይቅርታ፣ ይህ ዩኒቨርሲቲ አልተገኘም!", show_alert=True)
        return

    uni_name = uni_names[idx]
    res = find_university_courses(uni_name)

    if not res:
        await callback.answer("⚠️ ይቅርታ፣ የዚህ ዩኒቨርሲቲ መረጃ አልተገኘም!", show_alert=True)
        return

    official_name, streams = res

    # Force Channel Membership Check
    is_member = await check_channel_membership(bot, callback.from_user.id)
    if not is_member:
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናላችንን ይቀላቀሉ!", show_alert=True)
        lock_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል (Join Channel)",
                        url=f"https://t.me/{TARGET_CHANNEL}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ ተቀላቅያለሁ (Check & View)",
                        callback_data=f"unicourse_idx_{idx}",
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
            f"🔒 <b>የ{official_name} 1ኛ ሴሚስተር ኮርሶች ዝርዝር ለማየት መጀመሪያ የቻናላችን ቤተሰብ ይሁኑ!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"የ 1ኛ ዓመት ማቴሪያሎች፣ ኖቶች እና የፈተና ጥያቄዎች ለማግኘት እባክዎ መጀመሪያ <b>@{TARGET_CHANNEL}</b> ቻናልን ይቀላቀሉ!\n\n"
            f"👇 ከታች <b>'ቻናል ተቀላቀል'</b> የሚለውን ተጭነው ከገቡ በኋላ <b>'ተቀላቅያለሁ'</b> የሚለውን ይጫኑ:"
        )
        await callback.message.edit_text(
            lock_text,
            parse_mode=ParseMode.HTML,
            reply_markup=lock_keyboard,
            disable_web_page_preview=True,
        )
        return

    await callback.answer()
    card_text = msg.format_university_courses_card(official_name, streams)
    keyboard = build_university_course_card_keyboard(idx)

    await callback.message.edit_text(
        card_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("uni_view_"))
async def handle_legacy_uni_view(callback: CallbackQuery, bot: Bot):
    """Handles university selection from Database ID (e.g. from placement result card)."""
    if not isinstance(callback.message, Message):
        return

    uni_id = int(callback.data.partition("uni_view_")[2])
    uni = await db.get_university_by_id(uni_id)

    if not uni:
        await callback.answer("⚠️ ይቅርታ፣ ይህ ዩኒቨርሲቲ አልተገኘም!", show_alert=True)
        return

    res = find_university_courses(uni.name)
    if not res:
        # Fallback to DB about text if not found in markdown
        await callback.message.edit_text(
            uni.about_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="🔙 ወደ ዩኒቨርሲቲዎች ዝርዝር (Back)", callback_data="uni_list_back")]]
            ),
            disable_web_page_preview=True,
        )
        return

    official_name, streams = res
    uni_names = get_all_university_names()
    uni_idx = uni_names.index(official_name) if official_name in uni_names else 0

    # Redirect to unicourse display
    callback.data = f"unicourse_idx_{uni_idx}"
    await handle_unicourse_by_idx(callback, bot)


@router.callback_query(F.data == "uni_list_back")
async def handle_universities_back(callback: CallbackQuery):
    """Returns to the university list view grid."""
    if not isinstance(callback.message, Message):
        return

    await callback.answer()
    await show_universities_list(callback.message, edit=True)

