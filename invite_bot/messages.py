"""
FreshMinds Invite Competition Bot — Message Templates (Amharic & English)
"""

from config import (
    TARGET_CHANNEL,
    COMPETITION_TITLE,
    PRIZE_1ST,
    PRIZE_2ND,
    PRIZE_3RD,
    PRIZE_4TH_10TH,
)

# ── Main Menu Keyboard Labels ────────────────────────────────────────────────
BTN_GET_LINK = "🔗 የእኔ መጋበዣ ሊንክ (My Link)"
BTN_MY_STATS = "📊 የእኔ ውጤት (My Stats)"
BTN_LEADERBOARD = "🏆 የሳምንቱ ደረጃ (Leaderboard)"
BTN_RULES = "🎁 ሽልማቶችና ህጎች (Prizes & Rules)"

# ── Welcome / Start Message ──────────────────────────────────────────────────
WELCOME_TEXT = (
    f"🎉 <b>እንኳን ወደ {COMPETITION_TITLE} በደህና መጡ!</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    f"ጓደኞችዎን ወደ <b>@{TARGET_CHANNEL}</b> በመጋበዝ ከፍተኛ ተሸላሚ ይሁኑ!\n\n"
    "🎁 <b>የሳምንቱ ሽልማቶች:</b>\n"
    f"🥇 1ኛ: <b>{PRIZE_1ST}</b>\n"
    f"🥈 2ኛ: <b>{PRIZE_2ND}</b>\n"
    f"🥉 3ኛ: <b>{PRIZE_3RD}</b>\n"
    f"🎖️ 4ኛ - 10ኛ: <b>{PRIZE_4TH_10TH}</b>\n\n"
    "👇 የራስዎን ልዩ መጋበዣ ሊንክ ለማግኘት ከታች <b>'🔗 የእኔ መጋበዣ ሊንክ'</b> የሚለውን ይጫኑ!"
)


# ── Ready-to-Forward Promotional Marketing Post ──────────────────────────────
def format_promotional_post(invite_link: str) -> str:
    """
    Complete, attractive promotional post that students can directly
    forward to Telegram groups, batch channels, or friends.
    """
    return (
        "🎓 <b>ለ 2018 ዓ.ም የዩኒቨርሲቲ Freshman ተማሪዎች በሙሉ!</b> 🇪🇹\n\n"
        "ለ 1ኛ አመት (Freshman) የዩኒቨርሲቲ ህይወትህ/ሽ በሚገባ ተዘጋጅተሃል/ሻል? "
        "<b>FreshMinds Academy</b> ለተማሪዎች የተዘጋጀ ልዩ የትምህርት ማዕከል ነው!\n\n"
        "📌 <b>በቻናላችን ምን ያገኛሉ?</b>\n"
        "📚 <b>ነፃ የ Freshman የቪዲዮ ኮርሶች</b> (Applied Maths, General Physics, Chemistry, Economics...)\n"
        "📝 <b>የዩኒቨርሲቲ ፈተና ሞዴሎች</b> እና የማጠቃለያ ኖቶች (Summary Handouts)\n"
        "🏛️ <b>የዩኒቨርሲቲ ምደባ</b> እና የዲፓርትመንት መረጣ መረጃዎች\n"
        "📱 <b>FreshMinds Mobile App</b> (በቅርቡ የሚለቀቅ)\n\n"
        "👇 <b>አሁኑኑ ቻናሉን ይቀላቀሉ:</b>\n"
        f"{invite_link}\n\n"
        f"@{TARGET_CHANNEL}"
    )


# ── Link Card (Instructions & 1-Tap Copyable URL) ────────────────────────────
def format_link_card(invite_link: str) -> str:
    """Delivers 1-tap copyable monospace URL and sharing instructions."""
    return (
        "🔗 <b>የእርስዎ ልዩ መጋበዣ ሊንክ ተዘጋጅቷል!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<code>{invite_link}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>(ሊንኩን 1 ጊዜ በመንካት በቀላሉ ኮፒ (Copy) ማድረግ ይችላሉ)</i>\n\n"
        "📋 <b>እንዴት መጋበዝ ይችላሉ?</b>\n"
        "1. ከላይ የተላከውን የማስታወቂያ ጽሑፍ <b>Forward</b> በማድረግ ለጓደኞችዎ ወይም ለግሩፖች ያጋሩ።\n"
        "2. ወይም ይህንን ሊንክ ብቻ ኮፒ አድርገው ይላኩ።\n\n"
        "✨ <i>በዚህ ሊንክ ቻናሉን የተቀላቀለ እያንዳንዱ ሰው <b>+1 ነጥብ</b> ያስገኝልዎታል!</i>"
    )


# ── Instant Join / Leave Push Notifications ──────────────────────────────────
def format_join_notification(friend_name: str, active_points: int, rank: int) -> str:
    """Instant push notification sent to inviter when someone joins."""
    return (
        f"🎉 <b>እንኳን ደስ አለዎት! አዲስ ሰው ተቀላቅሏል!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>{friend_name}</b> በርስዎ መጋበዣ ሊንክ ቻናላችንን ተቀላቅለዋል!\n\n"
        f"⭐ ያገኙት ነጥብ: <b>+1</b>\n"
        f"📊 አጠቃላይ ነጥብዎ: <b>{active_points}</b>\n"
        f"🏆 አሁን ያሉበት ደረጃ: <b>#{rank}</b>"
    )


def format_leave_notification(friend_name: str, active_points: int) -> str:
    """Notification if a member leaves the channel."""
    return (
        f"⚠️ <b>አንድ ሰው ቻናሉን ለቋል!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>{friend_name}</b> ቻናሉን በመልቀቃቸው <b>-1 ነጥብ</b> ተቀንሷል።\n"
        f"📊 የአሁኑ ነጥብዎ: <b>{active_points}</b>"
    )


# ── Personal Statistics Card ─────────────────────────────────────────────────
def format_stats_card(
    first_name: str, active_points: int, total_joins: int, rank: int
) -> str:
    """Displays personal competition statistics and progress."""
    left_count = total_joins - active_points
    return (
        f"📊 <b>የእኔ ውድድር ውጤት | {first_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ ንቁ ነጥብ (Active Points): <b>{active_points}</b>\n"
        f"👥 አጠቃላይ የተቀላቀሉ: <b>{total_joins}</b>\n"
        f"📉 ቻናሉን የለቀቁ: <b>{left_count}</b>\n"
        f"🏆 የውድድር ደረጃዎ: <b>#{rank}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>ብዙ ሰዎችን በጋበዙ ቁጥር ወደ Top 3 የመግባት እድልዎ ይጨምራል!</i>"
    )


# ── Real-Time Top 10 Leaderboard ─────────────────────────────────────────────
def format_leaderboard(top_users, my_rank: int, my_points: int) -> str:
    """Renders formatted Top 10 leaderboard with medals."""
    lines = [
        f"🏆 <b>{COMPETITION_TITLE}</b>",
        "🌟 <b>የሳምንቱ ከፍተኛ አጋባዦች (Leaderboard)</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    if not top_users:
        lines.append("<i>እስካሁን ምንም ተጋባዥ አልተመዘገበም። የመጀመሪያው ይሁኑ!</i>")
    else:
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for u in top_users:
            medal = medals.get(u.rank, f"<b>{u.rank}.</b>")
            display_name = u.first_name
            if u.username:
                display_name += f" (@{u.username})"
            lines.append(f"{medal} {display_name} ➜ <b>{u.points}</b> ተጋባዥ")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(
        f"👤 የእርስዎ ደረጃ: <b>#{my_rank}</b> | ነጥብ: <b>{my_points}</b>"
    )

    return "\n".join(lines)


# ── Rules & Prizes Card ──────────────────────────────────────────────────────
RULES_TEXT = (
    f"🎁 <b>{COMPETITION_TITLE} — ሽልማቶችና ህጎች</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏆 <b>የሳምንቱ አሸናፊዎች ሽልማት:</b>\n"
    f"🥇 <b>1ኛ የወጣ:</b> {PRIZE_1ST}\n"
    f"🥈 <b>2ኛ የወጣ:</b> {PRIZE_2ND}\n"
    f"🥉 <b>3ኛ የወጣ:</b> {PRIZE_3RD}\n"
    f"🎖️ <b>4ኛ - 10ኛ የወጡ:</b> {PRIZE_4TH_10TH}\n\n"
    "📜 <b>የውድድሩ ህጎች:</b>\n"
    "1. እያንዳንዱ ተጋባዥ የእርስዎን ልዩ ሊንክ ተጠቅሞ ቻናሉን መቀላቀል አለበት።\n"
    "2. አንድ ሰው ሊቆጠር የሚችለው አንድ ጊዜ ብቻ ነው።\n"
    "3. ተጋባዡ ውድድሩ ሳያልቅ ቻናሉን ከለቀቀ ነጥቡ ይቀነሳል።\n"
    "4. የውሸት አካውንቶችን (Bots/Fake Accounts) መጠቀም ከውድድሩ ያሰርዛል።\n"
    "5. አሸናፊዎች በየሳምንቱ እሁድ ምሽት ይፋ ይደረጋሉ።\n\n"
    "🚀 <i>አሁኑኑ መጋበዝ ጀምረው አሸናፊ ይሁኑ!</i>"
)
