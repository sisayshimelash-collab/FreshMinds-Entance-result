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
        referrer_id = None
        invite_link_str = ""

        if invite_link_obj:
            invite_link_str = invite_link_obj.invite_link
            link_name = invite_link_obj.name or ""
            referrer = await db.get_user_by_invite_link(invite_link_str)
            if referrer:
                referrer_id = referrer.user_id
            elif link_name.startswith("ref_") and link_name[4:].isdigit():
                referrer_id = int(link_name[4:])

        # Fallback: Check if user started bot via referral link before joining channel
        if not referrer_id:
            pending_ref_id = await db.get_pending_referrer(joining_user.id)
            if pending_ref_id:
                referrer_id = pending_ref_id
                invite_link_str = f"bot_deep_link_{referrer_id}"
                await db.clear_pending_referrer(joining_user.id)
                logger.info(
                    f"Auto-detected pending referral: User {joining_user.id} -> Referrer {referrer_id}"
                )

        if not referrer_id:
            logger.info(
                f"User {joining_user.id} ({joining_user.first_name}) joined via direct public username or search without referral."
            )
            return

        # Attempt to credit referral (Enforces 1 credit per lifetime user, no self-referral)
        credited = await db.record_referral(
            referrer_id=referrer_id,
            referred_user_id=joining_user.id,
            invite_link=invite_link_str or f"ref_{referrer_id}",
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
    Listens to ChatJoinRequest events from direct channel invite links (t.me/+...).
    Auto-approves and credits the referrer in real-time.
    """
    user = join_req.from_user
    invite_link_obj = join_req.invite_link

    invite_link_str = invite_link_obj.invite_link if invite_link_obj else "None"
    link_name = invite_link_obj.name or "" if invite_link_obj else ""

    logger.info(
        f"[JoinRequestEvent] User: {user.id} ({user.first_name}) | Link: {invite_link_str} | Name: {link_name}"
    )

    # 1. Auto-approve user into the channel immediately
    try:
        await bot.approve_chat_join_request(
            chat_id=join_req.chat.id,
            user_id=user.id,
        )
        logger.info(f"Auto-approved join request for user {user.id} in chat {join_req.chat.id}")
    except Exception as e:
        logger.warning(f"Failed to auto-approve join request for {user.id}: {e}")

    if not invite_link_obj:
        logger.warning(f"Join request from user {user.id} has no invite_link attached.")
        return

    # 2. Identify referrer by link name (ref_<user_id>) or exact DB link match
    referrer_id = None
    if link_name.startswith("ref_") and link_name[4:].isdigit():
        referrer_id = int(link_name[4:])
    
    if not referrer_id:
        referrer = await db.get_user_by_invite_link(invite_link_str)
        if referrer:
            referrer_id = referrer.user_id

    if not referrer_id:
        logger.warning(
            f"No referrer found for join request link: {invite_link_str} (name: {link_name})"
        )
        return

    # 3. Credit referral to inviter (1 credit per lifetime account, no self-referral)
    credited = await db.record_referral(
        referrer_id=referrer_id,
        referred_user_id=user.id,
        invite_link=invite_link_str,
    )

    if credited:
        logger.info(
            f"🎉 Direct Channel Join Referral SUCCESS: User {user.id} credited to Referrer {referrer_id}"
        )
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
        except Exception as e:
            logger.warning(
                f"Could not send join notification to referrer {referrer_id}: {e}"
            )
    else:
        logger.info(
            f"Join request user {user.id} already credited previously or self-referral."
        )
