"""
FreshMinds Invite Competition Bot — Referral Link & Promotional Post Generator
"""

import logging
import urllib.parse
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from database import db
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


def get_share_keyboard(invite_link: str) -> InlineKeyboardMarkup:
    """Inline button that opens Telegram share picker with pre-filled promotional message."""
    share_text = (
        "🎓 ለ 2019 ዓ.ም የ Freshman ተማሪዎች በሙሉ! ነፃ የቪዲዮ ኮርሶች እና የፈተና ሞዴሎች በ FreshMinds Academy ያግኙ። አሁኑኑ ይቀላቀሉ👇"
    )
    encoded_text = urllib.parse.quote(share_text)
    encoded_url = urllib.parse.quote(invite_link)
    telegram_share_url = (
        f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ለጓደኞችህ/ሽ አጋራ (Share with Friends)",
                    url=telegram_share_url,
                )
            ]
        ]
    )


from handlers.utils import check_and_credit_membership, send_feature_lock_message

async def generate_and_send_link(target: Message | CallbackQuery, bot: Bot, user):
    """Generates and sends the referral link and promo post to the user."""
    # 1. Fetch user from DB
    await db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    # 2. Build 100% reliable Bot Deep-Link
    bot_info = await bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start=ref_{user.id}"
    await db.set_user_invite_link(user.id, invite_link)
    logger.info(f"Generated referral link for user {user.id}: {invite_link}")

    # 3. Send Ready-to-Forward Promotional Marketing Post
    promo_post = msg.format_promotional_post(invite_link)
    link_card = msg.format_link_card(invite_link)

    chat_id = target.chat.id if isinstance(target, Message) else target.message.chat.id

    await bot.send_message(
        chat_id=chat_id,
        text=promo_post,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await bot.send_message(
        chat_id=chat_id,
        text=link_card,
        parse_mode=ParseMode.HTML,
        reply_markup=get_share_keyboard(invite_link),
        disable_web_page_preview=True,
    )


@router.message(F.text == msg.BTN_GET_LINK)
@router.message(Command("link"))
@router.message(Command("invite"))
@router.message(Command("newlink"))
async def handle_get_link(message: Message, bot: Bot):
    """Generate or retrieve bulletproof bot referral deep link — gated behind channel membership."""
    user = message.from_user
    if not user:
        return

    if not await check_and_credit_membership(bot, user):
        await send_feature_lock_message(message, "🔗 የመጋበዣ ሊንክ ማውጫን", "retry_feature_link")
        return

    await generate_and_send_link(message, bot, user)


@router.callback_query(F.data == "retry_feature_link")
async def handle_retry_link(callback: CallbackQuery, bot: Bot):
    """Retry handler for referral link generation after user joins channel."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await generate_and_send_link(callback, bot, callback.from_user)

