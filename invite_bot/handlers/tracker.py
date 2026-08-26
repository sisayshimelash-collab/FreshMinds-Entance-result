"""
FreshMinds Invite Competition Bot — Real-Time Join & Leave Event Tracker
"""

import logging
from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus, ParseMode
from database import db
import messages as msg

logger = logging.getLogger(__name__)
router = Router()


@router.chat_member()
async def handle_channel_chat_member_update(event: ChatMemberUpdated, bot: Bot):
    """
    Listens to real-time ChatMemberUpdated events directly on the target channel.
    Tracks both new member joins and member departures.
    """
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status
    joining_user = event.new_chat_member.user

    # Ignore bots
    if joining_user.is_bot:
        return

    # ── 1. MEMBER JOINED CHANNEL ──────────────────────────────────────────────
    is_join = old_status in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.KICKED,
        ChatMemberStatus.RESTRICTED,
    ) and new_status in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    )

    if is_join:
        invite_link_obj = event.invite_link
        if not invite_link_obj:
            logger.info(
                f"User {joining_user.id} ({joining_user.first_name}) joined via direct public link or search."
            )
            return

        invite_link_str = invite_link_obj.invite_link
        link_name = invite_link_obj.name or ""

        # Identify referrer: By exact link match or link name (ref_<user_id>)
        referrer = await db.get_user_by_invite_link(invite_link_str)
        referrer_id = None

        if referrer:
            referrer_id = referrer.user_id
        elif link_name.startswith("ref_") and link_name[4:].isdigit():
            referrer_id = int(link_name[4:])

        if not referrer_id:
            logger.warning(
                f"No referrer matched for invite link: {invite_link_str} (name: {link_name})"
            )
            return

        # Attempt to credit referral (Enforces 1 credit per lifetime user, no self-referral)
        credited = await db.record_referral(
            referrer_id=referrer_id,
            referred_user_id=joining_user.id,
            invite_link=invite_link_str,
        )

        if credited:
            logger.info(
                f"Referral SUCCESS: User {joining_user.id} credited to Referrer {referrer_id}"
            )
            # Fetch updated stats for inviter
            active_points, total_joins, rank = await db.get_user_stats(
                referrer_id
            )

            # Send instant push notification to inviter
            try:
                await bot.send_message(
                    chat_id=referrer_id,
                    text=msg.format_join_notification(
                        friend_name=joining_user.first_name,
                        active_points=active_points,
                        rank=rank,
                    ),
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                logger.warning(
                    f"Could not send join notification to referrer {referrer_id}: {e}"
                )
        else:
            logger.info(
                f"Duplicate join: User {joining_user.id} already counted in the past."
            )

    # ── 2. MEMBER LEFT CHANNEL (ANTI-CHEAT DEDUCTION) ─────────────────────────
    is_leave = old_status in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.RESTRICTED,
    ) and new_status in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.KICKED,
    )

    if is_leave:
        leaving_user = event.new_chat_member.user
        referrer_id = await db.handle_member_leave(leaving_user.id)

        if referrer_id:
            logger.info(
                f"Member left: User {leaving_user.id} left. -1 point from referrer {referrer_id}"
            )
            active_points, _, _ = await db.get_user_stats(referrer_id)

            # Send leave notice to inviter
            try:
                await bot.send_message(
                    chat_id=referrer_id,
                    text=msg.format_leave_notification(
                        friend_name=leaving_user.first_name,
                        active_points=active_points,
                    ),
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                logger.warning(
                    f"Could not send leave notification to referrer {referrer_id}: {e}"
                )
