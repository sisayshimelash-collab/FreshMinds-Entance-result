"""
FreshMinds Invite Competition Bot — Personal Statistics Handler
"""

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from database import db
from handlers.utils import check_and_credit_membership, send_feature_lock_message
import messages as msg

router = Router()


async def show_stats(target: Message | CallbackQuery, user):
    """Fetch and display personal competition score, invites count, and rank."""
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

    active_points, total_joins, rank = await db.get_user_stats(user.id)

    stats_card = msg.format_stats_card(
        first_name=user.first_name,
        active_points=active_points,
        total_joins=total_joins,
        rank=rank,
    )

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            stats_card,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    else:
        await target.answer(
            stats_card,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )



@router.message(F.text == msg.BTN_MY_STATS)
@router.message(Command("stats"))
@router.message(Command("my_stats"))
async def handle_my_stats(message: Message, bot: Bot):
    """Fetch and display personal stats — gated behind channel membership."""
    user = message.from_user
    if not user:
        return

    if not await check_and_credit_membership(bot, user):
        await send_feature_lock_message(message, "📊 የእርስዎን ውጤት", "retry_feature_stats")
        return

    await show_stats(message, user)


@router.callback_query(F.data == "retry_feature_stats")
async def handle_retry_stats(callback: CallbackQuery, bot: Bot):
    """Retry handler for stats after user joins channel."""
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await show_stats(callback, callback.from_user)
