import os
import json
import logging
import re
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode, ChatAction
from database import db
from config import TARGET_CHANNEL
from handlers.utils import check_and_credit_membership, send_feature_lock_message

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    genai = None
    HAS_GENAI = False

# Configure Gemini API Key if available
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if HAS_GENAI and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.warning(f"Could not configure Gemini API Key: {e}")

logger = logging.getLogger(__name__)
router = Router()



# In-memory session store for active user quizzes
# Format: {user_id: {"course_id": int, "course_name": str, "questions": list, "current_idx": int, "score": int}}
user_quiz_sessions: dict[int, dict] = {}


def clean_json_response(text: str) -> str:
    """Removes markdown code fences and cleans raw JSON string from Gemini."""
    cleaned = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE)
    return cleaned.strip()


def build_quiz_courses_keyboard(courses: list) -> InlineKeyboardMarkup:
    """Builds keyboard grid of quiz-enabled courses."""
    keyboard = []
    row = []
    for c in courses:
        btn = InlineKeyboardButton(
            text=f"{c.icon} {c.name}", callback_data=f"aiq_course_{c.id}"
        )
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class AIQuizStates(StatesGroup):
    waiting_for_custom_topic = State()


def build_topics_keyboard(course_id: int, materials: list = None) -> InlineKeyboardMarkup:
    """Builds chapter & exam topic selection keyboard for a course, dynamically populated with material titles."""
    buttons = []
    
    # Render up to 4 material titles as custom chapter buttons if available
    if materials:
        for idx, m in enumerate(materials[:4]):
            title_clean = m.title[:30]
            buttons.append([InlineKeyboardButton(text=f"📖 {title_clean}", callback_data=f"aiq_topic_{course_id}_mat{m.id}")])

    buttons.extend([
        [InlineKeyboardButton(text="📌 Chapter 1: Key Concepts & Foundations", callback_data=f"aiq_topic_{course_id}_ch1")],
        [InlineKeyboardButton(text="📌 Chapter 2: Core Laws, Theorems & Formulas", callback_data=f"aiq_topic_{course_id}_ch2")],
        [InlineKeyboardButton(text="📌 Chapter 3: Applied Problems & Analysis", callback_data=f"aiq_topic_{course_id}_ch3")],
        [InlineKeyboardButton(text="✍️ በምርጫዎ ርዕስ/ምዕራፍ ይጻፉ (Type Custom Topic)", callback_data=f"aiq_custom_{course_id}")],
        [InlineKeyboardButton(text="🎯 Midterm Exam Simulation (5 Questions)", callback_data=f"aiq_topic_{course_id}_midterm")],
        [InlineKeyboardButton(text="🏆 Final Exam Challenge (5 Questions)", callback_data=f"aiq_topic_{course_id}_final")],
        [InlineKeyboardButton(text="🔙 ወደ ኮርሶች ዝርዝር (Back)", callback_data="aiq_menu")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_question_options_keyboard(user_id: int, q_idx: int, options: list) -> InlineKeyboardMarkup:
    """Builds 4 option buttons for a quiz question."""
    prefixes = ["A", "B", "C", "D"]
    keyboard = []
    row = []

    for idx, opt in enumerate(options[:4]):
        p = prefixes[idx] if idx < len(prefixes) else str(idx + 1)
        btn = InlineKeyboardButton(
            text=f"[ {p} ] {opt[:25]}",
            callback_data=f"aiq_opt_{user_id}_{q_idx}_{idx}",
        )
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def show_quiz_courses_menu(target: Message | CallbackQuery):
    """Renders the course selection menu for interactive AI quizzes."""
    courses = await db.get_courses_with_materials()

    text = (
        "🧪 <b>FreshMinds AI — በ 1ኛ ዓመት ኮርሶች እራስዎን በፈተና ይፈትኑ!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "በመምህራን የተጫኑ <b>የሞጁል ማቴሪያሎችንና ይፋዊ የትምህርት ይዘቶችን</b> መሰረት በማድረግ "
        "በ AI የተዘጋጁ <b>ተفاعላዊ (Interactive) የፈተና ጥያቄዎችን</b> ይስሩ:\n\n"
        "👇 <b>ፈተና ለመስራት የሚፈልጉትን ኮርስ ይምረጡ:</b>"
    )

    keyboard = build_quiz_courses_keyboard(courses)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    else:
        await target.answer(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )


@router.message(Command("quiz"))
@router.message(Command("aiquiz"))
@router.message(F.text == "🧪 Quiz Yourself (በነፃ ፈትን)")
async def handle_quiz_cmd(message: Message, bot: Bot):
    """Entry point for Interactive AI Quiz — gated behind channel membership and admin toggle."""
    if not await db.is_ai_quiz_enabled():
        await message.answer(
            "ℹ️ <b>የ AI ፈተና አገልግሎት በጊዜያዊነት በአድሚን ተዘግቷል!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "አገልግሎቱ ለጥገና ወይም ማሻሻያ በጊዜያዊነት የተዘጋ ሲሆን በቅርቡ የሚከፈት ይሆናል።",
            parse_mode=ParseMode.HTML,
        )
        return
    if not await check_and_credit_membership(bot, message.from_user):
        await send_feature_lock_message(message, "🧪 የተفاعላዊ ፈተና አገልግሎትን", "retry_feature_quiz")
        return
    await show_quiz_courses_menu(message)


@router.callback_query(F.data == "retry_feature_quiz")
@router.callback_query(F.data == "aiq_menu")
async def handle_quiz_menu_callback(callback: CallbackQuery, bot: Bot):
    """Callback entry point for AI Quiz Menu."""
    if not await db.is_ai_quiz_enabled():
        await callback.answer("⚠️ የ AI ፈተና አገልግሎት በጊዜያዊነት በአድሚን ተዘግቷል!", show_alert=True)
        return
    if not await check_and_credit_membership(bot, callback.from_user):
        await callback.answer("⚠️ እባክዎ መጀመሪያ ቻናሉን ይቀላቀሉ!", show_alert=True)
        return
    await callback.answer("✅ ተረጋግጧል!", show_alert=False)
    await show_quiz_courses_menu(callback)


@router.callback_query(F.data.startswith("aiq_course_"))
async def handle_quiz_course_select(callback: CallbackQuery):
    """Prompts student to choose a chapter / topic for the selected course."""
    course_id = int(callback.data.partition("aiq_course_")[2])
    course = await db.get_course_by_id(course_id)

    if not course:
        await callback.answer("⚠️ ኮርሱ አልተገኘም!", show_alert=True)
        return

    materials = await db.get_materials_by_course(course_id)

    await callback.answer()
    text = (
        f"{course.icon} <b>{course.name} — Interactive AI Quiz</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "የሚፈልጉትን ምዕራፍ ወይም የፈተና አይነት ይምረጡ:\n\n"
        "• 📖 <b>የተጫኑ የትምህርት ይዘቶች:</b> በመምህራን በተጫኑ ይዘቶች መፈተን\n"
        "• ✍️ <b>Custom Topic:</b> የሚፈልጉትን ማንኛውንም ርዕስ ጽፈው መፈተን\n"
        "• 🎯 <b>Exam Simulation:</b> የ 5 ጥያቄዎች የ Midterm / Final ሞዴል ፈተና"
    )

    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_topics_keyboard(course_id, materials),
    )


@router.callback_query(F.data.startswith("aiq_custom_"))
async def handle_quiz_custom_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompts student to type custom chapter / topic name."""
    course_id = int(callback.data.partition("aiq_custom_")[2])
    course = await db.get_course_by_id(course_id)
    if not course:
        await callback.answer("⚠️ ኮርሱ አልተገኘም!", show_alert=True)
        return

    await state.update_data(ai_course_id=course_id)
    await state.set_state(AIQuizStates.waiting_for_custom_topic)
    await callback.answer()

    text = (
        f"✍️ <b>{course.name} — የፈለጉትን ርዕስ/ምዕራፍ ይጻፉ:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ፈተና እንዲዘጋጅበት የሚፈልጉትን ርዕስ ከታች በጽሁፍ ይላኩ:\n"
        "<i>(ምሳሌ፡ Chapter 1 Kinematics, or Newton's Laws, or Limits and Continuity)</i>"
    )
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)


@router.message(AIQuizStates.waiting_for_custom_topic)
async def process_custom_topic_text(message: Message, state: FSMContext, bot: Bot):
    """Receives student's custom topic text input and generates quiz."""
    data = await state.get_data()
    course_id = data.get("ai_course_id")
    custom_topic = message.text.strip() if message.text else "General Concepts"
    await state.clear()

    course = await db.get_course_by_id(course_id)
    if not course:
        await message.answer("⚠️ ኮርሱ አልተገኘም። እባክዎ እንደገና ይጀምሩ።")
        return

async def generate_and_start_quiz(
    target_msg: Message | CallbackQuery,
    user_id: int,
    course,
    topic_title: str,
    bot: Bot,
    edit_existing: bool = True
):
    """Core function to query Gemini AI and initialize user quiz session."""
    chat_id = target_msg.message.chat.id if isinstance(target_msg, CallbackQuery) else target_msg.chat.id

    if isinstance(target_msg, CallbackQuery):
        await target_msg.answer("🧠 FreshMinds AI ጥያቄዎችን እያዘጋጀ ነው...")
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Fetch material titles uploaded for this course to ground AI prompt
    materials = await db.get_materials_by_course(course.id)
    mat_titles = [m.title for m in materials] if materials else ["MoE Freshman Standard Syllabus"]

    prompt = (
        f"Generate 5 multiple-choice questions for the Ethiopian university freshman course '{course.name}' "
        f"specifically on the topic '{topic_title}'. "
        f"Base the questions strictly on the official MoE freshman curriculum and course materials: {', '.join(mat_titles[:5])}.\n\n"
        "Return ONLY a valid JSON array of 5 objects without markdown formatting. Each object must have:\n"
        "- 'num': integer (1 to 5)\n"
        "- 'question': string (clear exam question in English)\n"
        "- 'options': list of 4 strings (e.g. ['A. ...', 'B. ...', 'C. ...', 'D. ...'])\n"
        "- 'correct_index': integer (0 for A, 1 for B, 2 for C, 3 for D)\n"
        "- 'explanation': string (detailed step-by-step solution and reasoning in a mix of Amharic and English)\n"
    )

    questions = []
    if HAS_GENAI and GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            json_str = clean_json_response(response.text)
            parsed = json.loads(json_str)
            if isinstance(parsed, list) and len(parsed) > 0:
                questions = parsed
        except Exception as e:
            logger.error(f"Failed to generate AI quiz questions via Gemini API: {e}")

    # Fallback demo questions if Gemini API key is missing or call failed
    if not questions:
        questions = [
            {
                "num": 1,
                "question": f"In {course.name} ({topic_title}), which of the following principles is fundamental?",
                "options": ["A. Fundamental Principle", "B. Secondary Corollary", "C. Arbitrary Assumption", "D. None of the above"],
                "correct_index": 0,
                "explanation": f"በ {course.name} መሰረታዊው መبدአ Fundamental Principle ነው (A)።"
            },
            {
                "num": 2,
                "question": f"Which approach is standard when analyzing core problems in {course.name}?",
                "options": ["A. Unstructured Estimation", "B. SI Unit & Dimensional Analysis", "C. Trial and Error", "D. Disregarding units"],
                "correct_index": 1,
                "explanation": "በሳይንሳዊ ትንተና መሰረታዊ መለኪያዎችን በመጠቀም SI Unit Analysis መተግበር ያስፈልጋል (B)።"
            }
        ]

    user_quiz_sessions[user_id] = {
        "course_id": course.id,
        "course_name": course.name,
        "topic_title": topic_title,
        "questions": questions,
        "current_idx": 0,
        "score": 0,
    }

    msg_to_render = target_msg.message if isinstance(target_msg, CallbackQuery) else target_msg
    await render_quiz_question(msg_to_render, user_id, edit=edit_existing)


@router.callback_query(F.data.startswith("aiq_topic_"))
async def handle_quiz_generate(callback: CallbackQuery, bot: Bot):
    """Generates 5 interactive AI quiz questions using Gemini 1.5 Flash."""
    parts = callback.data.split("_")
    course_id = int(parts[2])
    topic_slug = parts[3]
    user_id = callback.from_user.id

    course = await db.get_course_by_id(course_id)
    if not course:
        await callback.answer("⚠️ ኮርሱ አልተገኘም!", show_alert=True)
        return

    materials = await db.get_materials_by_course(course_id)
    mat_dict = {f"mat{m.id}": m.title for m in materials} if materials else {}

    topic_names = {
        "ch1": "Chapter 1: Key Concepts & Foundations",
        "ch2": "Chapter 2: Core Laws & Formulas",
        "ch3": "Chapter 3: Advanced Problems & Analysis",
        "midterm": "Midterm Exam Simulation",
        "final": "Final Exam Challenge",
    }
    topic_names.update(mat_dict)
    topic_title = topic_names.get(topic_slug, "General Assessment")

    await generate_and_start_quiz(
        target_msg=callback,
        user_id=user_id,
        course=course,
        topic_title=topic_title,
        bot=bot,
        edit_existing=True
    )


async def render_quiz_question(message: Message, user_id: int, edit: bool = True):
    """Renders the current question card for the user's active quiz session."""
    session = user_quiz_sessions.get(user_id)
    if not session:
        await message.answer("⚠️ የፈተና ጊዜው አልፏል። እባክዎ በድጋሚ ይጀምሩ።")
        return

    q_idx = session["current_idx"]
    questions = session["questions"]

    if q_idx >= len(questions):
        await render_quiz_final_results(message, user_id, edit=edit)
        return

    q = questions[q_idx]
    total_q = len(questions)

    text = (
        f"🧪 <b>{session['course_name']} Quiz</b>\n"
        f"📌 <i>{session['topic_title']}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"❓ <b>ጥያቄ {q_idx + 1} / {total_q}:</b>\n\n"
        f"<b>{q['question']}</b>\n\n"
        "👇 <b>ትክክለኛውን መልስ ይምረጡ:</b>\n"
    )
    for idx, opt in enumerate(q["options"]):
        text += f"• {opt}\n"

    keyboard = build_question_options_keyboard(user_id, q_idx, q["options"])

    if edit:
        await message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)


@router.callback_query(F.data.startswith("aiq_opt_"))
async def handle_quiz_option_tap(callback: CallbackQuery):
    """Evaluates student's answer choice and reveals full explanation."""
    parts = callback.data.split("_")
    user_id = int(parts[2])
    q_idx = int(parts[3])
    opt_idx = int(parts[4])

    session = user_quiz_sessions.get(user_id)
    if not session or session["current_idx"] != q_idx:
        await callback.answer("⚠️ ይህ ጥያቄ አልፏል!", show_alert=True)
        return

    q = session["questions"][q_idx]
    correct_idx = q["correct_index"]
    is_correct = (opt_idx == correct_idx)

    if is_correct:
        session["score"] += 1
        result_badge = "✅ <b>ትክክል ነው! (CORRECT!)</b> 🎉"
    else:
        result_badge = f"❌ <b>አልተሳካም! (INCORRECT!)</b>\n💡 ትክክለኛው መልስ: <b>{q['options'][correct_idx]}</b>"

    await callback.answer("✅ መልስዎ ተመዝግቧል!")

    explanation_text = (
        f"🧪 <b>{session['course_name']} — ጥያቄ {q_idx + 1} ማብራሪያ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{result_badge}\n\n"
        f"📝 <b>የጥያቄው ሙሉ ማብራሪያ (Solution & Explanation):</b>\n"
        f"<i>{q['explanation']}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 የአሁኑ ውጤትዎ: <b>{session['score']} / {q_idx + 1}</b>"
    )

    next_btn_text = "▶️ ቀጣይ ጥያቄ (Next Question)" if (q_idx + 1) < len(session["questions"]) else "🏆 ውጤትን ተመልከት (View Results)"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=next_btn_text, callback_data=f"aiq_next_{user_id}_{q_idx + 1}")]
        ]
    )

    await callback.message.edit_text(
        explanation_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("aiq_next_"))
async def handle_quiz_next_question(callback: CallbackQuery):
    """Moves to the next question in the quiz session."""
    parts = callback.data.split("_")
    user_id = int(parts[2])
    next_idx = int(parts[3])

    session = user_quiz_sessions.get(user_id)
    if not session:
        await callback.answer("⚠️ የፈተና ጊዜው አልፏል።")
        return

    session["current_idx"] = next_idx
    await callback.answer()
    await render_quiz_question(callback.message, user_id, edit=True)


async def render_quiz_final_results(message: Message, user_id: int, edit: bool = True):
    """Renders the final score report card at the end of the quiz."""
    session = user_quiz_sessions.get(user_id)
    if not session:
        return

    score = session["score"]
    total = len(session["questions"])
    pct = int((score / total) * 100) if total > 0 else 0

    if pct >= 80:
        badge = "🏆 <b>እጅግ ድንቅ ብቃት! (Mastery Level 🌟)</b>\nለ 1st Semester ፈተናዎች በሚገባ ተዘጋጅተዋል!"
    elif pct >= 60:
        badge = "👍 <b>ጥሩ ጥረት! (Good Standing 🏅)</b>\nጥቂት ምዕራፎችን በመከለስ ውጤትዎን ማሻሻል ይችላሉ!"
    else:
        badge = "📚 <b>ተጨማሪ ክለሳ ያስፈልጋል (Needs Review ⚠️)</b>\nየ FreshMinds ማጠቃለያ ኖቶችን በድጋሚ ያንብቡ!"

    text = (
        f"🎉 <b>የፈተናው ማጠቃለያ ውጤት | {session['course_name']}</b>\n"
        f"📌 <i>{session['topic_title']}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 ያገኙት ነጥብ: <b>{score} / {total}</b> (<b>{pct}%</b>)\n"
        f"🎖️ የብቃት ደረጃ: {badge}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>ጓደኞችዎን በመጋበዝ የውድድር ነጥቦችን ያግኙ!</i>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 እንደገና ፈትን (Retry Quiz)", callback_data=f"aiq_course_{session['course_id']}")],
            [InlineKeyboardButton(text="📚 የኮርሱ ማቴሪያሎች (View Materials)", callback_data=f"course_view_{session['course_id']}")],
            [InlineKeyboardButton(text=f"📢 @{TARGET_CHANNEL} ቻናል ተቀላቀል", url=f"https://t.me/{TARGET_CHANNEL}")],
        ]
    )

    if edit:
        await message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
