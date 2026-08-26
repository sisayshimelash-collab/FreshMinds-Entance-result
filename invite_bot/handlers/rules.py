"""
FreshMinds Invite Competition Bot — Rules & Prizes Handler
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
import messages as msg

router = Router()


@router.message(F.text == msg.BTN_RULES)
@router.message(Command("rules"))
@router.message(Command("prizes"))
async def handle_rules(message: Message):
    """Display weekly prizes, rules, anti-cheat policies, and award info."""
    await message.answer(
        msg.RULES_TEXT,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
