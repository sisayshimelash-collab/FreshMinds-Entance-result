"""
FreshMinds Invite Competition Bot — Start & Main Menu Handler
"""

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.enums import ParseMode
from database import db
import messages as msg

router = Router()


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom reply keyboard for easy 1-tap navigation."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=msg.BTN_GET_LINK)],
            [
                KeyboardButton(text=msg.BTN_MY_STATS),
                KeyboardButton(text=msg.BTN_LEADERBOARD),
            ],
            [KeyboardButton(text=msg.BTN_RULES)],
        ],
        resize_keyboard=True,
        persistent=True,
    )


@router.message(CommandStart())
async def handle_start(message: Message):
    """Handle /start command — registers student and opens main menu."""
    user = message.from_user
    if not user:
        return

    # Register or update student in DB
    await db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    await message.answer(
        msg.WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(Command("help"))
async def handle_help(message: Message):
    """Handle /help command."""
    await message.answer(
        msg.WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True,
    )
