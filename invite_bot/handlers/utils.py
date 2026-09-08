"""
FreshMinds Invite Bot — Shared Handler Utilities
"""

import logging
from aiogram import Bot
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import TARGET_CHANNEL, TARGET_CHANNEL_ID
from database import db
import messages as msg

logger = logging.getLogger(__name__)


async def check_channel_membership(bot: Bot, user_id: int) -> bool:
    """Check if a user is currently a member of the target channel."""
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


async def check_and_credit_membership(bot: Bot, user) -> bool:
    """Checks membership; if joined and user had a pending referrer, credits referrer immediately."""
    is_member = await check_channel_membership(bot, user.id)
    if is_member:
        pending_ref = await db.get_pending_referrer(user.id)
        if pending_ref:
            await db.clear_pending_referrer(user.id)
            comp = await db.get_active_competition()
            if not comp:
                return is_member

            credited = await db.record_referral(
                referrer_id=pending_ref,
                referred_user_id=user.id,
                invite_link=f"bot_deep_link_{pending_ref}",
            )

            if credited:
                active_points, total_joins, rank = await db.get_user_stats(pending_ref)
                try:
                    await bot.send_message(
                        chat_id=pending_ref,
                        text=msg.format_join_notification(
                            friend_name=user.first_name,
                            active_points=active_points,
                            rank=rank,
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                except Exception as e:
                    logger.warning(f"Could not notify referrer {pending_ref}: {e}")
    return is_member


def get_feature_lock_keyboard(retry_callback: str) -> InlineKeyboardMarkup:
    """Inline keyboard for membership locked features."""
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
                    text="✅ ተቀላቅያለሁ (ክፈት / Unlock)",
                    callback_data=retry_callback,
                )
            ],
        ]
    )


async def send_feature_lock_message(
    target: Message | CallbackQuery,
    feature_name: str,
    retry_callback: str,
):
    """Sends a standardized lock prompt when user tries to use a feature without joining channel."""
    text = (
        f"🔒 <b>{feature_name}ን ለመጠቀም የ ቻናላችን ቤተሰብ ይሁኑ!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"የ <b>Freshman Super Bot</b> የኮርስ ማቴሪያሎች፣ የዩኒቨርሲቲዎች መረጃ፣ GPA ማስያ እና ሌሎች አገልግሎቶችን በነፃ ለማግኘት "
        f"እባክዎ መጀመሪያ ይፋዊ የቴሌግራም ቻናላችንን ይቀላቀሉ:\n\n"
        f"1️⃣ ከታች ያለውን <b>'@{TARGET_CHANNEL} ቻናል ተቀላቀል'</b> ይጫኑ\n"
        f"2️⃣ ቻናሉን ከተቀላቀሉ በኋላ <b>'ተቀላቅያለሁ (ክፈት)'</b> የሚለውን ይጫኑ!"
    )
    markup = get_feature_lock_keyboard(retry_callback)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            text, parse_mode=ParseMode.HTML, reply_markup=markup, disable_web_page_preview=True
        )
    else:
        await target.answer(
            text, parse_mode=ParseMode.HTML, reply_markup=markup, disable_web_page_preview=True
        )
