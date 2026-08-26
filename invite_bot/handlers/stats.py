"""
FreshMinds Invite Competition Bot — Personal Statistics Handler
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from database import db
import messages as msg

router = Router()


@router.message(F.text == msg.BTN_MY_STATS)
@router.message(Command("stats"))
@router.message(Command("my_stats"))
async def handle_my_stats(message: Message):
    """Fetch and display personal competition score, invites count, and rank."""
    user = message.from_user
    if not user:
        return

    # Ensure user exists in DB
    await db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    active_points, total_joins, rank = await db.get_user_stats(user.id)

    stats_card = msg.format_stats_card(
        first_name=user.first_name,
        active_points=active_points,
        total_joins=total_joins,
        rank=rank,
    )

    await message.answer(
        stats_card,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
