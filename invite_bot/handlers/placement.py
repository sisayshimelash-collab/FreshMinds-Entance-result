"""
FreshMinds Placement Handler — University Placement Checker
Queries the Ethiopian Ministry of Education placement endpoint with channel membership gating,
local caching, and direct links into campus guides & freshman resources.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode, ChatAction

from database import db
from config import TARGET_CHANNEL
from placement_client import placement_client
from handlers.utils import check_and_credit_membership, send_feature_lock_message
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


class PlacementStates(StatesGroup):
    waiting_for_admission_no = State()


def get_placement_cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel button when waiting for user admission number."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ ሰርዝ (Cancel)", callback_data="cancel_placement")]
        ]
    )


async def build_placement_result_keyboard(university_name: str) -> InlineKeyboardMarkup:
    """Builds inline action buttons for the placement result card."""
    buttons = []

    # 1. Cross-link: Check if assigned university exists in bot's directory
    uni_record = await db.find_university_by_name(university_name)
    if uni_record:
        buttons.append([
            InlineKeyboardButton(
                text=f"🏛️ ስለ {uni_record.name} መረጃ እይ",
                callback_data=f"uni_view_{uni_record.id}",
            )
        ])

    # 2. Direct access to freshman materials
    buttons.append([
        InlineKeyboardButton(
            text="📚 የ 1st Year ኮርሶችና ሞጁሎች (Courses)",
            callback_data="placement_view_courses",
        )
    ])

    # 3. Quick re-check button
    buttons.append([
        InlineKeyboardButton(
            text="🔄 ሌላ ቁጥር ለመፈለግ (Check Another)",
            callback_data="check_another_placement",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == msg.BTN_PLACEMENT)
@router.message(Command("placement"))
@router.message(Command("result"))
async def start_placement_flow(message: Message, bot: Bot, state: FSMContext):
    """Initiates placement check flow with channel membership check and admin toggle gating."""
    from handlers.admin import is_admin

    user = message.from_user
    is_user_admin = user and is_admin(user.id)
    placement_enabled = await db.is_placement_enabled()

    if not placement_enabled and not is_user_admin:
        await message.answer(
            "ℹ️ <b>የዩኒቨርሲቲ ምደባ ማወቂያ በአሁኑ ወቅት ዝግ ነው!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "ተማሪዎች አሁንም የዩኒቨርሲቲ ምርጫ (Choosing Stage) ላይ ስለሆኑ የ 2019 ዓ.ም ምደባ በትምህርት ሚኒስቴር እስካሁን ይፋ አልተደረገም።\n\n"
            "📢 <i>የትምህርት ሚኒስቴር ይፋ እንዳደረገ ይህ አገልግሎት ወዲያውኑ የሚከፈት ይሆናል!</i>\n"
            "እስከዚያው ድረስ የቦቱን የኮርስ ማቴሪያሎች እና የዩኒቨርሲቲ መረጃዎች በነፃ መጠቀም ይችላሉ።",
            parse_mode=ParseMode.HTML,
        )
        return

    if not await check_and_credit_membership(bot, user):
        await send_feature_lock_message(
            message,
            "🎓 የዩኒቨርሲቲ ምደባ ማወቂያን",
            "retry_feature_placement",
        )
        return

    admin_hint = "\n\n<i>🛡️ (Admin Mode: Feature is currently disabled for normal users)</i>" if (is_user_admin and not placement_enabled) else ""
    await state.set_state(PlacementStates.waiting_for_admission_no)
    await message.answer(
        msg.PLACEMENT_PROMPT_TEXT + admin_hint,
        parse_mode=ParseMode.HTML,
        reply_markup=get_placement_cancel_keyboard(),
    )


@router.callback_query(F.data == "retry_feature_placement")
async def handle_retry_placement(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Retry handler after user joins channel."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return

    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await state.set_state(PlacementStates.waiting_for_admission_no)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            msg.PLACEMENT_PROMPT_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=get_placement_cancel_keyboard(),
        )


@router.callback_query(F.data == "cancel_placement")
async def handle_cancel_placement(callback: CallbackQuery, state: FSMContext):
    """Cancels placement lookup."""
    await state.clear()
    await callback.answer("ተሰርዟል", show_alert=False)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "❌ የምደባ ፍለጋ ተሰርዟል። የሚፈልጉትን ከዋናው ሜኑ ይምረጡ።",
            parse_mode=ParseMode.HTML,
        )


@router.callback_query(F.data == "check_another_placement")
async def handle_check_another_placement(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Prompts user to enter another admission number."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return

    await callback.answer()
    await state.set_state(PlacementStates.waiting_for_admission_no)
    if isinstance(callback.message, Message):
        await callback.message.answer(
            msg.PLACEMENT_PROMPT_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=get_placement_cancel_keyboard(),
        )


@router.callback_query(F.data == "placement_view_courses")
async def handle_placement_courses(callback: CallbackQuery, bot: Bot):
    """Redirects user to courses directory."""
    from handlers.resources import show_courses_list
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer()
    if isinstance(callback.message, Message):
        await show_courses_list(callback.message, edit=False)


@router.message(PlacementStates.waiting_for_admission_no)
async def process_admission_number(message: Message, bot: Bot, state: FSMContext):
    """Processes user entered admission number and queries MoE Placement API."""
    text = (message.text or "").strip()

    # Cancel command or menu button tapped
    if text in ("/cancel", "cancel", "ሰርዝ"):
        await state.clear()
        await message.answer("❌ የምደባ ፍለጋ ተሰርዟል።", parse_mode=ParseMode.HTML)
        return

    # If user clicks another main menu button while in state, handle gracefully
    if text in (
        msg.BTN_PLACEMENT,
        msg.BTN_RESOURCES,
        msg.BTN_UNIVERSITIES,
        msg.BTN_GPA_CALC,
        msg.BTN_GET_LINK,
        msg.BTN_MY_STATS,
        msg.BTN_LEADERBOARD,
        msg.BTN_RULES,
        msg.BTN_CHANNEL,
    ):
        await state.clear()
        return

    # Basic admission number validation (allow digits/letters, length 4 to 15)
    clean_admission_no = text.replace(" ", "").replace("#", "")
    if len(clean_admission_no) < 4 or len(clean_admission_no) > 15:
        await message.answer(
            "⚠️ <b>ያስገቡት መለያ ቁጥር ልክ አይደለም!</b>\n"
            "እባክዎ ትክክለኛ የፈተና መለያ ቁጥርዎን (ለምሳሌ <code>00052454</code>) ያስገቡ ወይም ለመሰረዝ <b>/cancel</b> ይበሉ:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_placement_cancel_keyboard(),
        )
        return

    # Send typing action
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("🔍 <b>ምደባዎ በመፈለግ ላይ ነው፣ እባክዎ ትንሽ ይጠብቁ...</b>", parse_mode=ParseMode.HTML)

    # 1. Check local cache first
    cached_record = await db.get_cached_placement(clean_admission_no)
    if cached_record and cached_record.university:
        await state.clear()
        keyboard = await build_placement_result_keyboard(cached_record.university)
        response_text = msg.format_placement_card(
            student_name=cached_record.student_name,
            reg_number=clean_admission_no,
            university=cached_record.university,
            stream=cached_record.stream or "N/A",
            cached=True,
        )
        await status_msg.edit_text(response_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return

    # 2. Query live placement endpoint
    result = await placement_client.query_placement(clean_admission_no)

    if result.status == "SUCCESS":
        await state.clear()
        student_name = result.student_name or "N/A"
        university = result.university or "N/A"
        stream = result.stream or "N/A"

        # Save to local cache
        raw_json_str = str(result.raw_data) if result.raw_data else ""
        await db.save_placement_cache(
            admission_no=clean_admission_no,
            student_name=student_name,
            university=university,
            stream=stream,
            raw_json=raw_json_str,
        )

        keyboard = await build_placement_result_keyboard(university)
        response_text = msg.format_placement_card(
            student_name=student_name,
            reg_number=clean_admission_no,
            university=university,
            stream=stream,
            cached=False,
        )
        await status_msg.edit_text(response_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    elif result.status == "NOT_FOUND":
        # Keep state active so user can retype or cancel
        await status_msg.edit_text(
            msg.PLACEMENT_NOT_RELEASED_TEXT.format(reg_no=clean_admission_no),
            parse_mode=ParseMode.HTML,
            reply_markup=get_placement_cancel_keyboard(),
        )

    elif result.status in ("SERVER_BUSY", "TIMEOUT"):
        await status_msg.edit_text(
            msg.PLACEMENT_SERVER_BUSY_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=get_placement_cancel_keyboard(),
        )

    else:
        await status_msg.edit_text(
            "⚠️ <b>ስህተት ተፈጥሯል!</b>\n"
            "የትምህርት ሚኒስቴር ሰርቨርን ማግኘት አልተቻለም። እባክዎ ከጥቂት ደቂቃዎች በኋላ በድጋሚ ይሞክሩ።",
            parse_mode=ParseMode.HTML,
            reply_markup=get_placement_cancel_keyboard(),
        )
