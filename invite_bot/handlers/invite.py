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
from config import TARGET_CHANNEL_ID
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
async def handle_get_link(message: Message, bot: Bot):
    """Generate or retrieve unique direct channel invite link and send promo kit."""
    user = message.from_user
    if not user:
        return

    # 1. Fetch user from DB
    user_record = await db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    invite_link = user_record.invite_link

    # 2. If no link exists yet, create one natively via Telegram API (with join request for 100% reliable tracking)
    if not invite_link:
        try:
            link_obj = await bot.create_chat_invite_link(
                chat_id=TARGET_CHANNEL_ID,
                name=f"ref_{user.id}",
                creates_join_request=True,
            )
            invite_link = link_obj.invite_link
            await db.set_user_invite_link(user.id, invite_link)
            logger.info(
                f"Generated new channel invite link for user {user.id}: {invite_link}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create channel invite link for user {user.id}: {e}"
            )
            await message.answer(
                "⚠️ <b>ይቅርታ፣ የመጋበዣ ሊንክ ማመንጨት አልተቻለም!</b>\n"
                "እባክዎ ቦቱ በቻናሉ ላይ የአድሚን (Admin) ፍቃድ እንዳለው ያረጋግጡ።",
                parse_mode=ParseMode.HTML,
            )
            return

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
