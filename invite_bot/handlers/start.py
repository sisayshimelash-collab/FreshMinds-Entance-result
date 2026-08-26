"""
FreshMinds Invite Competition Bot — Start & Referral Verification Handler
"""

import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode, ChatMemberStatus
from database import db
from config import TARGET_CHANNEL, TARGET_CHANNEL_ID
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom reply keyboard for easy 1-tap navigation."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=msg.BTN_GET_LINK)],
            [
                KeyboardButton(text=msg.BTN_MY_STATS),
                KeyboardButton(text=msg.BTN_LEADERBOARD),
            ],
            [KeyboardButton(text=msg.BTN_RULES)],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def get_channel_join_markup(referrer_id: int) -> InlineKeyboardMarkup:
    """Markup prompting user to join channel and verify referral."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል",
                    url=f"https://t.me/{TARGET_CHANNEL}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ ተቀላቅያለሁ አረጋግጥ (Verify Membership)",
                    callback_data=f"verify_{referrer_id}",
                )
            ],
        ]
    )


async def check_channel_membership(bot: Bot, user_id: int) -> bool:
    """Check if user is currently a member of the target channel."""
    try:
        member = await bot.get_chat_member(
            chat_id=TARGET_CHANNEL_ID, user_id=user_id
        )
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        )
    except Exception as e:
        logger.warning(f"Failed to check channel membership for {user_id}: {e}")
        return False


async def credit_and_notify_referrer(
    bot: Bot, referrer_id: int, joining_user, invite_link_str: str = ""
):
    """Credit +1 referral point to referrer and send instant push notification."""
    credited = await db.record_referral(
        referrer_id=referrer_id,
        referred_user_id=joining_user.id,
        invite_link=invite_link_str or f"ref_{referrer_id}",
    )
    if credited:
        logger.info(
            f"🎉 Referral SUCCESS: User {joining_user.id} credited to Referrer {referrer_id}"
        )
        active_points, total_joins, rank = await db.get_user_stats(referrer_id)
        try:
            await bot.send_message(
                chat_id=referrer_id,
                text=msg.format_join_notification(
                    friend_name=joining_user.first_name,
                    active_points=active_points,
                    rank=rank,
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.warning(
                f"Could not send join notification to referrer {referrer_id}: {e}"
            )
        return True
    return False


@router.message(CommandStart())
async def handle_start(message: Message, bot: Bot):
    """Handle /start command — registers student and processes referral payload."""
    user = message.from_user
    if not user:
        return

    # Register or update user in DB
    await db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    # Check for referral payload (e.g. /start ref_12345678 or /start 12345678)
    referrer_id = None
    args = message.text.split()
    if len(args) > 1:
        payload = args[1].strip()
        if payload.startswith("ref_") and payload[4:].isdigit():
            referrer_id = int(payload[4:])
        elif payload.isdigit():
            referrer_id = int(payload)

    # If joined via a referral link and not self
    if referrer_id and referrer_id != user.id:
        is_member = await check_channel_membership(bot, user.id)
        if is_member:
            # Already in channel -> credit immediately
            await credit_and_notify_referrer(bot, referrer_id, user)
            await message.answer(
                f"✅ <b>ተሳትፎዎ ተረጋግጧል!</b>\n\n"
                f"ለ <b>@{TARGET_CHANNEL}</b> ሳምንታዊ ውድድር በተሳካ ሁኔታ ተመዝግበዋል።\n"
                "የራስዎን መጋበዣ ሊንክ አውጥተው ጓደኞችዎን በመጋበዝ አሸናፊ ይሁኑ!",
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_menu_keyboard(),
            )
            return
        else:
            # Prompt to join channel first
            await message.answer(
                f"👋 <b>እንኳን ወደ {msg.COMPETITION_TITLE} በደህና መጡ!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"ተሳትፎዎን ለማረጋገጥ እና ለጋባዥዎ ነጥብ ለማስመዝገብ እባክዎ መጀመሪያ <b>@{TARGET_CHANNEL}</b> ቻናልን ይቀላቀሉ:\n\n"
                "👇 ከታች <b>'ቻናል ተቀላቀል'</b> የሚለውን ተጭነው ከገቡ በኋላ <b>'ተቀላቅያለሁ አረጋግጥ'</b> የሚለውን ይጫኑ!",
                parse_mode=ParseMode.HTML,
                reply_markup=get_channel_join_markup(referrer_id),
                disable_web_page_preview=True,
            )
            return

    # Standard Welcome
    await message.answer(
        msg.WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("verify_"))
async def handle_verify_callback(callback: CallbackQuery, bot: Bot):
    """Handle verification button tap when user joins channel."""
    user = callback.from_user
    if not user:
        return

    referrer_str = callback.data.partition("_")[2]
    if not referrer_str.isdigit():
        return

    referrer_id = int(referrer_str)

    # Check channel membership
    is_member = await check_channel_membership(bot, user.id)

    if not is_member:
        await callback.answer(
            f"⚠️ እባክዎ መጀመሪያ @{TARGET_CHANNEL} ቻናልን ይቀላቀሉ!", show_alert=True
        )
        return

    # Successfully verified
    await callback.answer("✅ ተሳትፎዎ ተረጋግጧል! እናመሰግናለን።", show_alert=True)
    await credit_and_notify_referrer(bot, referrer_id, user)

    try:
        await callback.message.edit_text(
            f"🎉 <b>ተሳትፎዎ በሚገባ ተረጋግጧል!</b>\n\n"
            f"የ <b>@{TARGET_CHANNEL}</b> ቤተሰብ ስለሆኑ እናመሰግናለን!\n"
            "እርስዎም የራስዎን መጋበዣ ሊንክ አውጥተው ጓደኞችዎን በመጋበዝ ሽልማቶችን ያሸንፉ! 👇",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    await callback.message.answer(
        msg.WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(Command("help"))
async def handle_help(message: Message):
    """Handle /help command."""
    await message.answer(
        msg.WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True,
    )
