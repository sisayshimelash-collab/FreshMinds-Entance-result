"""
FreshMinds Invite Competition Bot — Main Entrypoint
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, TARGET_CHANNEL
from database import db
from handlers import setup_routers

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("invite_bot")


async def on_startup(bot: Bot):
    """Actions performed on bot initialization."""
    # 1. Initialize SQLite Database Tables
    await db.init_db()

    bot_info = await bot.get_me()
    logger.info(
        f"FreshMinds Invite Bot started as @{bot_info.username} (ID: {bot_info.id})"
    )
    logger.info(f"Monitoring channel joins for: @{TARGET_CHANNEL}")


async def on_shutdown(bot: Bot):
    """Actions performed on bot shutdown."""
    logger.info("FreshMinds Invite Bot is shutting down...")


async def main():
    """Main application loop."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing! Please set it in .env file.")
        sys.exit(1)

    # Initialize Bot & Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register Routers
    dp.include_router(setup_routers())

    # Startup & Shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Allowed updates must include 'chat_member' for channel tracking
    allowed_updates = ["message", "chat_member", "callback_query"]

    logger.info("Starting long-polling loop...")
    await dp.start_polling(
        bot,
        allowed_updates=allowed_updates,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
