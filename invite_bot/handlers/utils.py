"""
FreshMinds Invite Bot — Shared Handler Utilities
"""

import logging
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from config import TARGET_CHANNEL_ID

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
