"""
FreshMinds Invite Competition Bot — Live Leaderboard Handler
"""

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from database import db
from config import is_admin
from handlers.utils import check_and_credit_membership, send_feature_lock_message
import messages as msg

router = Router()


async def show_leaderboard(target: Message | CallbackQuery, user):
    """Render real-time Leaderboard with personal rank comparison."""
    comp = await db.get_active_competition()
    if not comp:
        text = msg.NO_ACTIVE_COMPETITION_TEXT
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text, parse_mode=ParseMode.HTML)
        else:
            await target.answer(text, parse_mode=ParseMode.HTML)
        return

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
        is_admin=is_admin(user.id),
        competition_title=comp.title,
    )

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            leaderboard_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    else:
        await target.answer(
            leaderboard_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )



@router.message(F.text == msg.BTN_LEADERBOARD)
@router.message(Command("leaderboard"))
@router.message(Command("top"))
async def handle_leaderboard(message: Message, bot: Bot):
    """Render real-time Leaderboard — gated behind channel membership."""
    user = message.from_user
    if not user:
        return

    if not await check_and_credit_membership(bot, user):
        await send_feature_lock_message(message, "🏆 የሳምንቱን ደረጃ", "retry_feature_lb")
        return

    await show_leaderboard(message, user)


@router.callback_query(F.data == "retry_feature_lb")
async def handle_retry_leaderboard(callback: CallbackQuery, bot: Bot):
    """Retry handler for leaderboard after user joins channel."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await show_leaderboard(callback, callback.from_user)
