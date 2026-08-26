"""
FreshMinds Invite Competition Bot — Handlers Registration
"""

from aiogram import Router
from .start import router as start_router
from .invite import router as invite_router
from .tracker import router as tracker_router
from .stats import router as stats_router
from .leaderboard import router as leaderboard_router
from .rules import router as rules_router
from .admin import router as admin_router


def setup_routers() -> Router:
    main_router = Router()
    main_router.include_router(tracker_router)  # ChatMemberUpdated priority
    main_router.include_router(admin_router)
    main_router.include_router(start_router)
    main_router.include_router(invite_router)
    main_router.include_router(stats_router)
    main_router.include_router(leaderboard_router)
    main_router.include_router(rules_router)
    return main_router
