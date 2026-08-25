"""
FreshMinds Result Bot — Concise & Modern Message Templates

Ultra-clean, high-readability messages (Amharic + English).
"""

from config import FRESHMINDS_CHANNEL, FRESHMINDS_CHANNEL_LINK


# ── Welcome & Start ──────────────────────────────────────────────────────────

WELCOME = (
    "🎓 <b>FreshMinds Result Checker</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🇪🇹 <b>የመግቢያ ፈተና ውጤትህን/ሽን ለማየት የምዝገባ ቁጥር አስገባ/ቢ:</b>\n"
    "🇬🇧 <i>Enter your Admission Number to start:</i>"
)

PRIVACY_NOTICE = ""


# ── Input Prompts ─────────────────────────────────────────────────────────────

ASK_ADMISSION_NUMBER = (
    "📝 <b>የምዝገባ ቁጥርህን/ሽን አስገባ/ቢ:</b>\n"
    "<i>Enter Admission Number (e.g. 347484):</i>"
)

ADMISSION_RECEIVED = (
    "✅ <code>{admission_no}</code>\n\n"
    "📝 <b>የመጀመሪያ ስምህን/ሽን አስገባ/ቢ:</b>\n"
    "<i>Enter your First Name:</i>"
)


# ── Validation Errors ─────────────────────────────────────────────────────────

INVALID_ADMISSION = (
    "⚠️ <b>ትክክለኛ የምዝገባ ቁጥር አስገባ/ቢ (ቁጥር ብቻ)</b>\n"
    "<i>Please enter numbers only (e.g. 347484).</i>"
)

INVALID_NAME = (
    "⚠️ <b>ትክክለኛ የመጀመሪያ ስም አስገባ/ቢ (ፊደል ብቻ)</b>\n"
    "<i>Please enter letters only (e.g. Abebe / አበበ).</i>"
)


# ── Loading ───────────────────────────────────────────────────────────────────

SEARCHING = (
    "🔍 <b>ውጤት በመፈለግ ላይ...</b>\n"
    "<i>Searching result...</i>"
)


# ── Transition Gate ───────────────────────────────────────────────────────────

def format_transition_gate(admission_no: str, first_name: str) -> str:
    """Ultra-crisp transition message."""
    return (
        f"⏳ <b>{first_name}</b>, <b>ውጤትህን/ሽን እያዘጋጀን ነው...</b>\n"
        "<i>Preparing your result...</i>\n\n"
        f"📢 <b>ውጤትህ/ሽ እስኪወጣ ቻናላችንን ተቀላቀል/ይ:</b>\n"
        f"<i>Join our channel while we fetch:</i>\n"
        f"👉 @{FRESHMINDS_CHANNEL}"
    )


NOT_JOINED_YET = (
    f"⚠️ <b>መጀመሪያ ቻናላችንን ተቀላቀል/ይ!</b>\n"
    f"<i>Please join @{FRESHMINDS_CHANNEL} first.</i>"
)


# ── Result Display ────────────────────────────────────────────────────────────

def format_result_success(student, results) -> str:
    """Format clean scorecard."""
    lines = [
        "🎓 <b>የመግቢያ ፈተና ውጤት | Exam Result</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        f"👤 <b>{student.full_name}</b>",
        f"🔢 <code>{student.admission_no}</code>",
    ]

    meta_parts = []
    if student.stream:
        meta_parts.append(student.stream)
    if student.school:
        meta_parts.append(student.school)
    if meta_parts:
        lines.append(f"🏫 {' | '.join(meta_parts)}")

    lines.append("━━━━━━━━━━━━━━━━━━━━")

    for r in results:
        lines.append(f"📖 {r.subject}: <b>{r.result}</b>")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


# ── Result Status Errors ──────────────────────────────────────────────────────

RESULT_NOT_RELEASED = (
    "⏳ <b>የ2018 ዓ.ም. ውጤት ገና አልተለቀቀም!</b>\n"
    "<i>The 2018 E.C. results are not released yet.</i>\n\n"
    f"📢 <b>ውጤቱ ሲለቀቅ ወዲያውኑ በቻናላችን እናሳውቃለን:</b>\n"
    f"👉 @{FRESHMINDS_CHANNEL}"
)

STUDENT_NOT_FOUND = (
    f"❌ <b>ተማሪ አልተገኘም | Student Not Found</b>\n\n"
    "የምዝገባ ቁጥር እና ስምህን/ሽን አረጋግጠህ/ሽ ደግመህ/ሽ ሞክር/ሪ።\n"
    "<i>Please check admission number & name spelling.</i>"
)

SERVICE_ERROR = (
    "⚠️ <b>አገልግሎቱ ለጊዜው አልመለሰም</b>\n"
    "<i>Service temporarily busy. Please try again in a moment.</i>"
)

RATE_LIMITED = (
    "⏱️ <b>እባክህ/ሽ {seconds} ሴኮንድ ጠብቅ/ቂ</b>\n"
    "<i>Please wait {seconds}s before checking again.</i>"
)


# ── FreshMinds Promotion ──────────────────────────────────────────────────────

FRESHMINDS_PROMO = (
    "\n"
    f"📚 <b>ለ Freshman ጉዞህ/ሽ ተዘጋጅ/ጂ:</b> @{FRESHMINDS_CHANNEL}"
)


# ── Buttons ───────────────────────────────────────────────────────────────────

BTN_CHECK_ANOTHER = "🔄 ሌላ ውጤት / Check Another"
BTN_JOIN_CHANNEL = "📢 ቻናል ተቀላቀል / Join Channel"
BTN_SHOW_RESULT = "🚀 ውጤቴን አሳየኝ / Show Result"
