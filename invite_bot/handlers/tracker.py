"""
FreshMinds Invite Competition Bot — Real-Time Join & Leave Event Tracker
"""

import logging
from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated, ChatJoinRequest
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

    logger.info(
        f"[ChatMemberEvent] User: {joining_user.id} ({joining_user.first_name}) | "
        f"Transition: {old_status} -> {new_status} | "
        f"InviteLink: {event.invite_link.invite_link if event.invite_link else 'None'} | "
        f"LinkName: {event.invite_link.name if event.invite_link else 'None'}"
    )

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
                f"User {joining_user.id} ({joining_user.first_name}) joined via direct public username or search."
            )
            return

        invite_link_str = invite_link_obj.invite_link
        link_name = invite_link_obj.name or ""

        # Identify referrer: By exact link match, URL hash match, or link name (ref_<user_id>)
        referrer = await db.get_user_by_invite_link(invite_link_str)
        referrer_id = None

        if referrer:
            referrer_id = referrer.user_id
        elif link_name.startswith("ref_") and link_name[4:].isdigit():
            referrer_id = int(link_name[4:])

        if not referrer_id:
            logger.warning(
                f"No referrer found for invite link: {invite_link_str} (name: {link_name})"
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
                f"🎉 Referral SUCCESS: User {joining_user.id} credited to Referrer {referrer_id}"
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
                f"Duplicate or self-join: User {joining_user.id} not credited (already in database or self-click)."
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
                f"Member left: User {leaving_user.id} left channel. -1 point deducted from referrer {referrer_id}"
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


@router.chat_join_request()
async def handle_chat_join_request(join_req: ChatJoinRequest, bot: Bot):
    """
    Listens to ChatJoinRequest events if the channel has join request approval mode.
    Auto-approves and credits the referrer in real-time.
    """
    user = join_req.from_user
    invite_link_obj = join_req.invite_link

    logger.info(
        f"[JoinRequestEvent] User: {user.id} ({user.first_name}) | "
        f"InviteLink: {invite_link_obj.invite_link if invite_link_obj else 'None'}"
    )

    # Auto-approve user into the channel
    try:
        await bot.approve_chat_join_request(
            chat_id=join_req.chat.id,
            user_chat_id=user.id,
        )
    except Exception as e:
        logger.warning(f"Failed to auto-approve join request for {user.id}: {e}")

    if not invite_link_obj:
        return

    invite_link_str = invite_link_obj.invite_link
    link_name = invite_link_obj.name or ""

    referrer = await db.get_user_by_invite_link(invite_link_str)
    referrer_id = None

    if referrer:
        referrer_id = referrer.user_id
    elif link_name.startswith("ref_") and link_name[4:].isdigit():
        referrer_id = int(link_name[4:])

    if not referrer_id:
        return

    credited = await db.record_referral(
        referrer_id=referrer_id,
        referred_user_id=user.id,
        invite_link=invite_link_str,
    )

    if credited:
        active_points, total_joins, rank = await db.get_user_stats(referrer_id)
        try:
            await bot.send_message(
                chat_id=referrer_id,
                text=msg.format_join_notification(
                    friend_name=user.first_name,
                    active_points=active_points,
                    rank=rank,
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
