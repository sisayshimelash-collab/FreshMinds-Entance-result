"""
FreshMinds Course Resources & Materials Explorer — Modules, Notes & Exam Banks
"""

import asyncio
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
    check_channel_membership,
    check_and_credit_membership,
    send_feature_lock_message,
)
import messages as msg

logger = logging.getLogger(__name__)
router = Router()

CATEGORY_NAMES = {
    "module": "📖 Official Course Module (PDF)",
    "note": "📝 Summary Handouts & Notes",
    "midterm": "📑 Midterm Exam Bank (with Solutions)",
    "final": "🎯 Final Exam Bank (with Solutions)",
    "video": "🎥 Video Tutorials & Drive Links",
}


# check_channel_membership imported from handlers.utils


def build_courses_keyboard(courses: list) -> InlineKeyboardMarkup:
    """Builds keyboard grid of all available courses."""
    keyboard = []
    # 2 buttons per row for compact clean UI
    row = []
    for c in courses:
        row.append(
            InlineKeyboardButton(text=f"{c.icon} {c.name}", callback_data=f"course_view_{c.id}")
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_course_categories_keyboard(course_id: int) -> InlineKeyboardMarkup:
    """Builds category options for a selected course."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=CATEGORY_NAMES["module"], callback_data=f"ccat_{course_id}_module")],
            [InlineKeyboardButton(text=CATEGORY_NAMES["note"], callback_data=f"ccat_{course_id}_note")],
            [InlineKeyboardButton(text=CATEGORY_NAMES["midterm"], callback_data=f"ccat_{course_id}_midterm")],
            [InlineKeyboardButton(text=CATEGORY_NAMES["final"], callback_data=f"ccat_{course_id}_final")],
            [InlineKeyboardButton(text=CATEGORY_NAMES["video"], callback_data=f"ccat_{course_id}_video")],
            [InlineKeyboardButton(text="🔙 ወደ ኮርሶች ዝርዝር (Back)", callback_data="courses_list_back")],
        ]
    )


async def show_courses_list(target: Message | CallbackQuery):
    """Renders the course selection list."""
    courses = await db.get_all_courses()
    if not courses:
        text = (
            "📚 <b>የኮርስ ማቴሪያሎች ማዕከል</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<i>ይቅርታ፣ እስካሁን ምንም ኮርስ አልተመዘገበም።</i>"
        )
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text, parse_mode=ParseMode.HTML)
        else:
            await target.answer(text, parse_mode=ParseMode.HTML)
        return

    text = (
        "📚 <b>FreshMinds — የ 1ኛ አመት (Freshman) ኮርሶችና ማቴሪያሎች</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "የሚፈልጉትን ኮርስ በመጫን <b>ሞጁሎች፣ ማጠቃለያ ኖቶች፣ የፈተና ሞዴሎች እና ቪዲዮዎችን</b> በነፃ ያግኙ:\n\n"
        "👇 <b>ኮርስ ይምረጡ:</b>"
    )
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_courses_keyboard(courses),
            disable_web_page_preview=True,
        )
    else:
        await target.answer(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_courses_keyboard(courses),
            disable_web_page_preview=True,
        )


@router.message(F.text == msg.BTN_RESOURCES)
@router.message(Command("resources"))
@router.message(Command("courses"))
@router.message(Command("materials"))
async def handle_resources_menu(message: Message, bot: Bot):
    """Entry point for browsing freshman courses and materials — gates with channel membership."""
    if not await check_and_credit_membership(bot, message.from_user):
        await send_feature_lock_message(message, "📚 የኮርስ ማቴሪያሎችን", "retry_feature_resources")
        return
    await show_courses_list(message)


@router.callback_query(F.data == "retry_feature_resources")
async def handle_retry_resources(callback: CallbackQuery, bot: Bot):
    """Retry handler for resources after user joins channel."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await show_courses_list(callback)


@router.callback_query(F.data.startswith("course_view_"))
async def handle_course_view(callback: CallbackQuery):
    """Displays material categories for the selected course."""
    course_id = int(callback.data.partition("course_view_")[2])
    course = await db.get_course_by_id(course_id)

    if not course:
        await callback.answer("⚠️ ኮርሱ አልተገኘም!", show_alert=True)
        return

    await callback.answer()
    text = (
        f"{course.icon} <b>{course.name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "የሚፈልጉትን የማቴሪያል አይነት ይምረጡ:\n\n"
        "• 📖 <b>Official Module:</b> የትምህርት ሚኒስቴር ይፋዊ ሞጁል\n"
        "• 📝 <b>Notes & Handouts:</b> በአጫጭር የተዘጋጁ የማጠቃለያ ኖቶች\n"
        "• 📑 <b>Midterm & Final:</b> ያለፉ የዩኒቨርሲቲ ፈተናዎች ከመልሶቻቸው ጋር\n"
        "• 🎥 <b>Videos:</b> የቪዲዮ ትምህርቶችና ጠቃሚ ሊንኮች"
    )

    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_course_categories_keyboard(course_id),
    )


@router.callback_query(F.data.startswith("ccat_"))
async def handle_course_category_view(callback: CallbackQuery, bot: Bot):
    """Verifies channel membership and reveals all materials under the selected course category."""
    # Format: ccat_<course_id>_<category>
    _, course_id_str, category = callback.data.split("_", 2)
    course_id = int(course_id_str)
    user_id = callback.from_user.id

    course = await db.get_course_by_id(course_id)
    cat_title = CATEGORY_NAMES.get(category, "ማቴሪያሎች")

    if not course:
        await callback.answer("⚠️ ኮርሱ አልተገኘም!", show_alert=True)
        return

    # Check Channel Membership (Force-Subscription to reveal materials)
    is_member = await check_channel_membership(bot, user_id)
    if not is_member:
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናላችንን ይቀላቀሉ!", show_alert=True)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል", url=f"https://t.me/{TARGET_CHANNEL}")],
                [InlineKeyboardButton(text="🔓 ተቀላቅያለሁ (ሁሉንም ክፈት / Reveal)", callback_data=f"ccat_{course_id}_{category}")],
                [InlineKeyboardButton(text="🔙 ወደ ማቴሪያል ምድቦች (Back)", callback_data=f"course_view_{course_id}")],
            ]
        )
        await callback.message.edit_text(
            f"🔒 <b>የ{course.name} ({cat_title}) ማቴሪያሎችን ለማግኘት:</b>\n\n"
            f"እነዚህን ጠቃሚ ማቴሪያሎችና ፈተናዎች በነፃ ለማውረድ የ <b>@{TARGET_CHANNEL}</b> ቻናላችን አባል መሆን አለብዎት።\n\n"
            f"1️⃣ ከታች ያለውን <b>'@{TARGET_CHANNEL} ቻናል ተቀላቀል'</b> ይጫኑ\n"
            f"2️⃣ ቻናሉን ከተቀላቀሉ በኋላ <b>'ተቀላቅያለሁ (ሁሉንም ክፈት)'</b> የሚለውን ይጫኑ!",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        return

    await callback.answer("✨ ማቴሪያሎቹ በመከፈት ላይ ናቸው...", show_alert=False)
    materials = await db.get_materials_by_course(course_id, category)
    # Reverse to deliver in chronological order (earliest uploaded first)
    materials_ordered = list(reversed(materials))

    if not materials_ordered:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 ወደ ማቴሪያል ምድቦች (Back)", callback_data=f"course_view_{course_id}")]
            ]
        )
        await callback.message.edit_text(
            f"{course.icon} <b>{course.name}</b>\n"
            f"📁 <b>{cat_title}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<i>📌 ለዚህ ኮርስ ማቴሪያሎች በቅርቡ የሚጫኑ ይሆናል።</i>\n\n"
            f"አዳዲስ ማቴሪያሎች ሲጫኑ በ <b>@{TARGET_CHANNEL}</b> ይፋ ይደረጋሉ!",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        return

    # User is verified and materials exist: Reveal all!
    await callback.message.edit_text(
        f"🎉 <b>{course.icon} {course.name} — {cat_title}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>{len(materials_ordered)}</b> ማቴሪያል(ሎች) ተገኝተዋል! ከስር ተልከውሎታል:\n"
        f"🎓 ከ <b>FreshMinds Academy</b> | 📢 @{TARGET_CHANNEL}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    # Deliver every document / file / link
    for idx, m in enumerate(materials_ordered, start=1):
        try:
            if m.file_id:
                await bot.send_document(
                    chat_id=user_id,
                    document=m.file_id,
                    caption=(
                        f"📚 <b>{idx}. {m.title}</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎓 <b>{course.name}</b> | {cat_title}\n"
                        f"✨ <i>FreshMinds Academy</i> | 📢 @{TARGET_CHANNEL}"
                    ),
                    parse_mode=ParseMode.HTML,
                )
            elif m.external_url:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"📚 <b>{idx}. {m.title}</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔗 <b>የማቴሪያሉ ሊንክ:</b>\n{m.external_url}\n\n"
                        f"🎓 <b>{course.name}</b> | 📢 @{TARGET_CHANNEL}"
                    ),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False,
                )
            # Brief pause to avoid Telegram flood limits
            await asyncio.sleep(0.35)
        except Exception as e:
            logger.error(f"Failed to deliver material {m.id} to user {user_id}: {e}")

    # Send completion card with navigation buttons
    nav_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📂 ሌሎች ማቴሪያሎችን ምረጥ (Categories)", callback_data=f"course_view_{course_id}")],
            [InlineKeyboardButton(text="📚 ወደ ኮርሶች ዝርዝር (All Courses)", callback_data="courses_list_back")],
        ]
    )
    await bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ <b>ሁሉም የ{course.name} ({cat_title}) ማቴሪያሎች ተልከዋል!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "ተጨማሪ ኮርሶችንና ማቴሪያሎችን ከታች መምረጥ ይችላሉ 👇"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=nav_keyboard,
    )


@router.callback_query(F.data.startswith("mat_get_"))
@router.callback_query(F.data.startswith("mat_verify_"))
async def handle_material_download(callback: CallbackQuery, bot: Bot):
    """Verifies channel membership and delivers the requested file."""
    user = callback.from_user
    material_id = int(callback.data.split("_")[-1])
    material = await db.get_material_by_id(material_id)

    if not material:
        await callback.answer("⚠️ ፋይሉ አልተገኘም!", show_alert=True)
        return

    # Check Channel Membership (Force-Subscription)
    is_member = await check_channel_membership(bot, user.id)

    if not is_member:
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናላችንን ይቀላቀሉ!", show_alert=True)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል", url=f"https://t.me/{TARGET_CHANNEL}")],
                [InlineKeyboardButton(text="✅ ተቀላቅያለሁ (አውርድ)", callback_data=f"mat_verify_{material_id}")],
            ]
        )
        await callback.message.answer(
            f"🔒 <b>ይህንን ማቴሪያል ለማውረድ የ ቻናላችን ቤተሰብ ይሁኑ!</b>\n\n"
            f"📄 <b>{material.title}</b>\n\n"
            f"👇 መጀመሪያ <b>@{TARGET_CHANNEL}</b> ቻናልን ተቀላቅለው <b>'ተቀላቅያለሁ'</b> የሚለውን ይጫኑ:",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        return

    # User is a verified channel member -> Deliver file!
    await callback.answer("📥 ማቴሪያሉ በመላክ ላይ...", show_alert=False)

    if material.file_id:
        try:
            await bot.send_document(
                chat_id=user.id,
                document=material.file_id,
                caption=(
                    f"📚 <b>{material.title}</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎓 ከ <b>FreshMinds Academy</b> የተዘጋጀ!\n"
                    f"📢 ቻናላችን: @{TARGET_CHANNEL}"
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(f"Failed to send document {material.file_id}: {e}")
            await callback.message.answer(
                f"⚠️ <b>ይቅርታ፣ ፋይሉን መላክ አልተቻለም።</b>\n{material.title}",
                parse_mode=ParseMode.HTML,
            )
    elif material.external_url:
        await callback.message.answer(
            f"📚 <b>{material.title}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <b>የማቴሪያሉ ሊንክ:</b>\n{material.external_url}\n\n"
            f"📢 ቻናላችን: @{TARGET_CHANNEL}",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
        )
    else:
        await callback.message.answer(
            f"📚 <b>{material.title}</b>\n━━━━━━━━━━━━━━━━━━━━\n<i>ማቴሪያል ዝግጁ ነው።</i>",
            parse_mode=ParseMode.HTML,
        )


@router.callback_query(F.data == "courses_list_back")
async def handle_courses_list_back(callback: CallbackQuery):
    """Returns to the courses list."""
    await callback.answer()
    courses = await db.get_all_courses()

    text = (
        "📚 <b>FreshMinds — የ 1ኛ አመት (Freshman) ኮርሶችና ማቴሪያሎች</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "የሚፈልጉትን ኮርስ በመጫን <b>ሞጁሎች፣ ማጠቃለያ ኖቶች፣ የፈተና ሞዴሎች እና ቪዲዮዎችን</b> በነፃ ያግኙ:\n\n"
        "👇 <b>ኮርስ ይምረጡ:</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_courses_keyboard(courses),
        disable_web_page_preview=True,
    )
