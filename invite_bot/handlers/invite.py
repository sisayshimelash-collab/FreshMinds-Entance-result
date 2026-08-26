"""
FreshMinds Invite Competition Bot — Invite Link & Promotional Post Generator
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
        "🎓 ለ 2018 ዓ.ም የ Freshman ተማሪዎች በሙሉ! ነፃ የቪዲዮ ኮርሶች እና የፈተና ሞዴሎች በ FreshMinds Academy ያግኙ። አሁኑኑ ይቀላቀሉ👇"
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


@router.message(F.text == msg.BTN_GET_LINK)
@router.message(Command("link"))
@router.message(Command("invite"))
@router.message(Command("newlink"))
async def handle_get_link(message: Message, bot: Bot):
    """Generate unique bulletproof referral link and send promo kit."""
    user = message.from_user
    if not user:
        return

    # 1. Fetch or create user in DB
    await db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    # 2. Build 100% reliable Bot Deep-Link
    bot_info = await bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start=ref_{user.id}"
    await db.set_user_invite_link(user.id, invite_link)

    # 3. Send Ready-to-Forward Promotional Marketing Post
    promo_post = msg.format_promotional_post(invite_link)
    await message.answer(
        promo_post,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    # 4. Send 1-Tap Copyable Link Card with Share Button
    link_card = msg.format_link_card(invite_link)
    await message.answer(
        link_card,
        parse_mode=ParseMode.HTML,
        reply_markup=get_share_keyboard(invite_link),
        disable_web_page_preview=True,
    )
