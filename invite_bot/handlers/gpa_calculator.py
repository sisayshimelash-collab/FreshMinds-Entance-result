"""
FreshMinds GPA Calculator — Interactive Course-1 to Course-8 Live Table
"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
import messages as msg

logger = logging.getLogger(__name__)
router = Router()

# In-memory dictionary for user active GPA sessions
# Format: {user_id: {1: {'ch': 4, 'grade': 'A'}, 2: {'ch': 3, 'grade': 'A-'}, ...}}
user_gpa_sessions: dict[int, dict[int, dict]] = {}


def get_default_courses() -> dict[int, dict]:
    """Default freshman courses preset for convenient 1-tap calculation."""
    return {
        1: {"ch": 4, "grade": "A"},
        2: {"ch": 3, "grade": "A-"},
        3: {"ch": 3, "grade": "B+"},
        4: {"ch": 3, "grade": "A"},
        5: {"ch": 2, "grade": "B"},
        6: {"ch": None, "grade": None},
        7: {"ch": None, "grade": None},
        8: {"ch": None, "grade": None},
    }


def get_user_courses(user_id: int) -> dict[int, dict]:
    """Retrieve or initialize user's course table."""
    if user_id not in user_gpa_sessions:
        user_gpa_sessions[user_id] = get_default_courses()
    return user_gpa_sessions[user_id]


def build_gpa_table_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Builds interactive Course-1 to Course-8 table keyboard."""
    courses = get_user_courses(user_id)
    keyboard = []

    for idx in range(1, 9):
        c = courses.get(idx, {})
        ch = c.get("ch")
        grade = c.get("grade")
        if ch and grade:
            btn_text = f"Course-{idx}: {ch} CH | Grade: {grade} ✏️"
        else:
            btn_text = f"Course-{idx}: [ Unfilled ] ➕"

        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"gpa_edit_{idx}")])

    keyboard.append([
        InlineKeyboardButton(text="🧮 አስላ (Calculate GPA)", callback_data="gpa_do_calc"),
        InlineKeyboardButton(text="🔄 Reset (አጽዳ)", callback_data="gpa_reset_all"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_course_editor_keyboard(user_id: int, course_idx: int) -> InlineKeyboardMarkup:
    """Builds Credit Hour and Grade selection keyboard for a specific course."""
    courses = get_user_courses(user_id)
    current_ch = courses[course_idx].get("ch")
    current_grade = courses[course_idx].get("grade")

    # 1. Credit Hours Row (1 to 5)
    ch_buttons = []
    for ch in [1, 2, 3, 4, 5]:
        ch_text = f"✅ {ch} CH" if current_ch == ch else f"{ch} CH"
        ch_buttons.append(
            InlineKeyboardButton(text=ch_text, callback_data=f"gpa_setch_{course_idx}_{ch}")
        )

    # 2. Grades Row 1 (A+, A, A-, B+, B, B-)
    grades_row1 = []
    for g in ["A+", "A", "A-", "B+", "B", "B-"]:
        g_text = f"✅ {g}" if current_grade == g else g
        grades_row1.append(
            InlineKeyboardButton(text=g_text, callback_data=f"gpa_setgrade_{course_idx}_{g}")
        )

    # 3. Grades Row 2 (C+, C, C-, D, F)
    grades_row2 = []
    for g in ["C+", "C", "C-", "D", "F"]:
        g_text = f"✅ {g}" if current_grade == g else g
        grades_row2.append(
            InlineKeyboardButton(text=g_text, callback_data=f"gpa_setgrade_{course_idx}_{g}")
        )

    # 4. Action Row (Clear / Back)
    action_row = [
        InlineKeyboardButton(text="🗑️ Unfill (አጽዳ)", callback_data=f"gpa_clear_{course_idx}"),
        InlineKeyboardButton(text="🔙 ወደ ሰንጠረዥ (Done)", callback_data="gpa_back_table"),
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            ch_buttons,
            grades_row1,
            grades_row2,
            action_row,
        ]
    )


@router.message(F.text == msg.BTN_GPA_CALC)
@router.message(Command("gpa"))
@router.message(Command("calculator"))
async def handle_gpa_calculator(message: Message):
    """Entry point for the interactive GPA Calculator."""
    user = message.from_user
    if not user:
        return

    # Initialize courses
    courses = get_user_courses(user.id)
    filled_count = sum(1 for c in courses.values() if c.get("ch") and c.get("grade"))

    text = (
        "🧮 <b>FreshMinds — የ 1st Semester GPA ማስያ (Live Table)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ከታች ካሉት ኮርሶች ውስጥ የወሰዷቸውን <b>Credit Hour (CH)</b> እና <b>Grade (A, B...)</b> ይምረጡ።\n\n"
        "💡 <i>ያልወሰዷቸውን ኮርሶች (Unfilled) እንደነበሩ መተው ይችላሉ፤ ካልኩሌተሩ ያልተሞሉትን በራሱ ችላ ይላል!</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 በአሁኑ ሰዓት የተሞሉ ኮርሶች: <b>{filled_count} / 8</b>"
    )

    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_gpa_table_keyboard(user.id),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("gpa_edit_"))
async def handle_gpa_edit_course(callback: CallbackQuery):
    """Opens the Credit Hour & Grade editor for a course."""
    course_idx = int(callback.data.partition("gpa_edit_")[2])
    user_id = callback.from_user.id
    courses = get_user_courses(user_id)
    c = courses[course_idx]
    ch_str = f"{c.get('ch')} CH" if c.get('ch') else "Not set"
    grade_str = c.get('grade') if c.get('grade') else "Not set"

    await callback.answer()
    text = (
        f"✏️ <b>Course-{course_idx} ማስተካከያ:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Current Credit Hour: <b>{ch_str}</b>\n"
        f"⭐ Current Grade: <b>{grade_str}</b>\n\n"
        "👇 <b>Credit Hour እና የጠበቁትን Grade ይምረጡ:</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_course_editor_keyboard(user_id, course_idx),
    )


@router.callback_query(F.data.startswith("gpa_setch_"))
async def handle_gpa_set_ch(callback: CallbackQuery):
    """Sets the credit hour for a course."""
    parts = callback.data.split("_")
    course_idx = int(parts[2])
    ch = int(parts[3])
    user_id = callback.from_user.id

    courses = get_user_courses(user_id)
    courses[course_idx]["ch"] = ch
    # If grade is not set, default to A
    if not courses[course_idx].get("grade"):
        courses[course_idx]["grade"] = "A"

    await callback.answer(f"✅ Credit Hour: {ch} CH ተመርጧል")
    try:
        await callback.message.edit_reply_markup(
            reply_markup=build_course_editor_keyboard(user_id, course_idx)
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise


@router.callback_query(F.data.startswith("gpa_setgrade_"))
async def handle_gpa_set_grade(callback: CallbackQuery):
    """Sets the grade for a course and returns to the table."""
    parts = callback.data.split("_")
    course_idx = int(parts[2])
    grade = parts[3]
    user_id = callback.from_user.id

    courses = get_user_courses(user_id)
    courses[course_idx]["grade"] = grade
    # If CH is not set, default to 3
    if not courses[course_idx].get("ch"):
        courses[course_idx]["ch"] = 3

    await callback.answer(f"✅ Course-{course_idx}: {courses[course_idx]['ch']} CH | {grade}")
    # Return to table
    filled_count = sum(1 for c in courses.values() if c.get("ch") and c.get("grade"))
    text = (
        "🧮 <b>FreshMinds — የ 1st Semester GPA ማስያ (Live Table)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ከታች ካሉት ኮርሶች ውስጥ የወሰዷቸውን <b>Credit Hour (CH)</b> እና <b>Grade (A, B...)</b> ይምረጡ።\n\n"
        "💡 <i>ያልወሰዷቸውን ኮርሶች (Unfilled) እንደነበሩ መተው ይችላሉ፤ ካልኩሌተሩ ያልተሞሉትን በራሱ ችላ ይላል!</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 በአሁኑ ሰዓት የተሞሉ ኮርሶች: <b>{filled_count} / 8</b>"
    )
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_gpa_table_keyboard(user_id),
    )


@router.callback_query(F.data.startswith("gpa_clear_"))
async def handle_gpa_clear_course(callback: CallbackQuery):
    """Clears a course slot (marks it unfilled)."""
    course_idx = int(callback.data.partition("gpa_clear_")[2])
    user_id = callback.from_user.id
    courses = get_user_courses(user_id)
    courses[course_idx] = {"ch": None, "grade": None}

    await callback.answer(f"🗑️ Course-{course_idx} ተሰርዟል")
    filled_count = sum(1 for c in courses.values() if c.get("ch") and c.get("grade"))
    text = (
        "🧮 <b>FreshMinds — የ 1st Semester GPA ማስያ (Live Table)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ከታች ካሉት ኮርሶች ውስጥ የወሰዷቸውን <b>Credit Hour (CH)</b> እና <b>Grade (A, B...)</b> ይምረጡ።\n\n"
        "💡 <i>ያልወሰዷቸውን ኮርሶች (Unfilled) እንደነበሩ መተው ይችላሉ፤ ካልኩሌተሩ ያልተሞሉትን በራሱ ችላ ይላል!</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 በአሁኑ ሰዓት የተሞሉ ኮርሶች: <b>{filled_count} / 8</b>"
    )
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_gpa_table_keyboard(user_id),
    )


@router.callback_query(F.data == "gpa_back_table")
async def handle_gpa_back_table(callback: CallbackQuery):
    """Returns to the live table view."""
    await callback.answer()
    user_id = callback.from_user.id
    courses = get_user_courses(user_id)
    filled_count = sum(1 for c in courses.values() if c.get("ch") and c.get("grade"))

    text = (
        "🧮 <b>FreshMinds — የ 1st Semester GPA ማስያ (Live Table)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ከታች ካሉት ኮርሶች ውስጥ የወሰዷቸውን <b>Credit Hour (CH)</b> እና <b>Grade (A, B...)</b> ይምረጡ።\n\n"
        "💡 <i>ያልወሰዷቸውን ኮርሶች (Unfilled) እንደነበሩ መተው ይችላሉ፤ ካልኩሌተሩ ያልተሞሉትን በራሱ ችላ ይላል!</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 በአሁኑ ሰዓት የተሞሉ ኮርሶች: <b>{filled_count} / 8</b>"
    )
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_gpa_table_keyboard(user_id),
    )


@router.callback_query(F.data == "gpa_reset_all")
async def handle_gpa_reset_all(callback: CallbackQuery):
    """Resets all courses to unfilled."""
    user_id = callback.from_user.id
    user_gpa_sessions[user_id] = {i: {"ch": None, "grade": None} for i in range(1, 9)}

    await callback.answer("🔄 ሰንጠረዡ ጸድቷል (Reset)", show_alert=True)
    text = (
        "🧮 <b>FreshMinds — የ 1st Semester GPA ማስያ (Live Table)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ከታች ካሉት ኮርሶች ውስጥ የወሰዷቸውን <b>Credit Hour (CH)</b> እና <b>Grade (A, B...)</b> ይምረጡ።\n\n"
        "💡 <i>ያልወሰዷቸውን ኮርሶች (Unfilled) እንደነበሩ መተው ይችላሉ፤ ካልኩሌተሩ ያልተሞሉትን በራሱ ችላ ይላል!</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📝 በአሁኑ ሰዓት የተሞሉ ኮርሶች: <b>0 / 8</b>"
    )
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_gpa_table_keyboard(user_id),
    )


@router.callback_query(F.data == "gpa_do_calc")
async def handle_gpa_do_calc(callback: CallbackQuery):
    """Calculates semester GPA ignoring unfilled slots and presents results."""
    user_id = callback.from_user.id
    courses = get_user_courses(user_id)

    gpa, total_ch, total_pts, breakdown = msg.calculate_gpa(courses)

    if total_ch == 0 or len(breakdown) == 0:
        await callback.answer("⚠️ እባክዎ ቢያንስ የአንድ ኮርስ Credit Hour እና Grade ይሙሉ!", show_alert=True)
        return

    await callback.answer("✅ ስሌቱ ተጠናቋል!")
    result_text = msg.format_gpa_result_card(gpa, total_ch, total_pts, breakdown)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 እንደገና አስላ (Recalculate)", callback_data="gpa_back_table")],
        ]
    )

    await callback.message.answer(
        result_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
