"""
FreshMinds University Directory & 1st Semester Course Guide Handler
- General University Info & Departments (SQLite DB)
- 1st Semester Course Guide by University (FreshMinds_Academy_Freshman_Course_Guide.md)
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
)
from handlers.utils import (
    check_channel_membership,
    check_and_credit_membership,
    send_feature_lock_message,
)
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


# ── FEATURE A: General University Directory & Departments (DB) ────────────────
def build_db_universities_keyboard(unis: list) -> InlineKeyboardMarkup:
    """Builds 2-column grid of all universities from the database for general info."""
    keyboard = []
    row = []
    for u in unis:
        short_name = u.name.replace("University", "Uni").replace("Science & Technology", "Sci-Tech")
        btn = InlineKeyboardButton(text=f"🏛️ {short_name}", callback_data=f"uni_info_id_{u.id}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def show_db_universities_info_list(target: Message | CallbackQuery):
    """Renders general university information selection grid from DB."""
    unis = await db.get_all_universities()
    if not unis:
        text = "🏛️ <b>የኢትዮጵያ ዩኒቨርሲቲዎች መረጃ</b>\n━━━━━━━━━━━━━━━━━━━━\n<i>ይቅርታ፣ ምንም የዩኒቨርሲቲ መረጃ አልተገኘም።</i>"
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text, parse_mode=ParseMode.HTML)
        else:
            await target.answer(text, parse_mode=ParseMode.HTML)
        return

    text = (
        "🏛️ <b>FreshMinds — የኢትዮጵያ ዩኒቨርሲቲዎች መረጃና የዲፓርትመንቶች ዝርዝር</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ስለ ዩኒቨርሲቲዎች አጠቃላይ መረጃ፣ የካምፓስ ህይወት እና ያሉትን የዲፓርትመንት አማራጮች ለማወቅ ዩኒቨርሲቲ ይምረጡ:\n\n"
        f"📍 የተመዘገቡ ዩኒቨርሲቲዎች: <b>{len(unis)}</b>"
    )
    keyboard = build_db_universities_keyboard(unis)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await target.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)


@router.message(F.text == msg.BTN_UNIVERSITIES)
@router.message(Command("universities"))
@router.message(Command("uni"))
async def handle_db_universities_info(message: Message, bot: Bot):
    """Entry point for General University Info & Departments — gated behind channel membership."""
    if not await check_and_credit_membership(bot, message.from_user):
        await send_feature_lock_message(message, "🏛️ የዩኒቨርሲቲዎች መረጃን", "retry_feature_universities")
        return
    await show_db_universities_info_list(message)


@router.callback_query(F.data == "retry_feature_universities")
async def handle_retry_universities(callback: CallbackQuery, bot: Bot):
    """Retry handler for universities info after user joins channel."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await show_db_universities_info_list(callback)


@router.callback_query(F.data.startswith("uni_info_id_"))
@router.callback_query(F.data.startswith("uni_view_"))
async def handle_uni_info_by_id(callback: CallbackQuery, bot: Bot):
    """Displays detailed university info & departments from DB."""
    uni_id_str = callback.data.split("_")[-1]
    if not uni_id_str.isdigit():
        return
    uni_id = int(uni_id_str)
    uni = await db.get_university_by_id(uni_id)

    if not uni:
        await callback.answer("⚠️ ይቅርታ፣ ይህ ዩኒቨርሲቲ አልተገኘም!", show_alert=True)
        return

    # Check Channel Membership
    is_member = await check_channel_membership(bot, callback.from_user.id)
    if not is_member:
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናላችንን ይቀላቀሉ!", show_alert=True)
        lock_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል", url=f"https://t.me/{TARGET_CHANNEL}")],
                [InlineKeyboardButton(text="✅ ተቀላቅያለሁ (ክፈት)", callback_data=f"uni_info_id_{uni_id}")],
                [InlineKeyboardButton(text="🔙 ወደ ዩኒቨርሲቲዎች ዝርዝር", callback_data="uni_info_back")],
            ]
        )
        await callback.message.edit_text(
            f"🔒 <b>ስለ {uni.name} መረጃ ለማየት መጀመሪያ የቻናላችን ቤተሰብ ይሁኑ!</b>\n\n"
            f"👇 መጀመሪያ <b>@{TARGET_CHANNEL}</b> ቻናልን ይቀላቀሉ:",
            parse_mode=ParseMode.HTML,
            reply_markup=lock_keyboard,
            disable_web_page_preview=True,
        )
        return

    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"📢 @{TARGET_CHANNEL} ቻናል (Official)", url=f"https://t.me/{TARGET_CHANNEL}")],
            [InlineKeyboardButton(text="📖 የ 1ኛ ሴሚስተር ኮርሶች (Course Guide)", callback_data="courses_guide_menu")],
            [InlineKeyboardButton(text="🔙 ወደ ዩኒቨርሲቲዎች ዝርዝር (Back)", callback_data="uni_info_back")],
        ]
    )

    await callback.message.edit_text(
        f"🏛️ <b>{uni.name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{uni.about_text}\n\n"
        f"🎓 <b>FreshMinds Academy</b> | 📢 @{TARGET_CHANNEL}",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "uni_info_back")
async def handle_uni_info_back(callback: CallbackQuery):
    """Returns to general DB university list."""
    await callback.answer()
    await show_db_universities_info_list(callback)


# ── FEATURE B: 1st Semester University Course Guide (Markdown Source of Fact) ──
def build_university_course_guide_keyboard() -> InlineKeyboardMarkup:
    """Builds 2-column grid of all universities from the markdown guide."""
    uni_names = get_all_university_names()
    keyboard = []
    row = []
    for idx, name in enumerate(uni_names):
        short_name = name.replace("University", "Uni").replace("Science & Technology", "Sci-Tech")
        btn = InlineKeyboardButton(text=f"📖 {short_name}", callback_data=f"unicourse_idx_{idx}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def show_university_course_guide_list(target: Message | CallbackQuery):
    """Renders 1st semester course guide university selection grid."""
    uni_names = get_all_university_names()
    text = (
        "📖 <b>FreshMinds — የዩኒቨርሲቲዎች 1ኛ ሴሚስተር ኮርሶች ዝርዝር</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "በ 2018/2019 ዓ.ም በትምህርት ሚኒስቴር የተመደቡበትን ዩኒቨርሲቲ በመምረጥ "
        "የ 1ኛ ሴሚስተር የ Natural Science እና Social Science ኮርሶች ዝርዝር ያግኙ:\n\n"
        f"📍 የተካተቱ ዩኒቨርሲቲዎች: <b>{len(uni_names)}</b>"
    )
    keyboard = build_university_course_guide_keyboard()

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await target.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)


@router.message(F.text == msg.BTN_UNI_COURSES)
@router.message(Command("unicourses"))
@router.message(Command("courseguide"))
async def handle_uni_courses_menu(message: Message, bot: Bot):
    """Entry point for 1st Semester Course Guide — gated behind channel membership."""
    if not await check_and_credit_membership(bot, message.from_user):
        await send_feature_lock_message(message, "📖 የ 1ኛ ሴሚስተር ኮርሶችን", "retry_feature_unicourses")
        return
    await show_university_course_guide_list(message)


@router.callback_query(F.data == "retry_feature_unicourses")
@router.callback_query(F.data == "courses_guide_menu")
async def handle_retry_unicourses(callback: CallbackQuery, bot: Bot):
    """Retry / navigation handler for course guide."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await show_university_course_guide_list(callback)


@router.callback_query(F.data.startswith("unicourse_idx_"))
async def handle_unicourse_by_idx(callback: CallbackQuery, bot: Bot):
    """Displays HD watermarked 1st semester course card image for selected university."""
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
                [InlineKeyboardButton(text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል", url=f"https://t.me/{TARGET_CHANNEL}")],
                [InlineKeyboardButton(text="✅ ተቀላቅያለሁ (ክፈት)", callback_data=f"unicourse_idx_{idx}")],
                [InlineKeyboardButton(text="🔙 ወደ ኮርሶች መምረጫ", callback_data="courses_guide_menu")],
            ]
        )
        await callback.message.edit_text(
            f"🔒 <b>የ{official_name} 1ኛ ሴሚስተር ኮርሶችን ለማየት መጀመሪያ ቻናላችንን ይቀላቀሉ!</b>\n\n"
            f"👇 መጀመሪያ <b>@{TARGET_CHANNEL}</b> ቻናልን ይቀላቀሉ:",
            parse_mode=ParseMode.HTML,
            reply_markup=lock_keyboard,
            disable_web_page_preview=True,
        )
        return

    await callback.answer("🎨 Graphic Course Card እየተዘጋጀ ነው...")
    card_text = msg.format_university_courses_card(official_name, streams)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል", url=f"https://t.me/{TARGET_CHANNEL}")],
            [InlineKeyboardButton(text="📚 የ 1st Year ኮርሶችና ሞጁሎች (Materials)", callback_data="courses_list_back")],
            [InlineKeyboardButton(text="🔄 ሌላ ዩኒቨርሲቲ ለመምረጥ (Select Another Uni)", callback_data="courses_guide_menu")],
        ]
    )

    try:
        import os, tempfile
        from aiogram.types import FSInputFile
        from freshminds_card_generator import generate_university_course_card_image

        temp_path = os.path.join(tempfile.gettempdir(), f"unicourse_{idx}.png")
        generate_university_course_card_image(
            university_name=official_name,
            streams_dict=streams,
            output_filename=temp_path,
        )
        photo_file = FSInputFile(temp_path)
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=photo_file,
            caption=card_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    except Exception as err:
        logger.warning(f"Could not send watermarked uni course photo card: {err}")
        await callback.message.edit_text(
            card_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )


@router.callback_query(F.data == "uni_list_back")
async def handle_universities_back(callback: CallbackQuery):
    """Returns to course guide grid view."""
    await callback.answer()
    await show_university_course_guide_list(callback)


