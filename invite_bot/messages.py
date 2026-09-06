"""
FreshMinds Invite Competition Bot — Message Templates (Amharic & English)
"""

import html
from config import (
    TARGET_CHANNEL,
    COMPETITION_TITLE,
    PRIZE_1ST,
    PRIZE_2ND,
    PRIZE_3RD,
    PRIZE_4TH,
)

# ── Main Menu Keyboard Labels ────────────────────────────────────────────────
BTN_RESOURCES = "📚 ኮርሶችና ማቴሪያሎች (Resources)"
BTN_UNIVERSITIES = "🏛️ የዩኒቨርሲቲዎች መረጃ (Universities)"
BTN_GPA_CALC = "🧮 GPA ማስያ (Calculator)"
BTN_GET_LINK = "🔗 የእኔ መጋበዣ ሊንክ (My Link)"
BTN_MY_STATS = "📊 የእኔ ውጤት (My Stats)"
BTN_LEADERBOARD = "🏆 የሳምንቱ ደረጃ (Leaderboard)"
BTN_RULES = "🎁 ሽልማቶችና ህጎች (Prizes & Rules)"

# ── Welcome / Start Message ──────────────────────────────────────────────────
WELCOME_TEXT = (
    f"🎉 <b>እንኳን ወደ FreshMinds Academy በደህና መጡ!</b> 🇪🇹\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "ለ 2019 ዓ.ም የ Freshman ዩኒቨርሲቲ ተማሪዎች የተዘጋጀ ሁለገብ የትምህርትና መረጃ ቦት:\n\n"
    "📚 <b>የኮርስ ማቴሪያሎች:</b> የ 1ኛ አመት ሞጁሎች፣ የማጠቃለያ ኖቶችና ያለፉ ፈተናዎች\n"
    "🏛️ <b>የዩኒቨርሲቲዎች መረጃ:</b> የኢትዮጵያ ዩኒቨርሲቲዎች አጠቃላይ መረጃና የካምፓስ ህይወት\n"
    "🧮 <b>GPA ማስያ:</b> የ 1st Semester ውጤት በቀላሉ የሚያሰሉበት ልዩ ካልኩሌተር\n"
    f"🎁 <b>ሳምንታዊ ውድድር:</b> ጓደኞችን በመጋበዝ የገንዘብና የሞባይል ካርድ ሽልማቶችን ያሸንፉ!\n\n"
    "👇 <b>ከታች ካሉት አማራጮች የሚፈልጉትን ይምረጡ:</b>"
)

# ── Ethiopian MoE Grade Point Mapping ─────────────────────────────────────────
GRADE_POINTS = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.75,
    "B+": 3.5,
    "B": 3.0,
    "B-": 2.75,
    "C+": 2.5,
    "C": 2.0,
    "C-": 1.75,
    "D": 1.0,
    "F": 0.0,
}


def calculate_gpa(courses: dict) -> tuple[float, int, float, list[dict]]:
    """
    Calculates GPA ignoring unfilled slots.
    courses is a dict: {1: {'ch': 4, 'grade': 'A'}, 2: {'ch': 3, 'grade': 'A-'}, ...}
    Returns (gpa, total_ch, total_pts, filled_courses_breakdown)
    """
    total_ch = 0
    total_pts = 0.0
    breakdown = []

    for idx in sorted(courses.keys()):
        item = courses[idx]
        ch = item.get("ch")
        grade = item.get("grade")
        if ch and grade and grade in GRADE_POINTS:
            ch_val = int(ch)
            pts_val = GRADE_POINTS[grade] * ch_val
            total_ch += ch_val
            total_pts += pts_val
            breakdown.append({
                "idx": idx,
                "ch": ch_val,
                "grade": grade,
                "pts": pts_val,
            })

    gpa = (total_pts / total_ch) if total_ch > 0 else 0.0
    return round(gpa, 2), total_ch, round(total_pts, 2), breakdown


def format_gpa_result_card(gpa: float, total_ch: int, total_pts: float, breakdown: list[dict]) -> str:
    """Formats student semester GPA calculation result."""
    if gpa >= 3.80:
        standing = "Very Great Distinction (እጅግ በጣም ከፍተኛ ማዕረግ 🌟)"
        advice = "💡 <b>እጅግ ድንቅ ውጤት!</b> በዚህ GPA ወደ Medicine, Software Engineering እና Electrical በቀላሉ መግባት ይችላሉ!"
    elif gpa >= 3.60:
        standing = "Great Distinction (በጣም ከፍተኛ ማዕረግ 🏅)"
        advice = "💡 <b>በጣም ከፍተኛ ውጤት!</b> ወደ ተወዳጅ የኢንጂነሪንግና የጤና ዲፓርትመንቶች የሚያስገባ ውጤት ነው!"
    elif gpa >= 3.25:
        standing = "Distinction (ከፍተኛ ማዕረግ 🎖️)"
        advice = "💡 <b>ጥሩ ውጤት!</b> ጥረታችሁን አጠናክራችሁ በመቀጠል የፈለጋችሁትን ዲፓርትመንት መምረጥ ትችላላችሁ!"
    elif gpa >= 2.00:
        standing = "Satisfactory (ያለፉ / Promoted ✅)"
        advice = "💡 <b>ያለፉ ውጤት!</b> በቀጣይ ፈተናዎች ውጤታችሁን የበለጠ ለማሻሻል በርትታችሁ አንብቡ!"
    elif gpa >= 1.75:
        standing = "Academic Warning (ማስጠንቀቂያ ⚠️)"
        advice = "⚠️ <b>ማስጠንቀቂያ!</b> ውጤታችሁ ከ 2.00 በታች እንዳይወርድ ለቀጣይ ሴሚስተር ጠንክራችሁ መስራት አለባችሁ!"
    else:
        standing = "Academic Dismissal Risk (የመሰናበት አደጋ ❌)"
        advice = "❌ <b>አስቸኳይ ጥረት ያስፈልጋል!</b> ውጤታችሁን ለማሻሻል የ FreshMinds ማጠቃለያዎችን አሁኑኑ አንብቡ!"

    lines = [
        "📊 <b>የእርስዎ የ 1st Semester ውጤት ስሌት (GPA Card)</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]
    for b in breakdown:
        lines.append(
            f"• Course-{b['idx']} (<b>{b['ch']} CH</b>) : <b>{b['grade']}</b> ➜ <b>{b['pts']:.2f}</b> Pts"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📌 ጠቅላላ Credit Hours (Total CH): <b>{total_ch}</b>")
    lines.append(f"⭐ ጠቅላላ Grade Points: <b>{total_pts:.2f}</b>")
    lines.append(f"🏆 <b>Semester GPA: <code>{gpa:.2f} / 4.00</code></b>")
    lines.append(f"🎖️ ደረጃ: <b>{standing}</b>\n")
    lines.append(advice)

    return "\n".join(lines)


# ── Ready-to-Forward Promotional Marketing Post ──────────────────────────────
def format_promotional_post(invite_link: str) -> str:
    """
    Complete, attractive promotional post that students can directly
    forward to Telegram groups, batch channels, or friends.
    """
    return (
        "🎓 <b>ለ 2019 ዓ.ም የዩኒቨርሲቲ Freshman ተማሪዎች በሙሉ!</b> 🇪🇹\n\n"
        "ለ 1ኛ አመት (Freshman) የዩኒቨርሲቲ ህይወትህ/ሽ በሚገባ ተዘጋጅተሃል/ሻል? "
        "<b>FreshMinds Academy</b> ለተማሪዎች የተዘጋጀ ልዩ የትምህርት ማዕከል ነው!\n\n"
        "📌 <b>በቻናላችን ምን ያገኛሉ?</b>\n"
        "📚 <b>ነፃ የ Freshman የቪዲዮ ኮርሶች</b> (Applied Maths, General Physics, Chemistry, Economics...)\n"
        "📝 <b>የዩኒቨርሲቲ ፈተና ሞዴሎች</b> እና የማጠቃለያ ኖቶች (Summary Handouts)\n"
        "🏛️ <b>የዩኒቨርሲቲ ምደባ</b> እና የዲፓርትመንት መረጣ መረጃዎች\n"
        "📱 <b>FreshMinds Mobile App</b> (በቅርቡ የሚለቀቅ)\n\n"
        "👇 <b>አሁኑኑ ቻናሉን ይቀላቀሉ:</b>\n"
        f"{invite_link}"
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
    safe_name = html.escape(friend_name)
    return (
        f"🎉 <b>እንኳን ደስ አለዎት! አዲስ ሰው ተቀላቅሏል!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>{safe_name}</b> በርስዎ መጋበዣ ሊንክ ቻናላችንን ተቀላቅለዋል!\n\n"
        f"⭐ ያገኙት ነጥብ: <b>+1</b>\n"
        f"📊 አጠቃላይ ነጥብዎ: <b>{active_points}</b>\n"
        f"🏆 አሁን ያሉበት ደረጃ: <b>#{rank}</b>"
    )


def format_leave_notification(friend_name: str, active_points: int) -> str:
    """Notification if a member leaves the channel."""
    safe_name = html.escape(friend_name)
    return (
        f"⚠️ <b>አንድ ሰው ቻናሉን ለቋል!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>{safe_name}</b> ቻናሉን በመልቀቃቸው <b>-1 ነጥብ</b> ተቀንሷል።\n"
        f"📊 የአሁኑ ነጥብዎ: <b>{active_points}</b>"
    )


# ── Personal Statistics Card ─────────────────────────────────────────────────
def format_stats_card(
    first_name: str, active_points: int, total_joins: int, rank: int
) -> str:
    """Displays personal competition statistics and progress."""
    safe_name = html.escape(first_name)
    left_count = total_joins - active_points
    return (
        f"📊 <b>የእኔ ውድድር ውጤት | {safe_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ ንቁ ነጥብ (Active Points): <b>{active_points}</b>\n"
        f"👥 አጠቃላይ የተቀላቀሉ: <b>{total_joins}</b>\n"
        f"📉 ቻናሉን የለቀቁ: <b>{left_count}</b>\n"
        f"🏆 የውድድር ደረጃዎ: <b>#{rank}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>ብዙ ሰዎችን በጋበዙ ቁጥር ወደ Top 3 የመግባት እድልዎ ይጨምራል!</i>"
    )


# ── Real-Time Top 10 Leaderboard ─────────────────────────────────────────────
def format_leaderboard(
    top_users, my_rank: int, my_points: int, is_admin: bool = False
) -> str:
    """Renders formatted Top 10 leaderboard (clean display name for users, clickable username for admin)."""
    header_title = (
        "👑 <b>የሳምንቱ ከፍተኛ አጋባዦች (Admin View)</b>"
        if is_admin
        else "🌟 <b>የሳምንቱ ከፍተኛ አጋባዦች (Leaderboard)</b>"
    )
    lines = [
        f"🏆 <b>{COMPETITION_TITLE}</b>",
        header_title,
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    if not top_users:
        lines.append("<i>እስካሁን ምንም ተጋባዥ አልተመዘገበም። የመጀመሪያው ይሁኑ!</i>")
    else:
        medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🎖️"}
        for u in top_users:
            medal = medals.get(u.rank, f"<b>{u.rank}.</b>")
            display_name = html.escape(u.first_name)

            if is_admin:
                # Clickable username & profile for Admin
                if u.username:
                    user_tag = f'<b>{display_name}</b> (<a href="https://t.me/{u.username}">@{u.username}</a>)'
                else:
                    user_tag = f'<b><a href="tg://user?id={u.user_id}">{display_name}</a></b> [ID: <code>{u.user_id}</code>]'
            else:
                # Clean, unclickable text for regular users (privacy/security safe)
                user_tag = f"<b>{display_name}</b>"

            lines.append(f"{medal} {user_tag} ➜ <b>{u.points}</b> ተጋባዥ")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(
        f"👤 የእርስዎ ደረጃ: <b>#{my_rank}</b> | ነጥብ: <b>{my_points}</b>"
    )

    return "\n".join(lines)


# ── Rules & Prizes Card ──────────────────────────────────────────────────────
RULES_TEXT = (
    f"🎁 <b>{COMPETITION_TITLE} — ሽልማቶችና ህጎች</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏆 <b>የሳምንቱ ከፍተኛ 4 አሸናፊዎች ሽልማት:</b>\n"
    f"🥇 <b>1ኛ የወጣ:</b> {PRIZE_1ST}\n"
    f"🥈 <b>2ኛ የወጣ:</b> {PRIZE_2ND}\n"
    f"🥉 <b>3ኛ የወጣ:</b> {PRIZE_3RD}\n"
    f"🎖️ <b>4ኛ የወጣ:</b> {PRIZE_4TH}\n\n"
    "📜 <b>የውድድሩ ህጎች:</b>\n"
    "1. እያንዳንዱ ተጋባዥ የእርስዎን ልዩ ሊንክ ተጠቅሞ ቻናሉን መቀላቀል አለበት።\n"
    "2. አንድ ሰው ሊቆጠር የሚችለው አንድ ጊዜ ብቻ ነው።\n"
    "3. ተጋባዡ ውድድሩ ሳያልቅ ቻናሉን ከለቀቀ ነጥቡ ይቀነሳል።\n"
    "4. የውሸት አካውንቶችን (Bots/Fake Accounts) መጠቀም ከውድድሩ ያሰርዛል።\n"
    "5. አሸናፊዎች በየሳምንቱ እሁድ ምሽት ይፋ ይደረጋሉ።\n\n"
    "🚀 <i>አሁኑኑ መጋበዝ ጀምረው አሸናፊ ይሁኑ!</i>"
)
