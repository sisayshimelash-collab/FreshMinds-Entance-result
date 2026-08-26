"""
FreshMinds Invite Competition Bot — Live Leaderboard Handler
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from database import db
import messages as msg

router = Router()


@router.message(F.text == msg.BTN_LEADERBOARD)
@router.message(Command("leaderboard"))
@router.message(Command("top"))
async def handle_leaderboard(message: Message):
    """Render real-time Top 10 Leaderboard with personal rank comparison."""
    user = message.from_user
    if not user:
        return

    # Ensure user exists in DB
    await db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    top_users = await db.get_top_leaderboard(limit=4)
    my_points, _, my_rank = await db.get_user_stats(user.id)

    leaderboard_text = msg.format_leaderboard(
        top_users=top_users,
        my_rank=my_rank,
        my_points=my_points,
    )

    await message.answer(
        leaderboard_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
