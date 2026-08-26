"""
FreshMinds Result Bot — Handlers (Native In-App Join Pop-up & Auto-Approve Flow)

Features:
- Native In-App Join Pop-up Sheet using Chat Join Requests
- Instant 0.05s Auto-Approval for new join requests
- Native pop-up alert dialogs (show_alert=True)
- Pre-fetches and renders result instantly upon join
"""

import re
import logging
from typing import Optional

from aiogram import Router, Bot, F
from aiogram.types import (
    Message, CallbackQuery, ChatJoinRequest,
    InlineKeyboardButton, InlineKeyboardMarkup,
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from config import FRESHMINDS_CHANNEL, FRESHMINDS_CHANNEL_LINK, FRESHMINDS_WEB_URL
from eaes_client import EAESClient, ResultStatus, EAESResult
from rate_limiter import RateLimiter, TTLCache
import messages as msg

logger = logging.getLogger(__name__)

router = Router()

# ── Shared instances & Caches ────────────────────────────────────────────────
eaes_client: EAESClient = None  # type: ignore
rate_limiter: RateLimiter = None  # type: ignore

# 15-minute in-memory cache for channel membership
membership_cache = TTLCache(default_ttl=900.0, max_size=50000)

# Cached dynamic in-app join link
cached_join_link: Optional[str] = None


def init(client: EAESClient, limiter: RateLimiter):
    """Initialize shared instances."""
    global eaes_client, rate_limiter
    eaes_client = client
    rate_limiter = limiter


async def get_in_app_join_link(bot: Bot) -> str:
    """
    Get or create a native Telegram Chat Join Request link.
    This opens a modal pop-up bottom sheet directly in the app.
    """
    global cached_join_link
    if cached_join_link:
        return cached_join_link

    try:
        link_obj = await bot.create_chat_invite_link(
            chat_id=f"@{FRESHMINDS_CHANNEL}",
            creates_join_request=True,
            name="FreshMinds Bot In-App Join",
        )
        cached_join_link = link_obj.invite_link
        return cached_join_link
    except Exception as e:
        logger.warning(f"Could not create join request link (using direct link): {e}")
        return FRESHMINDS_CHANNEL_LINK


# ── FSM States ───────────────────────────────────────────────────────────────

class ResultForm(StatesGroup):
    waiting_admission = State()
    waiting_name = State()
    waiting_transition_unlock = State()


# ── Keyboards ────────────────────────────────────────────────────────────────

def transition_gate_keyboard(join_url: str) -> InlineKeyboardMarkup:
    """Keyboard shown with native in-app pop-up join sheet."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=msg.BTN_JOIN_CHANNEL,
            url=join_url,
        )],
        [InlineKeyboardButton(
            text=msg.BTN_SHOW_RESULT,
            callback_data="show_result_after_join",
        )],
    ])


def after_result_keyboard(join_url: str, admission_no: str = "", first_name: str = "") -> InlineKeyboardMarkup:
    """Keyboard shown after successfully displaying a result."""
    web_link = FRESHMINDS_WEB_URL
    if admission_no and first_name:
        web_link = f"{FRESHMINDS_WEB_URL}?adm={admission_no}&name={first_name}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📸 የውጤት ማስታወሻ ምስል አውርድ (Story Card)",
            url=web_link,
        )],
        [InlineKeyboardButton(
            text=msg.BTN_CHECK_ANOTHER,
            callback_data="check_another",
        )],
        [InlineKeyboardButton(
            text=msg.BTN_JOIN_CHANNEL,
            url=join_url,
        )],
    ])


def try_again_keyboard(join_url: str) -> InlineKeyboardMarkup:
    """Keyboard shown after not released, student not found, or service error."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=msg.BTN_CHECK_ANOTHER,
            callback_data="check_another",
        )],
        [InlineKeyboardButton(
            text=msg.BTN_JOIN_CHANNEL,
            url=join_url,
        )],
    ])


# ── Input Sanitization Helpers ───────────────────────────────────────────────

def sanitize_admission_number(raw_text: Optional[str]) -> Optional[str]:
    """Cleans admission number: removes inner spaces, hyphens, and validates."""
    if not raw_text:
        return None
    cleaned = re.sub(r'[\s\-_\/]+', '', raw_text.strip())
    if cleaned.isdigit() and 3 <= len(cleaned) <= 12:
        return cleaned
    return None


def sanitize_first_name(raw_text: Optional[str]) -> Optional[str]:
    """Cleans first name: handles multi-word inputs, Ge'ez (Amharic) and Latin."""
    if not raw_text:
        return None
    trimmed = raw_text.strip()
    if not trimmed:
        return None

    tokens = re.split(r'[\s\-_,.]+', trimmed)
    first_token = tokens[0] if tokens else ""

    if not re.match(r'^[\u1200-\u137Fa-zA-Z\']+$', first_token):
        return None
    if len(first_token) < 2 or len(first_token) > 40:
        return None

    if first_token.isascii():
        return first_token[0].upper() + first_token[1:]
    return first_token


# ── Channel Membership Verification ──────────────────────────────────────────

async def is_channel_member(bot: Bot, user_id: int) -> bool:
    """Check channel membership with TTL cache to prevent Telegram API flood."""
    cache_key = f"member:{user_id}"
    cached_status = membership_cache.get(cache_key)
    if cached_status is not None:
        return cached_status

    try:
        member = await bot.get_chat_member(
            chat_id=f"@{FRESHMINDS_CHANNEL}",
            user_id=user_id,
        )
        is_member = member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        )
        membership_cache.set(cache_key, is_member, ttl=900.0)
        return is_member
    except TelegramAPIError as e:
        logger.warning(f"Telegram API check error for user {user_id}: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error in is_channel_member: {e}")
        return True


async def safe_delete_message(msg_obj: Optional[Message]):
    """Safely delete a message without raising unhandled exceptions."""
    if not msg_obj:
        return
    try:
        await msg_obj.delete()
    except Exception:
        pass


async def render_result_response(
    target_msg: Message,
    bot: Bot,
    result: EAESResult,
    admission_no: str,
    first_name: str,
    edit: bool = False,
):
    """Render the result or error response cleanly."""
    join_url = await get_in_app_join_link(bot)

    if result.status == ResultStatus.SUCCESS and result.student:
        result_text = msg.format_result_success(result.student, result.results)
        text = result_text + msg.FRESHMINDS_PROMO
        markup = after_result_keyboard(join_url, admission_no, first_name)
    elif result.status == ResultStatus.NOT_RELEASED:
        text = msg.RESULT_NOT_RELEASED
        markup = try_again_keyboard(join_url)
    elif result.status == ResultStatus.NOT_FOUND:
        text = msg.STUDENT_NOT_FOUND.format(
            admission_no=admission_no,
            first_name=first_name,
        )
        markup = try_again_keyboard(join_url)
    else:
        text = msg.SERVICE_ERROR
        markup = try_again_keyboard(join_url)

    if edit:
        try:
            await target_msg.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
                disable_web_page_preview=True,
            )
            return
        except Exception:
            pass

    await target_msg.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=markup,
        disable_web_page_preview=True,
    )


# ── Instant Auto-Approval for In-App Join Requests ───────────────────────────

@router.chat_join_request()
async def handle_chat_join_request(join_req: ChatJoinRequest, bot: Bot, state: FSMContext):
    """
    Handles native In-App Telegram Join Requests in real-time.
    Auto-approves the student in 0.05 seconds!
    """
    user_id = join_req.from_user.id
    try:
        # Instantly approve user into the channel
        await bot.approve_chat_join_request(
            chat_id=join_req.chat.id,
            user_chat_id=user_id,
        )
        # Update cache to True
        membership_cache.set(f"member:{user_id}", True, ttl=1800.0)
        logger.info(f"Auto-approved join request for user {user_id}")

        # Send immediate confirmation & result unlock to the user's private chat
        data = await state.get_data()
        admission_no = data.get("admission_no")
        first_name = data.get("first_name")

        if admission_no and first_name:
            result = await eaes_client.check_result(admission_no, first_name)
            join_url = await get_in_app_join_link(bot)
            if result.status == ResultStatus.SUCCESS and result.student:
                result_text = msg.format_result_success(result.student, result.results)
                await bot.send_message(
                    chat_id=user_id,
                    text=f"✅ <b>Channel Joined! Here is your result:</b>\n\n" + result_text + msg.FRESHMINDS_PROMO,
                    parse_mode=ParseMode.HTML,
                    reply_markup=after_result_keyboard(join_url, admission_no, first_name),
                    disable_web_page_preview=True,
                )
                await state.clear()
            elif result.status == ResultStatus.NOT_RELEASED:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"✅ <b>Channel Joined!</b>\n\n" + msg.RESULT_NOT_RELEASED,
                    parse_mode=ParseMode.HTML,
                    reply_markup=try_again_keyboard(join_url),
                    disable_web_page_preview=True,
                )
                await state.clear()

    except Exception as e:
        logger.warning(f"Error handling join request for {user_id}: {e}")


# ── /start Command ───────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """Handle /start — immediately prompt for admission number."""
    await state.clear()
    await message.answer(
        msg.WELCOME + "\n\n" + msg.PRIVACY_NOTICE,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await state.set_state(ResultForm.waiting_admission)


# ── "Check Another" Callback ──────────────────────────────────────────────────

@router.callback_query(F.data == "check_another")
async def cb_check_another(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Handle the 'Check Another Result' button."""
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        msg.ASK_ADMISSION_NUMBER,
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(ResultForm.waiting_admission)


# ── Admission Number Input ────────────────────────────────────────────────────

@router.message(ResultForm.waiting_admission)
async def handle_admission_number(message: Message, state: FSMContext):
    """Handle admission number input."""
    raw_text = message.text or ""
    admission_no = sanitize_admission_number(raw_text)

    if not admission_no:
        await message.answer(
            msg.INVALID_ADMISSION,
            parse_mode=ParseMode.HTML,
        )
        return

    await state.update_data(admission_no=admission_no)
    await message.answer(
        msg.ADMISSION_RECEIVED.format(admission_no=admission_no),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(ResultForm.waiting_name)


# ── First Name Input & Transition Gate ────────────────────────────────────────

@router.message(ResultForm.waiting_name)
async def handle_first_name(message: Message, state: FSMContext, bot: Bot):
    """Handle first name input and apply the transition gate."""
    user_id = message.from_user.id if message.from_user else 0
    raw_text = message.text or ""
    first_name = sanitize_first_name(raw_text)

    if not first_name:
        await message.answer(
            msg.INVALID_NAME,
            parse_mode=ParseMode.HTML,
        )
        return

    # Per-user rate limit check
    if not rate_limiter.is_allowed(user_id):
        wait = rate_limiter.seconds_until_reset(user_id)
        await message.answer(
            msg.RATE_LIMITED.format(seconds=wait),
            parse_mode=ParseMode.HTML,
        )
        return

    data = await state.get_data()
    admission_no = data.get("admission_no", "")
    if not admission_no:
        await message.answer(
            msg.ASK_ADMISSION_NUMBER,
            parse_mode=ParseMode.HTML,
        )
        await state.set_state(ResultForm.waiting_admission)
        return

    # Check if user is ALREADY a channel member
    user_is_member = await is_channel_member(bot, user_id)

    if user_is_member:
        searching_msg = await message.answer(
            msg.SEARCHING,
            parse_mode=ParseMode.HTML,
        )
        result = await eaes_client.check_result(admission_no, first_name)
        await safe_delete_message(searching_msg)
        await render_result_response(message, bot, result, admission_no, first_name)
        await state.clear()
    else:
        # Pre-fetch result in background
        import asyncio
        asyncio.create_task(eaes_client.check_result(admission_no, first_name))

        await state.update_data(
            admission_no=admission_no,
            first_name=first_name,
        )

        join_url = await get_in_app_join_link(bot)
        await message.answer(
            msg.format_transition_gate(admission_no, first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=transition_gate_keyboard(join_url),
            disable_web_page_preview=True,
        )
        await state.set_state(ResultForm.waiting_transition_unlock)


# ── "Show My Result" Callback (with Native Modal Alert) ─────────────────────────

@router.callback_query(F.data == "show_result_after_join")
async def cb_show_result_after_join(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Handle the 'Show My Result' button tap after user joins channel."""
    user_id = callback.from_user.id if callback.from_user else 0

    # Invalidate cache to force a real check
    membership_cache.delete(f"member:{user_id}")

    if not await is_channel_member(bot, user_id):
        # Native modal dialog popup alert!
        await callback.answer(
            "⚠️ Please tap 'Join Channel' first to unlock your result!",
            show_alert=True,
        )
        return

    # Acknowledge callback cleanly
    await callback.answer("🎉 Unlocking your result...")

    data = await state.get_data()
    admission_no = data.get("admission_no", "")
    first_name = data.get("first_name", "")

    result = await eaes_client.check_result(admission_no, first_name)
    await render_result_response(callback.message, bot, result, admission_no, first_name, edit=True)
    await state.clear()


# ── Catch-all for unsolicited inputs ──────────────────────────────────────────

@router.message()
async def handle_unknown(message: Message, state: FSMContext):
    """Handle unexpected messages by prompting /start."""
    await message.answer(
        "💡 Send <b>/start</b> to check your result.\n"
        "💡 ውጤትህን/ሽን ለማየት <b>/start</b> ላክ/ኪ።",
        parse_mode=ParseMode.HTML,
    )
