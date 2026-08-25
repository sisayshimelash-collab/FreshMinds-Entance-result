"""
FreshMinds Result Bot — High-Performance Entry Point

Features:
- Background cache & rate-limiter cleanup loop to guarantee bounded memory usage
- Optimized Telegram polling filter (allowed_updates)
- Graceful shutdown for HTTP connection pools and Telegram session
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ensure bot directory is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import BOT_TOKEN
from eaes_client import EAESClient
from rate_limiter import RateLimiter
import handlers


# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("freshminds_bot")


# ── Periodic Maintenance Loop ────────────────────────────────────────────────

async def maintenance_worker(rate_limiter: RateLimiter, eaes_client: EAESClient, interval: int = 180):
    """
    Background worker that purges expired cache and rate limit entries
    to prevent memory buildup during peak traffic.
    """
    while True:
        try:
            await asyncio.sleep(interval)
            rate_limiter.cleanup()
            handlers.membership_cache.cleanup()
            eaes_client._result_cache.cleanup()
            logger.debug("Periodic memory cleanup completed.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"Maintenance loop warning: {e}")


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    """Initialize and start the high-throughput bot service."""

    # Validate config
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logger.error(
            "BOT_TOKEN is not set!\n"
            "1. Copy .env.example to .env\n"
            "2. Replace 'your_bot_token_here' with your actual bot token from @BotFather"
        )
        sys.exit(1)

    # Initialize components
    eaes_client = EAESClient(
        max_concurrent_requests=50,
        result_cache_ttl=600.0,
        not_released_cache_ttl=30.0,
    )
    rate_limiter = RateLimiter(max_requests=4, window_seconds=60)
    handlers.init(eaes_client, rate_limiter)

    # Create bot & dispatcher with optimized storage
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router)

    logger.info("=" * 60)
    logger.info("FreshMinds Result Bot (High-Throughput Mode) starting...")
    logger.info("=" * 60)

    # Start EAES HTTP client pool
    await eaes_client.start()

    # Start background cleanup task
    cleaner_task = asyncio.create_task(maintenance_worker(rate_limiter, eaes_client))

    try:
        # Register bot commands
        await bot.set_my_commands([
            BotCommand(command="start", description="Check your result / ውጤትህን ፈልግ"),
        ])

        # Start polling with update filtering for high throughput & modal pop-up events
        logger.info("Bot is running! Press Ctrl+C to stop.")
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query", "chat_join_request"],
            handle_signals=True,
        )

    finally:
        cleaner_task.cancel()
        await eaes_client.close()
        await bot.session.close()
        logger.info("Bot stopped cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
