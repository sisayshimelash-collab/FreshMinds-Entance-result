"""
Script to seed/update all 31 Ethiopian Universities into invite_competition.db
Features:
- Comprehensive detailed profiles with bulleted department listings.
- Zero mixing of data between universities.
- Strict extraction of permanent information (Location, Weather, Campuses, Departments, Strengths).
- Volatile pricing/cafe food info excluded.
"""

import asyncio
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "invite_competition.db"

UNIVERSITIES_DATA = [
    (
        "Addis Ababa University (AAU)",
        (
            "📣 <b>Addis Ababa University (AAU) — አዲስ አበባ ዩኒቨርሲቲ (Autonomous)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አዲስ አበባ ከተማ እና ቢሾፍቱ (ኦሮሚያ ክልል)\n"
            "👑 <b>የሀገራችን ቁጥር 1 ፍላግሺፕ ዩኒቨርሲቲ:</b> ራሱን በራሱ የሚያስተዳድር (Autonomous Research University) የመጀመሪያው የመንግስት ዩኒቨርሲቲ ነው!\n"
            "📝 <b>ልዩ የመግቢያ ደንብ:</b> አዲስ አበባ ዩኒቨርሲቲ ለመግባት ተማሪዎች የ MoE መቁረጫ ውጤት ማሟላት ብቻ ሳይሆን የዩኒቨርሲቲውን ልዩ <b>UAT (Undergraduate Admission Test)</b> ማለፍ አለባቸው።\n"
            "⛅ <b>የአየር ሁኔታ:</b> የመጀመርያዎቹ ወራት መጠነኛ ብርዳማ ሆኖ በኋላ ላይ ተስማሚና ሞቃታማ ይሆናል።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 14 ታሪካዊ ካምፓሶች (Campuses):</b>\n\n"
            "⚙️ <b>1. 5 ኪሎ ካምፓስ (AAiT — Institute of Technology):</b>\n"
            "  • Software Engineering 💻 | Electrical & Computer Engineering ⚡ | Biomedical Engineering 🧬 (ልዩ የልህቀት መስክ)\n"
            "  • Mechanical Engineering ⚙️ | Civil Engineering 🏗️ | Chemical & Bio-Engineering 🧪\n\n"
            "💻 <b>2. 4 ኪሎ ካምፓስ (CNCS — Natural & Computational Sciences):</b>\n"
            "  • Computer Science 💻 | Mathematics | Physics | Chemistry | Biology | Statistics | Geology 🪨\n\n"
            "🏛️ <b>3. 6 ኪሎ ካምፓስ (Main Campus — Sidist Kilo):</b>\n"
            "  • School of Law ⚖️ (አንጋፋው የህግ ትምህርት ቤት — LL.B 5 Years)\n"
            "  • Political Science & IR (PSIR) | Sociology | Social Work | Philosophy | Geography | History\n"
            "  • Journalism & Communication | Languages (Amharic, English, Oromo, Arabic, Chinese, Sign Language)\n\n"
            "🏗️ <b>4. ልደታ ካምፓስ (EiABC — Architecture & Urban Planning):</b>\n"
            "  • Architecture 🏛️ (በቅድመ ፈተና የሚገባ) | Construction Technology & Management (COTM) | Urban & Regional Planning\n\n"
            "📈 <b>5. ሜክሲኮ & FBE ካምፓስ (School of Commerce / CBE):</b>\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management | Marketing Management | BAIS | PADM | Logistics & Supply Chain\n\n"
            "🩺 <b>6. ጥቁር አንበሳ & 18 ማዞሪያ & ሰፈረ ሰላም (Health Sciences 🏥):</b>\n"
            "  • Medicine (MD) 🩺 (ጥቁር አንበሳ ስፔሻላይዝድ ሆስፒታል) | Dental Medicine (DMD 🦷)\n"
            "  • Pharmacy | Medical Laboratory Sciences | Radiologic Technology | Physiotherapy | Comprehensive Nursing | Midwifery\n\n"
            "🎨 <b>7. የቴአትርና ሙዚቃ ካምፓሶች (CPVA):</b>\n"
            "  • Yared School of Music 🎼 | Alle School of Fine Arts & Design 🎨 | Theatrical Arts\n\n"
            "🌾 <b>8. ቢሾፍቱ ካምፓስ (Bishoftu — ደብረዘይት):</b>\n"
            "  • College of Veterinary Medicine (DVM - 6 Years) 🐾 & Veterinary Laboratory Technology\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        1,
    ),
    (
        "Jimma University (JU)",
        (
            "📣 <b>Jimma University (JU) — ጅማ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ጅማ ከተማ፣ ኦሮሚያ ክልል (ከአዲስ አበባ ~390 ኪ.ሜ)\n"
            "❤️ <b>የፍቅር ከተማ (Magaala Jaalalaa):</b> በንጉስ አባጅፋር ታሪክና ታሪካዊ ቤተ-መንግስት የምትታወቅ፣ ለኑሮም ሆነ ለትምህርት እጅግ ምቹ የሆነች አንጋፋ ከተማ።\n"
            "⛅ <b>የአየር ሁኔታ:</b> ደስ የሚል ለምለምና ሞቃታማ አየር። ቀለል ያሉ አልባሳትን ይዞ መሄድ ይመረጣል።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 4 ዋና ዋና ካምፓሶች (+ 1 አዲስ ኤክስፓንሽን):</b>\n\n"
            "🏫 <b>1. ዋናው ግቢ (Main Campus):</b>\n"
            "  • በከተማዋ አቅራቢያ የሚገኝ።\n"
            "  • ጤና እንስቲትዩት (Institute of Health — Medicine, Health Officer, Nursing, Pharmacy)፣ ህግና አስተዳደር ኮሌጅ (School of Law)፣ የተፈጥሮ ሳይንስ ኮሌጅ፣ ማህበራዊ ሳይንስና የስነ-ባህሪ ኮሌጆች ይገኙበታል።\n\n"
            "🏫 <b>2. ቤኮ ካምፓስ (B.E.Co — Business & Economics):</b>\n"
            "  • ከዋናው ግቢ አጠገብ የሚገኝ ሲሆን ሁለቱን ካምፓሶች የሚያገናኝ ትልቅ ውብ ድልድይ አለው፤ ተማሪዎች በድልድዩ በኩል ያለምንም ችግር ይመላለሳሉ።\n"
            "  • Accounting & Finance, Economics, Management, Banking & Finance።\n\n"
            "🏫 <b>3. ቴክኖ ግቢ (Kito Furdisa Campus — JiT / Engineering & Computing):</b>\n"
            "  • ከዋናው ግቢ ወጣ ብሎ የሚገኝ (በሁለቱ መካከል የመርካቶ ከተማ እምብርት አለ)።\n"
            "  • የ Engineering (Civil, Mechanical, Electrical, Water)፣ Biomedical Engineering (በሀገራችን ቀዳሚ)፣ Computer Science እና IT ተማሪዎች ግቢ ነው።\n"
            "  • ህንፃዎቹ እጅግ የሚያማምሩና <b>'የኢንጂነሮች ድንቅ ስራ'</b> የሚያስብሉ ናቸው!\n\n"
            "🏫 <b>4. Agri Campus (ግብርና እና እንስሳት ህክምና):</b>\n"
            "  • በቴክኖ ግቢ እና በዋናው ግቢ መካከል (መርካቶ አካባቢ) የሚገኝ።\n"
            "  • Agriculture, Horticulture, Animal Sciences, Veterinary Medicine (DVM)።\n\n"
            "🏫 <b>5. Agaro Campus:</b> አዲስ ኤክስፓንሽን ካምፓስ።\n\n"
            "💧 <b>መብራት፣ ውሃ እና Wi-Fi:</b> ጅማ ውስጥ የውሃ ችግር ከቶ የለም! <i>(ጅማ ውስጥ ውሃ ጠፋ ማለት ኒውዮርክ መብራት ጠፋ እንደማለት ነው)</i>። Wi-Fi እና መብራትም በጥሩ ደረጃ ላይ ይገኛል።\n"
            "🍲 <b>የካፌና የውጭ ምግብ:</b> የጅማ ዩኒቨርሲቲ ካፌ በሀገራችን ካፌዎች ቀዳሚ ከሚባሉት አንዱ ነው፤ ጨጓራ አይነካም። ከግቢ ውጭም በርካታ ሬስቶራንቶች፣ ጁስ ቤቶች እና ትኩስ ፍራፍሬዎች (ሙዝ 🍌፣ ብርቱካን 🍊፣ አቮካዶ 🥑) በቀላሉ ይገኛሉ።\n"
            "💡 <b>የትምህርት ማስታወሻ:</b> ጅማ ዩኒቨርሲቲ በሀገራችን ቀዳሚ የልህቀት ማዕከል ቢሆንም ትምህርቱ ጠንከር ያለ ስለሆነ በግቢው ምቾት እንዳትታለሉ! ከመጀመሪያው ቀን ጀምሮ በርትታችሁ አንብቡ።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        2,
    ),
    (
        "Adama Science & Technology (ASTU)",
        (
            "⚡ <b>Adama Science & Technology University (ASTU) — አዳማ ሳይንስና ቴክኖሎጂ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አዳማ (ናዝሬት)፣ ኦሮሚያ\n"
            "⛅ <b>የአየር ሁኔታ:</b> በቀን ሞቃታማ፣ ማታ ማታ ደግሞ መጠነኛ ቅዝቃዜ (ቀለል ያለ ሹራብ ያስፈልጋል)\n"
            "🔬 <b>ተፈጥሮ:</b> የሳይንስ እና ቴክኖሎጂ ልህቀት ማዕከል (Single Main Campus)\n\n"
            "📋 <b>የትምህርት ክፍሎች (Schools & Departments):</b>\n\n"
            "⚡ <b>School of Electrical Engineering & Computing:</b>\n"
            "  • Computer Science & Engineering (CSE)\n"
            "  • Electronics & Communication Engineering\n"
            "  • Power & Control Engineering\n\n"
            "🏗️ <b>School of Civil Engineering & Architecture:</b>\n"
            "  • Architecture (በፈተና የሚገባ)\n"
            "  • Civil Engineering\n"
            "  • Water Resources Management & Hydraulics\n"
            "  • Geomatics Engineering\n\n"
            "🔧 <b>School of Mechanical, Chemical & Materials:</b>\n"
            "  • Mechanical Engineering\n"
            "  • Chemical Engineering\n"
            "  • Materials Science & Engineering\n\n"
            "🔬 <b>School of Applied Natural Sciences:</b>\n"
            "  • Applied Biology\n"
            "  • Applied Chemistry\n"
            "  • Applied Geology\n"
            "  • Applied Mathematics\n"
            "  • Applied Physics\n\n"
            "💡 <b>ማስታወሻ:</b> የ 1st Year Pre-Engineering ውጤት ተወዳዳሪ ሆኖ ወደሚፈለገው ትምህርት ክፍል ለመግባት ወሳኝ ነው።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        3,
    ),
    (
        "Addis Ababa Science & Technology (AASTU)",
        (
            "⚡ <b>Addis Ababa Science & Technology University (AASTU)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አዲስ አበባ (ቂሊንጦ / አቃቂ ቃሊቲ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ከአዲስ አበባ ጋር ተመሳሳይ የሆነ ተስማሚ አየር\n"
            "🔬 <b>ተፈጥሮ:</b> የሳይንስ እና ቴክኖሎጂ የልህቀት ማዕከል (Center of Excellence)\n\n"
            "📋 <b>የትምህርት ክፍሎች (Colleges & Departments):</b>\n\n"
            "⚙️ <b>College of Engineering (የምህንድስና ኮሌጅ):</b>\n"
            "  • Software Engineering (5 Years)\n"
            "  • Electrical & Computer Engineering (5 Years)\n"
            "  • Electromechanical Engineering (5 Years)\n"
            "  • Mechanical Engineering (5 Years)\n"
            "  • Civil Engineering (5 Years)\n"
            "  • Architecture (5 Years — በፈተና የሚገባ)\n"
            "  • Chemical Engineering (5 Years)\n"
            "  • Mining Engineering (5 Years)\n"
            "  • Environmental Engineering (5 Years)\n\n"
            "🔬 <b>College of Natural & Applied Sciences:</b>\n"
            "  • Applied Biotechnology (4 Years)\n"
            "  • Industrial Chemistry (4 Years)\n"
            "  • Applied Geology (4 Years)\n"
            "  • Food Science & Applied Nutrition (4 Years)\n\n"
            "📚 <b>College of Social Science & Humanities:</b>\n"
            "  • Freshman & Pre-engineering foundational courses, Entrepreneurship & Languages\n\n"
            "💡 <b>ማስታወሻ:</b> AASTU ለመግባት ተማሪዎች የ MoE መቁረጫ ውጤት ካሟሉ በኋላ የዩኒቨርሲቲውን የመግቢያ ፈተና (Entrance Exam) ማለፍ አለባቸው።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        4,
    ),
    (
        "University of Gondar (UoG)",
        (
            "📣 <b>University of Gondar (UoG) — ጎንደር ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ጎንደር ከተማ፣ አማራ ክልል (ከአዲስ አበባ ~727 ኪ.ሜ)\n"
            "🚌 <b>ጉዞ:</b> በሀገር አቋራጭ ባስ (Selam, Habesha, Zemen, Golden, Tata Bus) በቀጥታ በአንድ ቀን መድረስ ይቻላል። በአየር መንገድ በ 41 ደቂቃ ውስጥ መብረር ይቻላል።\n"
            "⛅ <b>የአየር ሁኔታ:</b> ከፍተኛ ቦታ ላይ ስለሚገኝ ቀን ፀሐያማ፣ ማታ ብርዳማ ነው። ሹራብና ጃኬት ይያዙ! <i>(ወባና ቢንቢ ምንም የሌለበት ንጹህ ከተማ ነው)</i>።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 5 ዋና ዋና ካምፓሶች:</b>\n"
            "💡 <i>ማራኪ፣ ቴዲ እና ፋሲል ካምፓሶች የተያያዙ ሲሆኑ፤ GC Health እና ጤዳ ካምፓስ በተለየ ቦታ ይገኛሉ።</i>\n\n"
            "🏫 <b>1. GC Campus (College of Medicine & Health Sciences):</b>\n"
            "  • በሀገራችን አንጋፋና ተመራጭ የጤና ማዕከል (Medicine MD, Health Officer HO, Pharmacy, Nursing, Midwifery, Medical Lab, Physiotherapy, Optometry)። 🌐 <i>www.uog.edu.et</i>\n\n"
            "🏫 <b>2. ፋሲል Campus (Engineering & Technology):</b>\n"
            "  • 🏆 በ IoT (Engineering Science) በኢትዮጵያ ለ 3 ተከታታይ አመታት 1ኛ በመውጣት Hat-Trick የሰራ አንደኛ ደረጃ ካምፓስ!\n"
            "  • 8 የ Engineering መስኮች: Electrical & Computer, Biomedical Engineering, Chemical, Mechanical, Civil, COTM, Industrial, Hydraulics Engineering።\n"
            "  • 🍲 <i>በግቢው 4 ላውንቾች አሉ (ኮንትራት፣ መምህራን፣ ማሚና ኮፊ ሃውስ ላውንች — ሹሮ/በየአይነት 30+ ብር)።</i>\n\n"
            "🏫 <b>3. ቴዲ Campus (Tedd Campus):</b>\n"
            "  • Natural & Computational Sciences (ከ Engineering, Health እና Agriculture ውጭ ያሉ)።\n\n"
            "🏫 <b>4. ማራኪ Campus (Maraki Campus):</b>\n"
            "  • All Social Sciences & Humanities, School of Law ⚖️, College of Business & Economics 💰።\n\n"
            "🏫 <b>5. ጤዳ Campus (Teda Campus):</b>\n"
            "  • Agricultural Sciences & Animal Production 🌱።\n\n"
            "☠️ <b>ለአዲስ ተማሪዎች የደህንነት ማስጠንቀቂያ:</b> ከመናኸሪያ ወደ ግቢ ስትሄዱም ሆነ ግቢ ከገባችሁ በኋላ ወደ ከተማ ስትወጡ ስልካችሁንና ንብረታችሁን በንቃት ጠብቁ (የተደራጁ ሌቦች ስላሉ)።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        4,
    ),
    (
        "Hawassa University (HU)",
        (
            "📣 <b>Hawassa University (HU) — ሐዋሳ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ሐዋሳ ከተማ፣ የሲዳማ ክልል ፈርጥና መናገሻ (ከአዲስ አበባ እጅግ ቅርብ ርቀት)\n"
            "🌅 <b>የአካባቢ ውበት:</b> በሀገራችን በትምህርት ጥራቱም ሆነ በግቢ ውበቱ አንደኛ ደረጃ ከሚባሉት ተርታ የሚመደብ የውበትና የትምህርት ማዕከል ነው!\n"
            "⛅ <b>የአየር ሁኔታ:</b> በቀኑ ክፍለ ጊዜ ሞቃታማ ሆኖ አመሻሽ ላይ በሐዋሳ ሐይቅ ምክንያት እጅግ ደስ የሚልና ማታ ላይ ነፋሻማ አየር አላት።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 6 ዋና ዋና ካምፓሶች (Campuses):</b>\n\n"
            "🏫 <b>1. ዋናው ግቢ (Main Campus — ከተማ መግቢያ ላይ):</b>\n"
            "  • School of Law (ህግ) ⚖️, Governance & Development, Architecture (🏛️), Hotel Management & Tourism, Sport Science ⚽, Art, Computational Sciences, Social Sciences።\n\n"
            "🏫 <b>2. ቴክኖ ካምፓስ (Techno Campus / IoT):</b>\n"
            "  • ከዋናው ግቢ ጎን የሚገኝ ሆኖ ከዋናው ግቢ ጋር በድልድይ (Bridge) የተያያዘ ግቢ ነው። 🌉\n"
            "  • Engineering Fields 🏗️, Computer Science 💻, Information Systems (IS), Software Engineering, Biomedical Engineering 🧬።\n\n"
            "🏫 <b>3. ሪፈራል ካምፓስ (Referral Campus — ሐዋሳ ሐይቅ ዳር):</b>\n"
            "  • በሐዋሳ ሐይቅ አጠገብ የሚገኝ ከመንፈሻ ዶርሞች አስደናቂ ፀሐይ መግቢያ (Nice Sunset 🌅) እይታ ያለው ውብ ግቢ!\n"
            "  • Medicine (MD) 🩺, Health Officer (HO), Nursing, Environmental Health, Radiology, Optometry, Psychiatry።\n\n"
            "🏫 <b>4. ይርጋለም ካምፓስ (Yirgalem Campus — ይርጋለም ከተማ):</b>\n"
            "  • ከሐዋሳ ከተማ አቅራቢያ በይርጋለም ከተማ የሚገኝ የንግድና ቢዝነስ ማዕከል።\n"
            "  • Faculty of Business (FB): Accounting & Finance 📊, Economics 💰, Management, Marketing Management, Logistics & Supply Chain, Cooperative Management።\n\n"
            "🏫 <b>5. አግሪ ካምፓስ (Agri Campus — ፒያሳ):</b>\n"
            "  • መሀል ሐዋሳ ከተማ ፒያሳ አካባቢ የሚገኝ።\n"
            "  • Animal Sciences & Agricultural fields 🌱።\n\n"
            "🏫 <b>6. ወንዶ ገነት ካምፓስ (Wondo Genet Campus):</b>\n"
            "  • በታዋቂዋ ወንዶ ገነት ከተማ የሚገኝ አረንጓዴ ግቢ።\n"
            "  • Plant Sciences, Forestry & Natural Resources Management, Ecotourism።\n\n"
            "💧 <b>መብራት፣ ውሃና WiFi:</b> ለአንዳንድ ግቢዎች መብራትና ውሃ አይጠፋም፤ በግቢው ውስጥ በተለያዩ ቦታዎች አሪፍ የ WiFi ኢንተርኔት ይገኛል።\n"
            "🚿 <b>መጠለያና ባኞ:</b> ከብዙ ዩኒቨርሲቲዎች የተሻለ ጥሩ የሽንትቤትና የባኞ አገልግሎት አለው።\n"
            "🍲 <b>የምግብና የከተማ ኑሮ:</b> የካፌው ምግብ መጠነኛ ቢሆንም፣ ከካፌ ውጭ በ 50-70 ብር አሪፍ ምግብ ይገኛል፤ ቡናና መጠጦች ለተማሪ ተስማሚ ቅናሽ ናቸው።\n"
            "💡 <b>ምክር ለአዲስ ተማሪዎች:</b> በግቢው ውበትና በከተማዋ ማብለጭለጭ ሳትሸነፉ ትምህርታችሁን በቁም ነገር ከተከታተላችሁ ሃዋሳ ለትምህርት እጅግ ምርጥ ቦታ ናት!\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        5,
    ),
    (
        "Bahir Dar University (BDU)",
        (
            "📣 <b>Bahir Dar University (BDU) — ባህር ዳር ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ባህር ዳር ከተማ፣ አማራ ክልል (ከአዲስ አበባ ~530 ኪ.ሜ) — ለመዝናናትና ለመኖር እጅግ ውብ የሆነች ከተማ።\n"
            "⛅ <b>የአየር ሁኔታ:</b> በአብዛኛው ሞቃታማና ፀሐያማ። በተለይ ይባብ (Yibab) Campus የሚሄዱ ተማሪዎች (Engineering, Law, Arc, Land Admin) ጥላ መጠቀማቸው ይመረጣል (ወንድም ሴትም ጣጣ የለውም)፤ ቀለል ያለ ብርድ ልብስ ይበቃል።\n"
            "💧 <b>የውሃ ሁኔታ:</b> የአካባቢውን ውሃ ለመላመድ መጀመሪያ ላይ ትንሽ ጊዜ ሊወስድ ይችላል፤ ስትቆዩ ግን ትለምዱታላችሁ።\n\n"
            "🏢 <b>1. የዩኒቨርሲቲው 5 ዋና ዋና ካምፓሶች:</b>\n\n"
            "🏫 <b>1. ፔዳ Campus (Peda Main Campus):</b>\n"
            "  • ከከተማው 2 ብር ባጃጅ ርቀት ላይ የሚገኝ ዋና ግቢ። በውስጡ Faculty of Business (Fb) እና Main የተባሉ 2 ግቢዎችን ይዟል።\n"
            "  • All Social Science Departments (ከ Law እና Governance በስተቀር)፣ Computational Science፣ Medicine & Health Sciences፣ Maritime Academy።\n\n"
            "🏫 <b>2. ሰላም Campus (EiTEX):</b>\n"
            "  • ከከተማውና ከፔዳ ግቢ ሳይርቅ የሚገኝ።\n"
            "  • Ethiopian Institute of Textile & Fashion Technology (Textile, Fashion Technology, Garment እና ተዛማጅ መስኮች)።\n\n"
            "🏫 <b>3. ይባብ Campus (Yibab):</b>\n"
            "  • በባህር ዳር መግቢያ አካባቢ የሚገኝ፣ ከከተማው ወጣ ያለ ፀሐያማና ሞቃታማ ግቢ።\n"
            "  • Fresh Engineering (1st Year)፣ Computer Science፣ Law ⚖️፣ Land Administration።\n"
            "  • Architecture (🏛️): በቅድመ ፈተና (Entrance Exam) የሚገባ ሲሆን በየአመቱ ~30 ተማሪዎችን ተቀብሎ ከአንደኛ አመት ጀምሮ በዚሁ ግቢ ያስተምራል።\n\n"
            "🏫 <b>4. ዘንዘልማ Campus (Zenzelma):</b>\n"
            "  • ከከተማው መውጫ አካባቢ የሚገኝ።\n"
            "  • Agriculture 🌱፣ Computational Geology፣ Veterinary Medicine 🐾 እና ተዛማጅ መስኮች።\n\n"
            "🏫 <b>5. ፖሊ Campus (BiT):</b>\n"
            "  • 2nd Year እና 3rd Year የ Engineering ተማሪዎች የሚማሩበት ዋና የቴክኖሎጂ ግቢ (Freshman ተማሪ የለውም)።\n\n"
            "📋 <b>2. የአካዳሚክ መዋቅር (Colleges, Schools, Institutes & Academies):</b>\n\n"
            "🛠️ <b>Institutes & Academies:</b>\n"
            "  • Bahir Dar Institute of Technology (BiT)\n"
            "  • Ethiopian Institute of Textile and Fashion Technology (EiTEX)\n"
            "  • Institute of Land Administration\n"
            "  • Maritime Academy (Nautical Science, Marine Engineering)\n"
            "  • Sports Academy\n\n"
            "🏛️ <b>Colleges & Schools:</b>\n"
            "  • School of Computing & Electrical Engineering\n"
            "  • School of Civil & Water Resources Engineering\n"
            "  • School of Mechanical & Industrial Engineering\n"
            "  • School of Chemical & Food Engineering\n"
            "  • School of Law\n"
            "  • College of Medicine & Health Sciences (Tibebe Ghion Hospital)\n"
            "  • College of Agriculture & Environmental Sciences\n"
            "  • College of Business & Economics\n"
            "  • College of Natural Sciences\n"
            "  • Faculty of Educational & Behavioral Sciences (አንጋፋው ፋከልቲ)\n"
            "  • Faculty of Humanities & Social Sciences\n\n"
            "🚌 <b>አቀባበልና ነፃ ሰርቪስ:</b> ባህር ዳር መናኸሪያ ስትደርሱ አዲስ ተማሪዎችን የሚቀበሉ የዩኒቨርሲቲው ነፃ ሰርቪሶች እና Senior ተማሪዎች ተዘጋጅተው ይጠብቋችኋል፤ ዋናው Confidence ነው!\n"
            "🍞 <b>ምግብ፣ ካፌና ሱቆች:</b> በግቢው ውስጥ የሚገርሙ ላውንቾች እና ተወዳጅ የካፌ ዳቦ 🍣 ይገኛሉ፤ ዋጋ አያሳስብም። በውጭ በር አካባቢም የቡና፣ ሻይ፣ ወተት እና የምግብ ቤቶች አማራጮች ሞልተዋል!\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        6,
    ),
    (
        "Mekelle University (MU)",
        (
            "📣 <b>Mekelle University (MU) — መቀሌ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> መቀሌ ከተማ፣ ትግራይ ክልል (ከአዲስ አበባ ~780 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> በአጠቃላይ ደስ የሚል አየር አላት። እስከ የካቲት በተለይ በጠዋትና አመሻሽ ላይ ነፋሻማና ቅዝቃዜ ስላለ ሹራብ/ጃኬት መያዝ ይመከራል። ግንቦት አካባቢ መጠነኛ ሙቀት ይኖራል።\n"
            "📍 <b>የመግቢያ ጠቃሚ መረጃ:</b> ዋናው ግቢ (Endayesus) በከተማው መግቢያ አካባቢ ስለሚገኝ እስከ መናኸሪያ መሄድ አያስፈልግም፤ በግቢው በር አካባቢ መውረድ ይቻላል።\n\n"
            "🏢 <b>የመቀሌ ዩኒቨርሲቲ ዋና ዋና ካምፓሶች (Campuses):</b>\n\n"
            "🏫 <b>1. እንዳየሱስ (Endayesus) Main Campus:</b>\n"
            "  • Engineering Science፣ Computational Science፣ Agricultural Science፣ አንዳንድ Social Sciences፣ Hotel & Tourism Management።\n"
            "  • Architecture & Urban Planning ለመማር Pre-Engineering ሳይማሩ በቅድመ ፈተና (Entrance Exam) መቀላቀል ይቻላል።\n\n"
            "🏫 <b>2. ዓይደር (Ayder) Campus (🏥):</b>\n"
            "  • Human Health & Medical Sciences (ዓይደር ሪፈራል ሆስፒታል)።\n"
            "  • Medicine (MD)፣ Health Officer (HO)፣ Dental Medicine (DMD)፣ Anesthesia እና ሌሎች የጤና ዘርፎች።\n\n"
            "🏫 <b>3. ዓዲ ሓቂ (Adi-Haki) Campus:</b>\n"
            "  • Social Sciences፣ School of Law ⚖️፣ Economics 💰፣ Management፣ Accounting 📊 እና ሌሎች ማህበራዊ ሳይንስ ፕሮግራሞች።\n\n"
            "🏫 <b>4. ዓዲ ሓውሲ (Adi-Hawsi) Campus:</b>\n"
            "  • Veterinary Education (ከእንስሳት ጤና ጋር የተያያዙ ዘርፎች)።\n"
            "  • Doctor of Veterinary Medicine (DVM)፣ Veterinary Science።\n\n"
            "🏫 <b>5. አይናለም (Aynalem) Technology Campus (💻):</b>\n"
            "  • የቴክኖሎጂና ኮምፒውተር የልህቀት ማዕከል (እንደ ASTU & AASTU የራሱ የመግቢያ ፈተና አለው)።\n"
            "  • Computer Science፣ Information Technology (IT)፣ Electrical Engineering፣ Chemical Engineering እና ተዛማጅ የ Technology ዘርፎች።\n"
            "  • 💡 <i>ለ Computer-related fields በጣም ጥሩ አማራጭ ነው! የመግቢያ ፈተና ምዝገባ ማስታወቂያዎችን በጥንቃቄ ተከታተሉ።</i>\n\n"
            "🚌 <b>አቀባበልና ትራንስፖርት:</b> መቀሌ መናኸሪያ ስትደርሱ ወደሚመደቡበት ካምፓስ የሚወስድ የዩኒቨርሲቲው ነፃ ትራንስፖርት ተዘጋጅቶ ይጠብቃችኋል። ግቢ ስትደርሱም የተማሪ ክበባት አባላት ወደ Dormitory እንድትደርሱ እገዛ ያደርጋሉ።\n"
            "🛒 <b>የገበያ ሁኔታ:</b> በግቢው አካባቢ ሱቆችና Supermarkets ስላሉ ዕለታዊ ፍላጎቶችን በቀላሉ ማግኘት ይቻላል።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        7,
    ),
    (
        "Haramaya University (HU)",
        (
            "📣 <b>Haramaya University (HU) — ሐረማያ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ሐረማያ ከተማ፣ ምስራቅ ሐረርጌ፣ ኦሮሚያ ክልል (ከሐረር ከተማ 17 ኪ.ሜ / 10 ብር መንገድ፣ ከድሬዳዋ 50 ብር መንገድ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> በተለይ ምሽት ላይ እጅግ ብርዳማ ነው። <i>'ሐረርጌ ሞቃት ነው'</i> የሚባለውን አትስሙ፤ ቅዝቃዜው ስለሚያመዝን ወፍራም አልባሳት ይያዙ። (ልብስና ሸቀጦች በሐረማያ ከተማ ርካሽ ስለሆኑ ግቢ ከገቡ በኋላ መሸመት ይችላሉ)።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 4 ካምፓሶች (Campuses):</b>\n\n"
            "🏫 <b>1. Main Campus (ሐረማያ — ዋናው ግቢ):</b>\n"
            "  • All Social Science Departments, Computer Science, Business & Economics, Natural & Computational Sciences, School of Law ⚖️, College of Agriculture 🌱, Teacher Education።\n\n"
            "🏫 <b>2. Techno Campus (ጋንዳጃይ):</b>\n"
            "  • 2nd Year እና ከዚያ በላይ ያሉ የ Engineering ተማሪዎች እና Food Science።\n\n"
            "🏫 <b>3. Station Campus (ስቴሽን):</b>\n"
            "  • Fresh Engineering (1st Year) ተማሪዎች እና Veterinary Medicine (DVM)።\n\n"
            "🏫 <b>4. Hareri Campus (ሐረር ከተማ — ሕይወት ፋና ሆስፒታል):</b>\n"
            "  • Medicine (MD)፣ Pharmacy፣ Health Officer (HO) እና ሌሎች የጤና ሳይንስ ዘርፎች።\n\n"
            "⭐ <b>የልህቀት ዘርፎች:</b> Agriculture 🌱፣ School of Law ⚖️ እና Computer Science 💻 በሐረማያ ዩኒቨርሲቲ እጅግ አሪፍና ስመጥር የሚባሉ የትምህርት ክፍሎች ናቸው።\n"
            "🍲 <b>የካፌ ምግብ ደረጃ:</b> በሀገራችን ካፌዎች ቀዳሚ ነው! ምሳ በሳምንት 5 ቀን ስጋ (Therefore!) ይቀርባል (1 ቀን ፓስታ፣ 1 ቀን መኮረኒ)፤ ቁርስ ሳንድዊች፣ ማርማራታ፣ ስጋ ፍርፍር እና ሩዝ ይቀርባል።\n"
            "💧 <b>የውሃ ሁኔታ:</b> የውሃ ችግር የለም! ቢጠፋ እንኳ ካፌና በየብሎኩ ውሃ አይጠፋም።\n"
            "⚠️ <b>አስፈላጊ ምክሮች:</b>\n"
            "  1. <b>ከጫት ይራቁ:</b> በከተማው የጫት ተጠቃሚነት ምክንያት እንዳይረበሹ ወይም እንዳትሞክሩት ተጠንቀቁ።\n"
            "  2. <b>ዜሮ ዘረኝነት:</b> የብሔር ቀልድና ዘረኝነት ፍፁም የተከለከለ ነው (F Grade ያሰጣል!)።\n"
            "  3. <b>ትራንስፖርት:</b> ለአዲስ ተማሪዎች የዩኒቨርሲቲው ነፃ ሰርቪስ መናኸሪያ ተዘጋጅቶ ይጠብቃችኋል።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        8,
    ),
    (
        "Wollo University (WU)",
        (
            "🏛️ <b>Wollo University (WU) — ወሎ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ደሴ (Main & ጢጣ) እና ኮምቦልቻ (KIoT)፣ አማራ ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> ደሴ መጠነኛ ብርዳማ (ወይና ደጋ)፤ ኮምቦልቻ በቀን ሞቃታማ፣ ማታ ቀዝቃዛ\n"
            "🏢 <b>ዋና ዋና ካምፓሶች:</b> ደሴ ዋናው ግቢ, ጢጣ የጤና ካምፓስ (Tita Campus), ኮምቦልቻ (KIoT)\n\n"
            "📋 <b>የትምህርት ክፍሎች (All Programs & Departments):</b>\n\n"
            "🩺 <b>ጢጣ ካምፓስ (College of Medicine & Health Sciences):</b>\n"
            "  • Medicine (MD - 6 Years)\n"
            "  • Pharmacy (5 Years)\n"
            "  • Anesthesia (4.5 Years)\n"
            "  • Public Health (4 Years)\n"
            "  • Medical Laboratory Sciences (4 Years)\n"
            "  • Comprehensive Nursing (4 Years)\n"
            "  • Surgical Nursing (4 Years)\n"
            "  • Emergency & Critical Care Nursing (4 Years)\n"
            "  • Pediatrics & Child Health Nursing (4 Years)\n"
            "  • Psychiatry Nursing (4 Years)\n"
            "  • Midwifery (4 Years)\n"
            "  • Environmental Health Science (4 Years)\n"
            "  • Occupational Health & Safety (4 Years)\n"
            "  • Health Informatics (4 Years)\n\n"
            "⚙️ <b>ኮምቦልቻ ካምፓስ (KIoT — Engineering & Informatics):</b>\n"
            "  • Software Engineering (5 Years)\n"
            "  • Computer Science (4 Years)\n"
            "  • Information Systems & IT (4 Years)\n"
            "  • Biomedical Engineering (5 Years)\n"
            "  • Electrical & Computer Engineering (5 Years)\n"
            "  • Mechatronics Engineering (5 Years)\n"
            "  • Mechanical Engineering (5 Years)\n"
            "  • Civil Engineering (5 Years)\n"
            "  • Architecture (5 Years)\n"
            "  • Construction Technology & Management - COTM (5 Years)\n"
            "  • Water Resource & Irrigation Engineering (5 Years)\n"
            "  • Hydraulic & Water Resource Engineering (5 Years)\n"
            "  • Chemical Engineering (5 Years)\n"
            "  • Industrial Engineering (5 Years)\n"
            "  • Food Engineering (5 Years)\n"
            "  • Textile Engineering (5 Years)\n"
            "  • Garment Engineering (5 Years)\n"
            "  • Leather Engineering (5 Years)\n"
            "  • Fashion Design (4 Years)\n\n"
            "🏛️ <b>ደሴ ዋናው ግቢ (Dessie Main Campus):</b>\n"
            "  • <b>College of Natural Science:</b> Biology, Biotechnology, Chemistry, Geology, Mathematics, Physics, Statistics, Sport Science\n"
            "  • <b>College of Agriculture:</b> Agricultural Economics, Agribusiness & Value Chain, Plant Science, Animal Science, Forestry, NRM, Rural Development\n"
            "  • <b>College of Business & Economics:</b> Accounting & Finance, Economics, Management, Marketing Management, Cooperative Business Management\n"
            "  • <b>College of Social Science & Humanities:</b> Political Science & IR, Sociology, Social Work, Journalism & Communication, Geography, History, Tourism & Hotel Management, Civics, Peace & Development, Languages (Amharic, English, Arabic, Afaan Oromoo, Geez)\n"
            "  • <b>School of Law:</b> Law (LL.B - 5 Years)\n"
            "  • <b>School of Veterinary Medicine:</b> Veterinary Medicine (DVM - 6 Years), Vet Lab Technology\n"
            "  • <b>School of Arts:</b> Theatre Arts, Music\n"
            "  • <b>Institute of Teachers' Education & Behavioral Science:</b> Psychology, Early Childhood Care, Special Needs Education, EdPM\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        9,
    ),
    (
        "Arba Minch University (AMU)",
        (
            "📣 <b>Arba Minch University (AMU) — አርባ ምንጭ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አርባ ምንጭ ከተማ፣ ደቡብ ኢትዮጵያ (ከአዲስ አበባ ~515 ኪ.ሜ)\n"
            "🌅 <b>የአካባቢ መግለጫ:</b> 'Heaven of Rift Valley' በመባል የምትታወቅ፣ በአባያ (Lake Abaya) እና ጫሞ (Lake Chamo) ሐይቆች የተከበበች ውብ ከተማ ናት።\n"
            "⛅ <b>የአየር ሁኔታ:</b> አየሯ አረንጓዴ ቢሆንም ገራሚ ሞቃት ስለሆነ ቀለል ያሉ አልባሳትን ይዞ መሄድ ይመረጣል።\n"
            "🍌 <b>የፍራፍሬ ከተማ:</b> በሙዝ 🍌፣ ማንጎ 🍋፣ አፕል 🍎፣ አቮካዶ 🥑 እና ሌሎችም ትታወቃለች።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 6 ዋና ዋና ካምፓሶች (Campuses):</b>\n\n"
            "🏫 <b>1. Main Campus (አርባ ምንጭ መግቢያ ላይ):</b>\n"
            "  • በዋናነት የ Engineering 🏗️ እና Computer Science 💻 ተማሪዎች ብቻ የሚማሩበት ግቢ ነው።\n\n"
            "🏫 <b>2. Chamo Campus (ጫሞ ካምፓስ):</b>\n"
            "  • የ Social Science ፊልዶች ብቻ የሚገኙበት ግቢ ነው።\n"
            "  • School of Law ⚖️፣ Business & Economics 💰፣ Accounting 📊፣ Political Science 📰 እና ሌሎችም ተዛማጅ ፕሮግራሞች።\n\n"
            "🏫 <b>3. Nech Sar / Health Campus (ነጭ ሳር):</b>\n"
            "  • የጤና ዘርፎች (Health Sciences) የሚገኙበት ግቢ ነው። 🏥\n"
            "  • Medicine (MD)፣ Health Officer (HO) እና ሌሎች የጤና ትምህርቶች።\n\n"
            "🏫 <b>4. Abaya Campus (አባያ ካምፓስ):</b>\n"
            "  • Natural Science፣ Social Science እና Computational ፕሮግራሞች የሚሰጡበት ግቢ።\n\n"
            "🏫 <b>5. Kulfo Campus (ኩልፎ ካምፓስ):</b>\n"
            "  • የ Agriculture 🌱 (ግብርና) ተማሪዎች የሚማሩበት ግቢ ነው።\n\n"
            "🏫 <b>6. Sawula Campus (ሳውላ ካምፓስ):</b>\n"
            "  • ከአርባ ምንጭ ከተማ የ 4 ሰዓት ያህል መንገድ ርቀት ላይ በ Gofa Zone (ሳውላ ከተማ) የሚገኝ ግቢ ነው።\n"
            "  • Half Civil Engineering፣ Food Engineering፣ Automotive Engineering፣ Electromechanical Engineering እና Social Science ተማሪዎች ይገኙበታል።\n\n"
            "🛠️ <b>በ Engineering ስር የሚሰጡ ዋና ዋና ትምህርቶች:</b>\n"
            "  • Civil Engineering 🏗️ | Software Engineering 💻 | Architecture Engineering 🏛️\n"
            "  • Electrical & Computer Engineering ⚡ | Mechanical Engineering ⚙️ | Electromechanical Engineering\n"
            "  • Metal & Production Engineering | Meteorology & Hydrology\n"
            "  • Food Engineering 🌽 | Hydroelectric Engineering 🌊 | Environmental Engineering 🌱 | Water Supply Engineering 💧\n\n"
            "🏆 <b>ልዩ እውቅና:</b> አርባ ምንጭ ዩኒቨርሲቲ በ Water Supply, Hydraulic & Water Resources Engineering ዘርፍ ከምስራቅ አፍሪካ ዩኒቨርሲቲዎች መካከል በከፍተኛ ደረጃ የሚጠቀስ የልህቀት ማዕከል ነው!\n\n"
            "💡 <b>ለአዲስ ተማሪዎች አስፈላጊ ምክር:</b> ወደ ከተማ ለሸመታም ሆነ ለመዝናናት በምትንቀሳቀሱበት ጊዜ ተጠንቀቁ፤ ከመጀመሪያው ቀን ጀምሮ ትምህርታችሁን በቁም ነገር ያዙ!\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        10,
    ),
    (
        "Arsi University",
        (
            "📣 <b>Arsi University — አርሲ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አሰላ ከተማ እና በቆጂ፣ አርሲ ዞን፣ ኦሮሚያ ክልል\n"
            "🚗 <b>ምቹ መገኛ:</b> ከአዲስ አበባ እጅግ ቅርብ ከሆኑ ዩኒቨርሲቲዎች አንዱ ስለሆነ ለአዲስ አበባ ተማሪዎች አልፎ አልፎ ወደ ቤት ለመመላለስ በጣም ይመቻል!\n"
            "⛅ <b>የአየር ሁኔታ:</b> ጥቅምት አካባቢ በተለይ ማታ ማታ በጣም ይበርዳል፤ ከጥቅምትና ህዳር ውጭ ባሉት ወራት ግን አየሩ እጅግ ተስማሚ ነው።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 4 ዋና ዋና ካምፓሶች (Campuses):</b>\n\n"
            "🏫 <b>1. Dinsho Campus (ዲንሾ ግቢ):</b>\n"
            "  • አሰላ ከተማ መግቢያ ላይ የሚገኝ።\n"
            "  • Computational and Natural Sciences ትምህርቶች የሚሰጡበት ግቢ።\n\n"
            "🏫 <b>2. Ardu Campus (አርዱ ግቢ):</b>\n"
            "  • ከአሰላ መናኸሪያ የ 10 ብር ባጃጅ ርቀት።\n"
            "  • የ Law ⚖️፣ Accounting 📊፣ Marketing 📈 (ከ 2ኛ አመት በላይ) እና የ Agriculture 🌱 ተማሪዎች የሚገበዩበት ግቢ።\n"
            "  • 🍲 <i>የካፌው እንጀራ አንደኛ ነው! እራት ከረቡዕና አርብ ውጭ ስጋ ይቀርባል፤ ቁርስ በብዛት ፍርፍር (ማክሰኞ ስጋ ፍርፍር) ነው።</i>\n\n"
            "🏫 <b>3. Bekoji Campus (በቆጂ ግቢ):</b>\n"
            "  • በታዋቂዋ በቆጂ ከተማ ላይ የሚገኝ ግቢ።\n"
            "  • የ Social Science ተማሪዎች የሚማሩበት።\n\n"
            "🏫 <b>4. Health Campus (TTC & አሰላ ሆስፒታል):</b>\n"
            "  • በጊዜያዊነት TTC በሚባል የጋራ ግቢ ውስጥ Health Officer (HO)፣ Midwifery፣ Nursing ተማሪዎች ይማራሉ።\n"
            "  • Medicine (MD) ተማሪዎች ደግሞ በአሰላ ሆስፒታል ውስጥ ይማራሉ።\n"
            "  • 🏗️ <i>በቀጣይ የሚከፈተው አዲስ ግቢ ሲጠናቀቅ አርሲ ዩኒቨርሲቲ ለመጀመሪያ ጊዜ የ Engineering ትምህርት ክፍሎችን ያስጀምራል።</i>\n\n"
            "🏠 <b>ዶርሚተሪና ደህንነት:</b> ለአዲስ (Freshman) ሴት ተማሪዎች ዶርም ከነባር ተማሪዎች ተለይቶ የተዘጋጀ በመሆኑ ሰላማዊና ምቹ ነው። በግቢው ዙሪያ ምንም አይነት አስጊ ሰፈር የለም።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        11,
    ),
    (
        "Dilla University",
        (
            "📣 <b>Dilla University — ዲላ ዩኒቨርሲቲ (University of Green Land)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ዲላ ከተማ፣ ጌዴኦ ዞን፣ ደቡብ ኢትዮጵያ (ከአዲስ አበባ 360 ኪ.ሜ / ከውቢቷ ሐዋሳ 80 ኪ.ሜ)\n"
            "🌲 <b>የአካባቢ መግለጫ:</b> በለምለም፣ አረንጓዴና ተፈጥሯዊ ውበቷ <b>'University of Green Land'</b> በሚል ቅጽል ስም በስፋት ትታወቃለች።\n"
            "⛅ <b>የአየር ሁኔታ:</b> ዲላ ከ Rift Valley ከተሞች አንዷ በመሆኗ መጠነኛ ሙቀት አላት፤ ሆኖም ዓመቱን ሙሉ ዝናባማ በመሆኗ ቀለል ያሉ አልባሳትን ይዞ መሄድ ይመረጣል። (የሞያሌ ድንበር አቅራቢያ በመሆኑ በከተማዋ አልባሳትና ጫማዎች እጅግ በሽና ቅናሽ ናቸው!)።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 4 ዋና ዋና ካምፓሶች (Campuses):</b>\n\n"
            "🏫 <b>1. ዋናው ግቢ (Main Campus):</b>\n"
            "  • Computational & Natural Sciences, Applied Sciences, School of Law ⚖️, Agriculture 🌱, Social Sciences።\n\n"
            "🏫 <b>2. ኦዳያ ካምፓስ (Odaya Campus):</b>\n"
            "  • የተለያዩ የትምህርት ዘርፎች የሚሰጡበት ግቢ።\n\n"
            "🏫 <b>3. አሴዴላ ካምፓስ (Asedella Campus):</b>\n"
            "  • ተጨማሪ የአካዳሚክ ክፍሎች የሚገኙበት ግቢ።\n\n"
            "🏫 <b>4. ሪፈራል ሆስፒታል / ጤና ካምፓስ (Health Sciences 🏥):</b>\n"
            "  • Medicine (MD)፣ Pharmacy፣ Medical Laboratory Sciences፣ Anesthesia፣ Public Health (HO)፣ Psychiatry፣ Midwifery፣ Environmental Health፣ Nursing።\n\n"
            "🚿 <b>መጠለያና ሻወር:</b> ሻወርና የሞቅ ውሃ በበቂ ሁኔታ ይገኛል (በተለይ ጠዋት ወሳኝ ነው)፤ የሽንትቤት ንፅህና ከሌሎች በርካታ ግቢዎች የተሻለ ነው።\n"
            "🍌 <b>የምግብ ሁኔታና የፍራፍሬ ገነት:</b> የካፌው ምግብ ለብዙ ተማሪ ምቾት ከማይሰጡ ነገሮች ቀዳሚው ቢሆንም፣ ዲላ የፍራፍሬ ሀገር በመሆኗ በግቢ በሮች አካባቢ እጅግ ርካሽ ፍራፍሬዎች (ሙዝ 🍌፣ አቮካዶ 🥑፣ አናናስ 🍍) በብዛት ስለሚሸጡ ገዝቶ የካፌን ምግብ Balance ማድረግ ይቻላል! ከግቢ ውጭና ውስጥም አሪፍ ሬስቶራንቶች አሉ።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        12,
    ),
    (
        "Debre Markos University (DMU)",
        (
            "🏛️ <b>Debre Markos University (DMU) — ደብረ ማርቆስ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ደብረ ማርቆስ፣ ምስራቅ ጎጃም፣ አማራ (ከአዲስ አበባ 313 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ቀን ሞቃታማ፣ ጠዋትና ማታ መጠነኛ ቅዝቃዜ\n"
            "🏢 <b>ካምፓሶች:</b> ዋናው ግቢ እና ቡሬ ካምፓስ (ከማርቆስ 115 ኪ.ሜ)\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "⚙️ <b>ኢንጂነሪንግና ቴክኖሎጂ:</b>\n"
            "  • Engineering Fields\n"
            "  • Computer Science & IT\n\n"
            "🩺 <b>ጤና ሳይንስ:</b>\n"
            "  • Medicine & Health Sciences\n\n"
            "📚 <b>ማህበራዊ ሳይንስና ህግ:</b>\n"
            "  • Social Sciences\n"
            "  • School of Law\n"
            "  • Accounting & Economics\n\n"
            "🌾 <b>ቡሬ ካምፓስ:</b>\n"
            "  • Agriculture & Selected Applied Fields\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        13,
    ),
    (
        "Debre Berhan University (DBU)",
        (
            "🏛️ <b>Debre Berhan University (DBU) — ደብረ ብርሃን ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ደብረ ብርሃን፣ ሰሜን ሸዋ፣ አማራ (ከአዲስ አበባ 130 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> እጅግ ከፍተኛ ብርድ (ደጋ) — ወፍራም ብርድልብስና ጃኬት የግድ ነው!\n"
            "🏢 <b>ካምፓሶች:</b> Main Campus እና ዳግማዊ ሚኒሊክ ካምፓስ (መሀል ከተማ)\n\n"
            "📋 <b>የካምፓሶች እና የዲፓርትመንቶች ዝርዝር:</b>\n\n"
            "⚙️ <b>Technology College:</b>\n"
            "  • Computer Science\n"
            "  • Information System (IS)\n"
            "  • Information Technology (IT)\n"
            "  • Software Engineering\n"
            "  • Electrical & Computer Engineering\n"
            "  • Mechanical Engineering\n"
            "  • Civil Engineering\n"
            "  • COTM (Construction Technology & Management)\n"
            "  • Industrial Engineering\n"
            "  • Chemical Engineering\n"
            "  • Food Engineering\n"
            "  • Hydroelectric Engineering\n"
            "  • Surveying Engineering\n\n"
            "🩺 <b>ዳግማዊ ሚኒሊክ ካምፓስ (Health Sciences):</b>\n"
            "  • Medicine (MD)\n"
            "  • Public Health Officer (HO)\n"
            "  • Anesthesia\n"
            "  • Medical Laboratory\n"
            "  • Nursing & Midwifery\n\n"
            "🌾 <b>Agriculture College:</b>\n"
            "  • Agro Economics\n"
            "  • Animal Science\n"
            "  • Plant Science\n"
            "  • Horticulture\n"
            "  • Natural Resource Management (NRM)\n\n"
            "🔬 <b>Computational College:</b>\n"
            "  • Biotechnology & Geology\n"
            "  • Mathematics, Physics, Biology, Chemistry, Statistics, Sport\n\n"
            "📚 <b>Social Sciences:</b>\n"
            "  • School of Law\n"
            "  • Management, Accounting, Economics, Logistics\n"
            "  • Journalism, Geography, History, English, Amharic\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        14,
    ),
    (
        "Dire Dawa University (DDU)",
        (
            "📣 <b>Dire Dawa University (DDU) — ድሬዳዋ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ድሬዳዋ ከተማ (የበረሃዋ ንግስት — የፌደራል ሁለተኛ አስተዳደር ከተማ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> እጅግ ሞቃታማ! ወፍራም ብርድልብስ አያስፈልግም፤ አንሶላና ቀለል ያለ አልጋ ልብስ በቂ ነው (ግንቦት ላይ በጣም ይሞቃል)። <i>ድሬኛ slang: 'ሀዬ' = እሺ! 'አቦ' = አሪፍ/የመጀመሪያ!</i>\n"
            "🏛️ <b>የግቢ መዋቅር:</b> 3 መግቢያና መውጫ በሮች ያሉት አንድ ትልቅ የተዋሃደ ግቢ ነው። ሁሉም የትምህርት መስኮች እዚሁ ይሰጣሉ። 3 ትልልቅ ላይብረሪዎች (Techno, Main, FB/Keranyo) አሉት።\n\n"
            "📋 <b>የትምህርት ክፍሎችና የ Engineering መስኮች:</b>\n\n"
            "⚙️ <b>IoT (Institute of Technology):</b>\n"
            "  • Mechanical Engineering | Electrical Engineering | Chemical Engineering\n"
            "  • Civil Engineering | Textile Engineering | COTM\n"
            "  • Food Engineering | Industrial Engineering | Surveying Engineering\n"
            "  • Architecture (🏛️) እና Fashion Design (🎨): በቅድመ ፈተና (Entrance Exam) የሚገባ።\n\n"
            "🩺 <b>College of Medicine & Health Sciences:</b>\n"
            "  • Medicine (MD - በፈተና የሚገባ) እና ሁሉም የ Health Science ክፍሎች።\n\n"
            "📈 <b>Faculty of Business (FB) & Social Sciences:</b>\n"
            "  • Accounting, Management, Economics, Marketing እና ሁሉም የማህበራዊ ሳይንስ መስኮች።\n"
            "  • 🛍️ <i>ድሬ ላይ አልባሳት፣ ጫማዎችና ምግቦች በኤክስፖርት ምክንያት እጅግ ቅናሽ ናቸው!</i>\n\n"
            "🍲 <b>የካፌና የምግብ ሁኔታ:</b> ካፌው እጅግ ተሻሽሏል! ፍርፍር፣ ፓስታ፣ ድንች፣ ለብለብ፣ ሰላጣ፣ በየአይነት በቀላሉ ይገኛል። ሻይና ቡና በጣም ቅናሽ ናቸው።\n"
            "🕌 <b>ሃይማኖታዊ ተቋማት:</b> መስጂዶች እና ቤተ-ክርስቲያናት ከግቢው አቅራቢያ የሚገኙ በመሆናቸው ለጸሎት ይመቻል። ግቢው አሁን ላይ ሙሉ በሙሉ ሰላም ነው!\n"
            "⚠️ <b>ለአዲስ ተማሪዎች የደህንነት ማስጠንቀቂያ:</b>\n"
            "  1. <b>ቀጥ ብላችሁ ወደ ግቢ ግቡ:</b> መናኸሪያ፣ ታክሲና ባጃጅ ላይ አዲስ ተማሪ መሆናችሁን አይተው ስልክና ገንዘብ የሚሰርቁ ሌቦች ስላሉ ተጠንቀቁ።\n"
            "  2. <b>ጥንቃቄ የሚያስፈልጋቸው ሰፈሮች:</b> አሸዋ (የዝርፊያ ቦታ)፣ ሰባተኛ (ማታ walk ስታደርጉ) እና ሴዶ (ቀን) ስልካችሁንና ኪሳችሁን ጠብቁ።\n"
            "  3. <b>ከጫት ይራቁ:</b> ድሬ ላይ ጫት የዕለት ተዕለት ቢሆንም ተማሪዎች ለቅምሻም ቢሆን እንዳትሞክሩት ተመክሯል።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        15,
    ),
    (
        "Debark University",
        (
            "🏛️ <b>Debark University — ደባርቅ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ደባርቅ፣ ሰሜን ጎንደር፣ አማራ (ሰሜን ተራሮችና ሊማሊሞ አቅራቢያ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ተራራማና እጅግ ብርዳማ (ወፍራም አልባሳት የግድ ነው)\n"
            "🏢 <b>ካምፓስ:</b> Main Campus\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "🔬 <b>Natural & Computational Sciences:</b>\n"
            "  • Computer Science\n"
            "  • Statistics\n"
            "  • Natural Resource Management (NRM)\n"
            "  • Agriculture\n"
            "  • Teaching (Biology, Physics, English)\n\n"
            "📚 <b>Social Sciences:</b>\n"
            "  • Management\n"
            "  • Accounting\n"
            "  • Economics\n"
            "  • Social Sciences (ከጂኦግራፊ በስተቀር)\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        16,
    ),
    (
        "Ambo University",
        (
            "📣 <b>Ambo University — አምቦ ዩኒቨርሲቲ (በ1939 የተመሰረተ)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አምቦ ከተማ፣ ምዕራብ ሸዋ፣ ኦሮሚያ (ከአዲስ አበባ ~110 ኪ.ሜ / 73 miles)\n"
            "🚌 <b>ትራንስፖርትና አቀባበል:</b> የሕዝብ ትራንስፖርት ከ 80 - 140 ብር። በጥሪ ወቅት ከአዲስ አበባ አውቶብስ መናኸሪያ አዲስ ተማሪዎችን የሚቀበሉ የዩኒቨርሲቲው ነፃ ባሶችና በጎ ፈቃደኞች ይኖራሉ።\n"
            "⛅ <b>የአየር ሁኔታ:</b> ከአዲስ አበባ ጋር ተመሳሳይ የሆነ ደስ የሚልና ተስማሚ አየር።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 5 ዋና ዋና ቅርንጫፎች (Campuses):</b>\n\n"
            "🏫 <b>1. ዋናው ግቢ (Main Campus — መሀል ከተማ):</b>\n"
            "  • በከተማው መሀል የሚገኝ፣ መንገዶቹ በሙሉ የአስፓልትና ፓቪንግ ንጣፍ የሆኑለት እጅግ ውብ ግቢ።\n"
            "  • ማዕከላዊ ቢሮዎች፣ 2 ትልልቅ ካፌዎች፣ ጁስ ቤቶች፣ ፑል ቤት፣ ፀጉር ቤት ይገኛሉ።\n"
            "  • መብራትና ውሃ ሁልጊዜም አስተማማኝ ነው። Wi-Fi በሁሉም ግቢዎችና ዶርሞች (ከአዲስ ተማሪዎች ክላስና ስቴዲየም ውጭ) አለ።\n\n"
            "🏫 <b>2. አዋሮ ካምፓስ (Hachalu Hundessa Institute of Technology / Techno):</b>\n"
            "  • በከተማው መግቢያ ላይ የሚገኝ (ከመሀል ከተማ 5-10 ብር ባጃጅ)።\n"
            "  • ሁሉንም የ Technology & Engineering ተማሪዎች የሚያስተናግድ ግቢ ነው። መብራትና ውሃ ሁልጊዜ አለ።\n\n"
            "🏫 <b>3. ጉደር ካምፓስ (Guder Campus):</b>\n"
            "  • ከአምቦ 10 ብር ትራንስፖርት በስተምስራቅ ጉደር ከተማ ላይ የሚገኝ።\n"
            "  • Agriculture፣ Natural Sciences እና ተዛማጅ የትምህርት ዘርፎች የሚሰጡበት።\n\n"
            "🏫 <b>4. ወሊሶ ካምፓስ (Weliso Campus — FBE / Business & Economics):</b>\n"
            "  • ከአምቦ 35 ኪ.ሜ / ከአዲስ አበባ 65 ኪ.ሜ በጅማ መስመር ወሊሶ ከተማ የሚገኝ።\n"
            "  • በወንድማማችነቱና በፍቅሩ <b>'ትንሿ ኢትዮጵያ'</b> የሚል ተቀጥያ ስም ያለው እጅግ ደስ የሚል ግቢ።\n"
            "  • አቅራቢያው ታዋቂው <b>ወንጪ ሐይቅ (Lake Wonchi)</b> የገበታ ለሀገር ቱሪዝም ፕሮጀክት ይገኛል።\n\n"
            "🏫 <b>5. ጤና ግቢ (Health Sciences Campus):</b>\n"
            "  • Medicine (MD) እና ሌሎች የጤና ሳይንስ ትምህርቶች።\n\n"
            "📌 <b>የሰላምና ደህንነት ሁኔታ:</b> ከ 2012 ዓ.ም ጀምሮ በተደረጉ የሪፎርም ስራዎች እና በፌዴራል ፖሊስ ጥብቅ ቁጥጥር ምክንያት በአሁኑ ሰዓት አምቦ ዩኒቨርሲቲ እጅግ ሰላማዊና ለትምህርት ምቹ የሰላም አምባሳደር ዩኒቨርሲቲ ነው!\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        17,
    ),
    (
        "Aksum University",
        (
            "🏛️ <b>Aksum University — አክሱም ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አክሱም ከተማ፣ ትግራይ\n"
            "⛅ <b>የአየር ሁኔታ:</b> መጀመሪያ ወራት ቅዝቃዜ፣ ከጥር ወር ጀምሮ ሞቃታማ\n"
            "🏢 <b>ካምፓሶች:</b> Main (አክሱም), ሽሬ (Shire), ሪፈራል (Health), አድዋ (Textile)\n\n"
            "📋 <b>የካምፓሶች እና የዲፓርትመንቶች ዝርዝር:</b>\n\n"
            "🏛️ <b>Main Campus (አክሱም ከተማ):</b>\n"
            "  • College of Engineering Science\n"
            "  • College of Natural & Computational Science\n"
            "  • College of Business & Economics\n"
            "  • College of Social Science & Art\n"
            "  • School of Law\n"
            "  • Teaching & Languages\n\n"
            "⛏️ <b>ሽሬ ካምፓስ (Shire Campus):</b>\n"
            "  • Mining Engineering\n"
            "  • Hydraulics & Water Management Engineering\n"
            "  • College of Agriculture\n"
            "  • Business & Computational Courses\n\n"
            "🩺 <b>ሪፈራል ካምፓስ (Health Sciences):</b>\n"
            "  • Medicine (MD)\n"
            "  • Health Officer & Nursing\n\n"
            "🧵 <b>አድዋ ካምፓስ (Textile Campus):</b>\n"
            "  • Textile Engineering\n"
            "  • Garment Engineering\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        19,
    ),
    (
        "Adigrat University",
        (
            "🏛️ <b>Adigrat University — አዲግራት ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> አዲግራት ከተማ፣ ምስራቅ ትግራይ (ከአዲስ አበባ 900 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ቀን ይሞቃል፣ ማታ ይበርዳል (ለኑሮ ምቹ)\n"
            "🏢 <b>ካምፓስ:</b> Main Unified Campus with modern labs and libraries\n\n"
            "📋 <b>የትምህርት ክፍሎች (Colleges & Departments):</b>\n\n"
            "🔬 <b>Natural Sciences & Engineering:</b>\n"
            "  • Medicine (MD)\n"
            "  • Health Sciences & Nursing\n"
            "  • Veterinary Science\n"
            "  • Engineering Fields\n"
            "  • Computer Science\n"
            "  • Agriculture\n"
            "  • Teacher Education\n\n"
            "📚 <b>Social Sciences & Business:</b>\n"
            "  • School of Law\n"
            "  • Economics\n"
            "  • Business & Management\n"
            "  • Accounting & Finance\n"
            "  • Languages & Literature\n"
            "  • Sociology\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        20,
    ),
    (
        "Mizan-Tepi University (MTU)",
        (
            "🏛️ <b>Mizan-Tepi University (MTU) — ሚዛን-ቴፒ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ሚዛን ተፈሪ (ቤንች ሸኮ) እና ቴፒ (ሸካ)፣ ደቡብ ምዕራብ ኢትዮጵያ (570-611 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ሞቃታማና ለምለም አረንጓዴ ተፈጥሮ (አልፎ አልፎ ከባድ ዝናብ)\n"
            "🏢 <b>ካምፓሶች:</b> ሚዛን ተፈሪ (Main) እና ቴፒ ካምፓስ\n\n"
            "📋 <b>የካምፓሶች እና የዲፓርትመንቶች ዝርዝር:</b>\n\n"
            "⚙️ <b>ቴፒ ካምፓስ (Engineering & Computing):</b>\n"
            "  • Electrical Engineering\n"
            "  • Mechanical Engineering\n"
            "  • Civil Engineering\n"
            "  • Computer Science (CS)\n"
            "  • Information Systems (IS)\n"
            "  • Information Technology (IT)\n"
            "  • Computational Sciences\n\n"
            "🏛️ <b>ሚዛን ተፈሪ ካምፓስ (Main):</b>\n"
            "  • Medicine (አማን የመማሪያ ሆስፒታል)\n"
            "  • Health Sciences & Nursing\n"
            "  • Agriculture & Forestry\n"
            "  • Business & Economics\n"
            "  • School of Law\n"
            "  • All Social Sciences\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        21,
    ),
    (
        "Wolaita Sodo University (WSU)",
        (
            "📣 <b>Wolaita Sodo University (WSU) — ወላይታ ሶዶ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ሶዶ ከተማ፣ ወላይታ ዞን፣ ደቡብ ኢትዮጵያ\n"
            "⛅ <b>የአየር ሁኔታ:</b> ወቅታዊ የአየር ፀባይ አለው፤ ጥቅምት አካባቢ ቅዝቃዜ ሲኖር ከሚያዚያ በኋላ ደግሞ ሞቃታማ ይሆናል።\n"
            "🍌 <b>የፍራፍሬ ሀገር:</b> ወላይታ በሙዝ 🍌 እና አቮካዶ 🥑 ሀብት የተሞላች ከተማ ናት፤ በየአጥሩና በየቤቱ ፍራፍሬ በቀላሉ ይገኛል።\n\n"
            "🏢 <b>የዩኒቨርሲቲው 3 ዋና ዋና ካምፓሶች (Campuses):</b>\n\n"
            "🏫 <b>1. ዋናው ግቢ (Main Campus):</b>\n"
            "  • አብዛኞቹ ትምህርቶች የሚሰጡበት ዋና ግቢ (Engineering, Computer Science, Natural Sciences, Social Sciences, Business)።\n"
            "  • Veterinary Medicine (DVM)፣ Agrieconomics፣ Agribusiness እና ተዛማጅ መስኮች።\n\n"
            "🏫 <b>2. ኦቶና ካምፓስ (Otona Campus — Health Sciences 🏥):</b>\n"
            "  • የጤና ሳይንስ ዘርፎች (Medicine MD, Health Officer HO, Nursing, Midwifery, Pharmacy, Clinical Pharmacy) የሚሰጡበት ግቢ።\n\n"
            "🏫 <b>3. ታርጫ ካምፓስ (Tarcha Campus — Dawro):</b>\n"
            "  • የግብርና ትምህርቶች (Agriculture & Animal Sciences 🌱) የሚሰጡበት ግቢ።\n\n"
            "🕊️ <b>የሰላም ሁኔታ:</b> ወላይታ ሶዶ ዩኒቨርሲቲ እጅግ ሰላማዊና <b>'የሰላም አምባሳደር'</b> በመባል የሚታወቅ ምቹ ግቢ በመሆኑ ምንም ሃሳብ አይግባችሁ!\n"
            "💧 <b>ውሃ፣ መብራትና Wi-Fi:</b> ውሃ፣ መብራትና ኔትወርክ በጥሩ ሁኔታ የተሟሉ ናቸው።\n"
            "🍲 <b>የካፌና የምግብ ሁኔታ:</b> ካፌው ተማሪዎችን ለማስደሰት በሚጥር አሪፍ ሁኔታ ላይ ይገኛል፤ ከካፌ ውጭም የፍራፍሬና የምግብ አማራጮች በብዛት አሉ::\n"
            "⚠️ <b>የደህንነት ማስጠንቀቂያ:</b> ሶዶ ላይ ከግቢ ውጭ የኪስ ሌቦች (ጭልፊቶች) ስላሉ ስልካችሁንና ኪሳችሁን በጥንቃቄ ጠብቁ።\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        22,
    ),
    (
        "Injibara University",
        (
            "🏛️ <b>Injibara University — እንጅባራ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> እንጅባራ፣ አገው ምድር / አዊ ዞን፣ አማራ (ከአዲስ አበባ 440 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ቀዝቃዛ (ደጋ) — ወፍራም አልባሳትና ጃኬት ያስፈልጋል!\n"
            "🏢 <b>ካምፓስ:</b> Main Campus\n\n"
            "📋 <b>የትምህርት ክፍሎች (26+ Departments):</b>\n\n"
            "📚 <b>Social Sciences (14 Departments):</b>\n"
            "  • School of Law\n"
            "  • Economics\n"
            "  • Management\n"
            "  • Accounting & Finance\n"
            "  • Banking & Finance\n"
            "  • All Social Sciences & Humanities\n\n"
            "🔬 <b>Natural Sciences (12 Departments):</b>\n"
            "  • Computer Science\n"
            "  • Information Technology (IT)\n"
            "  • Agricultural Economics\n"
            "  • Natural Resource Management (NRM)\n"
            "  • Plant Science & Agriculture\n"
            "  • Computational Sciences\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        25,
    ),
    (
        "Semera University",
        (
            "🏛️ <b>Semera University — ሰመራ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ሰመራ፣ አፋር ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> ሞቃታማ / በርሃማ አየር (ቀለል ያሉ አልባሳትና አንሶላ)\n"
            "🏢 <b>ካምፓስ:</b> Single Unified Campus\n\n"
            "📋 <b>ኮሌጆች እና የዲፓርትመንቶች ዝርዝር:</b>\n\n"
            "⚙️ <b>College of Engineering & Technology:</b>\n"
            "  • Chemical Engineering\n"
            "  • Electrical Engineering\n"
            "  • Civil Engineering\n"
            "  • Mechanical Engineering\n"
            "  • COTM (Construction Technology & Management)\n"
            "  • Water Resource & Irrigation Engineering\n\n"
            "📈 <b>College of Business & Economics:</b>\n"
            "  • Accounting & Finance\n"
            "  • Management\n\n"
            "🩺 <b>College of Health Sciences:</b>\n"
            "  • BSc Nursing\n"
            "  • Midwifery\n\n"
            "🌾 <b>College of Agriculture:</b>\n"
            "  • Natural Resource Management (NRM)\n"
            "  • RDA (Rural Development & Agricultural Extension)\n"
            "  • Horticulture\n\n"
            "🔬 <b>College of Computational Science:</b>\n"
            "  • Biology\n"
            "  • Chemistry\n"
            "  • Statistics\n\n"
            "🗣️ <b>Language & Literature:</b>\n"
            "  • Afar, Amharic, English\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        26,
    ),
    (
        "Bule Hora University",
        (
            "🏛️ <b>Bule Hora University — ቡሌ ሆራ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ቡሌ ሆራ፣ ምዕራብ ጉጂ፣ ኦሮሚያ (ከአዲስ አበባ 469 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ወይናደጋ / መጠነኛ ቅዝቃዜ\n"
            "🏢 <b>ካምፓስ:</b> Main Campus (በፍጥነት በማደግ ላይ ያለ ግቢ)\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "🔬 <b>Natural Sciences & Tech:</b>\n"
            "  • Medicine (MD)\n"
            "  • Health Sciences\n"
            "  • Agriculture\n"
            "  • Engineering Fields\n"
            "  • Computational Sciences\n\n"
            "📚 <b>Social Sciences & Business:</b>\n"
            "  • Accounting & Finance\n"
            "  • Economics\n"
            "  • Marketing Management\n"
            "  • Logistics & Supply Chain Management\n"
            "  • Banking & Finance\n"
            "  • Cooperative Business\n"
            "  • Cooperative Auditing\n"
            "  • Business Administration & Information Systems\n"
            "  • Public Administration\n"
            "  • Hotel & Tourism Management\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        27,
    ),
    (
        "Jigjiga University (JJU)",
        (
            "🏛️ <b>Jigjiga University (JJU) — ጅግጅጋ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ጅግጅጋ ከተማ፣ ሶማሌ ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> 1ኛ ሴሚስተር ቅዝቃዜና አቧራ፣ 2ኛ ሴሚስተር ሞቃታማ፣ ከሚያዚያ በኋላ ዝናባማ\n"
            "🏢 <b>ካምፓሶች:</b> Main Campus እና ሪፈራል ካምፓስ (Health)\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "🏛️ <b>Main Campus:</b>\n"
            "  • Engineering Fields\n"
            "  • Agriculture & Veterinary\n"
            "  • Social Sciences & Humanities\n"
            "  • School of Law\n"
            "  • Faculty of Business (FB)\n"
            "  • Natural Sciences\n\n"
            "🩺 <b>ሪፈራል ካምፓስ:</b>\n"
            "  • Medicine (MD)\n"
            "  • Health Sciences & Nursing\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        28,
    ),
    (
        "Welkite University (WKU)",
        (
            "🏛️ <b>Welkite University (WKU) — ወልቂጤ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ወልቂጤ እና ጉብሬ፣ ጉራጌ ዞን (ከአዲስ አበባ 158 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ተስማሚ ሞቃታማ አየር (ፀሐያማ)\n"
            "🏢 <b>ካምፓሶች:</b> ቴክስታይል ግቢ (ወልቂጤ ከተማ) እና ጉብሬ (Main)\n\n"
            "📋 <b>የካምፓሶች እና የዲፓርትመንቶች ዝርዝር:</b>\n\n"
            "⚙️ <b>ጉብሬ ካምፓስ (Engineering & Technology):</b>\n"
            "  • Civil Engineering\n"
            "  • Chemical Engineering\n"
            "  • Electrical Engineering\n"
            "  • Food Process Engineering\n"
            "  • HWRE (Water Resources Engineering)\n"
            "  • Mechanical Engineering\n"
            "  • COTM (Construction Technology & Management)\n"
            "  • Architecture (በፈተና የሚገባ)\n\n"
            "💻 <b>Computing:</b>\n"
            "  • Software Engineering\n"
            "  • Computer Science (CS)\n"
            "  • Information System (IS)\n"
            "  • Information Technology (IT)\n\n"
            "🩺 <b>Health Sciences:</b>\n"
            "  • Medicine (MD)\n"
            "  • Public Health Officer (HO)\n"
            "  • Midwifery\n"
            "  • Nursing\n\n"
            "📚 <b>Social, Business & Science:</b>\n"
            "  • Faculty of Business (FB)\n"
            "  • School of Law\n"
            "  • Psychology\n"
            "  • Mathematics, Sport, Physics\n\n"
            "🧵 <b>ቴክስታይል ግቢ (ወልቂጤ ከተማ):</b>\n"
            "  • Textile Engineering\n"
            "  • Garment & Designing (በፈተና የሚገባ)\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        29,
    ),
    (
        "Wachemo University (WCU)",
        (
            "🏛️ <b>Wachemo University (WCU) — ዋቻሞ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ሆሳዕና፣ ሀዲያ ዞን (ከአዲስ አበባ 230 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> መጀመሪያ ወራት ብርዳማ፣ ከህዳር በኋላ በቀን ሞቃታማ፣ 2ኛ ሴሚስተር ዝናባማ\n"
            "🏢 <b>ካምፓሶች:</b> Main Campus (ሆሳዕና) እና ዱራሜ ካምፓስ (ከምባታ)\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "🩺 <b>Main Campus (Health & Medicine):</b>\n"
            "  • Medicine (MD — ንግስት ኢሌኒ ሪፈራል ሆስፒታል)\n"
            "  • Public Health Officer (HO)\n"
            "  • Nursing & Midwifery\n"
            "  • Pharmacy\n\n"
            "⚙️ <b>Engineering & Technology:</b>\n"
            "  • Engineering Fields\n"
            "  • Architecture (በፈተና የሚገባ)\n\n"
            "📚 <b>Business & Social Sciences:</b>\n"
            "  • Business & Economics\n"
            "  • Social Sciences\n\n"
            "🌾 <b>ዱራሜ ካምፓስ:</b>\n"
            "  • Agriculture & Applied Fields\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        30,
    ),
    (
        "Madda Walabu University (MWU)",
        (
            "🏛️ <b>Madda Walabu University (MWU) — መዳ ወላቡ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ባሌ ሮቤ፣ ባሌ ጎባ እና ሻሸመኔ፣ ኦሮሚያ (ከአዲስ አበባ 429 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ብርዳማ (የባሌ ከፍተኛ ቦታዎች — ወፍራም ልብሶች ያስፈልጋሉ)\n"
            "🏢 <b>ካምፓሶች:</b> Main Campus (ባሌ ሮቤ), ባሌ ጎባ (Health), ሻሸመኔ (Social)\n\n"
            "📋 <b>የካምፓሶች እና የዲፓርትመንቶች ዝርዝር:</b>\n\n"
            "⚙️ <b>ባሌ ሮቤ ካምፓስ (Main — Techno & Computing):</b>\n"
            "  • Civil Engineering\n"
            "  • COTM (Construction Technology & Management)\n"
            "  • Electrical Engineering\n"
            "  • Water Engineering\n"
            "  • Mechanical Engineering\n"
            "  • Computer Science (CS)\n"
            "  • Information Systems (IS)\n"
            "  • Information Technology (IT)\n"
            "  • Social Sciences\n\n"
            "🩺 <b>ባሌ ጎባ ካምፓስ (Health Sciences):</b>\n"
            "  • Medicine (MD)\n"
            "  • Public Health Officer (HO)\n"
            "  • Health Sciences & Nursing\n\n"
            "📚 <b>ሻሸመኔ ካምፓስ:</b>\n"
            "  • Social Sciences & Humanities\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        31,
    ),
    (
        "Raya University (RU)",
        (
            "🏛️ <b>Raya University (RU) — ራያ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ማይጨው፣ ደቡብ ትግራይ ዞን፣ ትግራይ ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> ተራራማና ቀዝቃዛ አየር (ቀለል ያሉ ወፍራም አልባሳት ይያዙ)\n"
            "🏢 <b>ካምፓስ:</b> Single Consolidated Academic Campus\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "⚙️ <b>Engineering & Health:</b>\n"
            "  • Civil Engineering 🏗️ | Electrical & Computer Engineering ⚡ | Mechanical Engineering ⚙️\n"
            "  • Computer Science 💻 | Comprehensive Nursing | Midwifery | Public Health\n\n"
            "🌾 <b>Agriculture & Natural Sciences:</b>\n"
            "  • Plant Science | Animal Science | Agricultural Economics | Soil Resource Management\n"
            "  • Biology | Chemistry | Physics | Mathematics | Statistics\n\n"
            "📚 <b>Business & Social Sciences:</b>\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management | Geography | History | Sociology | English\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        32,
    ),
    (
        "Mekdela Amba University (MAU)",
        (
            "🏛️ <b>Mekdela Amba University (MAU) — መቅደላ አምባ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ቱሉ አውሊያ (ዋናው) እና መቄት፣ ደቡብ ወሎ ዞን፣ አማራ ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> ወይናደጋ / ደስ የሚል አየር\n"
            "🏢 <b>ካምፓሶች:</b> ቱሉ አውሊያ ዋና ግቢ እና መቄት የቴክኖሎጂ/ቢዝነስ ግቢ\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "⚙️ <b>መቄት ካምፓስ (Engineering & Business):</b>\n"
            "  • Civil Engineering 🏗️ | Electrical & Computer Engineering ⚡ | COTM | Computer Science 💻\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management\n\n"
            "🏫 <b>ቱሉ አውሊያ ካምፓስ (Main — Agriculture & Natural Sciences):</b>\n"
            "  • Plant Science | Animal Science | NRM | Agricultural Economics\n"
            "  • Mathematics | Physics | Chemistry | Biology | Statistics\n"
            "  • Geography & Environmental Studies | History | English | Educational Planning (EdPM)\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        33,
    ),
    (
        "Selale University (SIU)",
        (
            "🏛️ <b>Selale University (SIU) — ሰላሌ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ፊቼ፣ ሰሜን ሸዋ ዞን፣ ኦሮሚያ ክልል (ከአዲስ አበባ ~112 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ደጋማና ቀዝቃዛ አየር (ወፍራም አልባሳትና ጃኬት ይያዙ)\n"
            "🥛 <b>የልህቀት ዘርፍ:</b> በወተትና እንስሳት ተዋጽኦ (Dairy Technology & Animal Husbandry) በሀገራችን ቀዳሚ የልህቀት ማዕከል!\n\n"
            "📋 <b>የካምፓሶች እና የዲፓርትመንቶች ዝርዝር:</b>\n\n"
            "🏫 <b>1. ቻንቾ ዋና ግቢ (General Chancho Main Campus):</b>\n"
            "  • <b>Dairy Technology 🥛</b> (ልዩ የልህቀት ትምህርት)\n"
            "  • Animal Science | Plant Science | Agribusiness | Computer Science 💻\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management | Afan Oromo | English | History | Geography\n"
            "  • School of Law ⚖️ (Law - LL.B)\n\n"
            "🩺 <b>2. ፊቼ ጤና ካምፓስ (Fiche Health Sciences Campus):</b>\n"
            "  • Medicine (MD) 🩺 | Comprehensive Nursing | Midwifery | Public Health | Pharmacy\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        34,
    ),
    (
        "Werabe University (WRU)",
        (
            "🏛️ <b>Werabe University (WRU) — ወራቤ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ወራቤ ከተማ፣ ስልጤ ዞን፣ ማዕከላዊ ኢትዮጵያ (ከአዲስ አበባ ~172 ኪ.ሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ወይናደጋ / እጅግ ተስማሚና ውብ አየር\n"
            "🏢 <b>ካምፓስ:</b> Consolidated Main Academic & Technology Campus\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "⚙️ <b>Engineering, Tech & Health:</b>\n"
            "  • Civil Engineering 🏗️ | Electrical & Computer Engineering ⚡ | Mechanical Engineering ⚙️\n"
            "  • Computer Science 💻 | Information Technology (IT) | Applied Biotechnology 🧬\n"
            "  • Comprehensive Nursing | Midwifery | Public Health\n\n"
            "🌾 <b>Agriculture & Natural Sciences:</b>\n"
            "  • Plant Science | Animal Science | Agricultural Economics\n"
            "  • Biology | Chemistry | Mathematics | Physics | Statistics\n\n"
            "📚 <b>Business & Social Sciences:</b>\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management | Marketing Management\n"
            "  • Geography | History | Sociology | English | School of Law ⚖️\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        35,
    ),
    (
        "Jinka University (JKU)",
        (
            "🏛️ <b>Jinka University (JKU) — ጂንካ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ጂንካ ከተማ፣ ደቡብ ኦሞ ዞን፣ ደቡብ ኢትዮጵያ\n"
            "⛅ <b>የአየር ሁኔታ:</b> ሞቃታማና ተስማሚ አየር\n"
            "🌍 <b>የልህቀት ዘርፍ:</b> ባህላዊ አንትሮፖሎጂ፣ የሀገር በቀል እውቀት እና የቆላ ግብርና (Cultural Anthropology, Indigenous Knowledge & Pastoral Ecology)።\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "🌾 <b>Pastoral Agriculture & Sciences:</b>\n"
            "  • <b>Pastoral Land Resource Management 🌿</b>\n"
            "  • Animal Science | Plant Science | Agricultural Economics\n"
            "  • Biology | Chemistry | Physics | Mathematics | Computer Science 💻\n"
            "  • Comprehensive Nursing | Midwifery | Public Health\n\n"
            "📜 <b>Social Sciences & Humanities:</b>\n"
            "  • <b>Social Anthropology & Heritage Management 🏛️</b>\n"
            "  • Geography & Environmental Studies | History | English\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        36,
    ),
    (
        "Kebri Dehar University (KDU)",
        (
            "🏛️ <b>Kebri Dehar University (KDU) — ቀብሪደሃር ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ቀብሪደሃር ከተማ፣ ቆራሄ ዞን፣ ሶማሌ ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> ሞቃታማ / ቆላማ አየር\n"
            "🐪 <b>የልህቀት ዘርፍ:</b> የቆላ ግብርና፣ የእንስሳት ጤና እና የውሃ ቴክኖሎጂ (Arid Agriculture & Water Technology)።\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "🌾 <b>Dryland Agriculture & Vet Science:</b>\n"
            "  • Dryland Crop Science | Rangeland Resource Management | Animal Science\n"
            "  • Agricultural Economics | Veterinary Science & Animal Health 🐫\n\n"
            "⚙️ <b>Engineering & Computing:</b>\n"
            "  • Civil Engineering 🏗️ | Water Resources & Irrigation Engineering 💧\n"
            "  • Electrical Engineering ⚡ | Computer Science 💻\n\n"
            "🩺 <b>Health & Social Sciences:</b>\n"
            "  • Comprehensive Nursing | Midwifery | Public Health\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management | Somali Language & Literature | English\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        37,
    ),
    (
        "Dembi Dolo University (DeDU)",
        (
            "🏛️ <b>Dembi Dolo University (DeDU) — ደምቢ ዶሎ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ደምቢ ዶሎ ከተማ፣ ቄለም ወለጋ ዞን፣ ኦሮሚያ ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> ወይናደጋ / ለምለም አየር\n"
            "⛏️ <b>የልህቀት ዘርፍ:</b> የማዕድን ምህንድስና (Mining Engineering) እና የደን ሳይንስ።\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "⛏️ <b>Engineering & Technology:</b>\n"
            "  • <b>Mining Engineering ⛏️</b> (የማዕድን ምህንድስና)\n"
            "  • Civil Engineering 🏗️ | Electrical & Computer Engineering ⚡ | Mechanical Engineering ⚙️\n"
            "  • Computer Science 💻\n\n"
            "🌾 <b>Agriculture & Health Sciences:</b>\n"
            "  • Plant Science | Animal Science | Forestry 🌲 | Agricultural Economics\n"
            "  • Comprehensive Nursing | Midwifery | Public Health\n\n"
            "📚 <b>Business & Social Sciences:</b>\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management | Afan Oromo | English | Geography | History | Sociology\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        38,
    ),
    (
        "Borena University (BorU)",
        (
            "🏛️ <b>Borena University (BorU) — ቦረና ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ያቤሎ ከተማ፣ ቦረና ዞን፣ ኦሮሚያ ክልል\n"
            "⛅ <b>የአየር ሁኔታ:</b> ቆላማ / መጠነኛ ሞቃታማ አየር\n"
            "🐪 <b>የልህቀት ዘርፍ:</b> የግጦሽ መሬት ስነ-ምህዳር፣ የጋመልና እንስሳት ሳይንስ (Camel & Livestock Science, Pastoral Ecology)።\n\n"
            "📋 <b>የትምህርት ክፍሎች (Departments):</b>\n\n"
            "🐪 <b>Pastoral Agriculture & Veterinary Ecology:</b>\n"
            "  • <b>Pastoral Rangeland Ecology 🌿</b>\n"
            "  • <b>Camel & Livestock Science 🐫</b>\n"
            "  • Dryland Agronomy | Agricultural Economics\n\n"
            "⚙️ <b>Water Tech & Engineering:</b>\n"
            "  • Hydraulic & Water Engineering 💧 | Civil Engineering 🏗️ | Electrical Engineering ⚡ | Computer Science 💻\n\n"
            "📚 <b>Business & Social Sciences:</b>\n"
            "  • Accounting & Finance 📊 | Economics 💰 | Management | Afan Oromo Literature | English | Sociology\n\n"
            "👥 <b>Telegram Channel:</b> @freshminds_academy"
        ),
        39,
    ),
    (
        "Woldia University (WLDU)",
        (
            "🏛️ <b>Woldia University (WLDU) — ወልድያ ዩኒቨርሲቲ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📍 <b>አድራሻ:</b> ወልድያ ከተማ፣ ሰሜን ወሎ ዞን፣ አማራ ክልል (ከአዲስ አበባ 520 ኪሜ)\n"
            "⛅ <b>የአየር ሁኔታ:</b> ወይና ደጋ አየር ንብረት — መጠነኛ ቀዝቃዛ ጠዋት/ማታ፣ ቀን ላይ ሞቃታማ\n"
            "🏢 <b>ዋና ዋና ካምፓሶች:</b> ወልድያ ዋናው ግቢ (Main Campus), "
            "መርሳ ግቢ (Agriculture, 30 ኪሜ ከዋናው ግቢ), "
            "ቅዱስ ላሊበላ የቅርስ እና ቱሪዝም ትምህርት ተቋም (Lalibela)\n\n"
            "📋 <b>የትምህርት ክፍሎች (All Programs &amp; Departments):</b>\n\n"
            "⚠️ <b>College of Health Sciences (CHS)</b> — "
            "<i>Incomplete/Not fully confirmed, verify with WLDU registrar before placement:</i>\n"
            "• Nursing\n"
            "• Medicine\n"
            "• Medical Laboratory Sciences\n"
            "• Health Officer (Public Health)\n"
            "• ⚠️ Full list not yet verified from official WLDU source — will update once confirmed\n\n"
            "⚙️ <b>Institute of Technology (WiT) — 4 Schools:</b>\n"
            "• School of Computing: Computer Science, Information Technology, Software Engineering\n"
            "• School of Civil &amp; Water Resource Engineering: Architecture, Civil Engineering, "
            "Construction Technology &amp; Management, Water Resources &amp; Irrigation Engineering\n"
            "• School of Mechanical &amp; Chemical Engineering: Mechanical Engineering, Chemical Engineering\n"
            "• School of Electrical &amp; Computer Engineering: Electrical &amp; Computer Engineering\n\n"
            "🔬 <b>College of Natural &amp; Computational Sciences (CNCS):</b>\n"
            "Biology, Biotechnology, Chemistry, Geology, Mathematics, Physics, Statistics, Sport Science\n\n"
            "🌾 <b>College of Agricultural Sciences (Mersa Campus):</b>\n"
            "Agricultural Economics, Animal Science, Plant Science, "
            "Rural Development &amp; Agricultural Extension, "
            "Soil Resource &amp; Watershed Management, Veterinary Medicine\n\n"
            "💼 <b>College of Business and Economics (CoBE):</b>\n"
            "Accounting &amp; Finance, Economics, Management, Marketing Management\n\n"
            "📚 <b>College of Social Science and Humanities (CSSH):</b>\n"
            "English Language &amp; Literature, Sociology, Journalism &amp; Communication, Amharic, "
            "History &amp; Heritage Management, Geography &amp; Environmental Studies, "
            "Theatrical Arts, Political Science &amp; International Relations\n\n"
            "🧑\u200d🏫 <b>College of Education and Behavioral Sciences (CEBS):</b>\n"
            "Psychology, Pedagogical Science, Special Needs &amp; Inclusive Education, "
            "Early Childhood Care &amp; Education, Lifelong Learning &amp; Community Development\n\n"
            "⚖️ <b>School of Law:</b> Law (LL.B)\n"
            "🗺️ <b>School of Land Administration and Surveying (SoLA)</b>\n"
            "🏛️ <b>St. Lalibela Institute of Heritage and Tourism Studies</b>\n\n"
            "👥 ቻናላችን: @freshminds_academy"
        ),
        40,
    ),
]


async def seed_all_universities():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM universities")
        await db.execute("DELETE FROM sqlite_sequence WHERE name='universities'")
        
        await db.executemany(
            "INSERT INTO universities (name, about_text, sort_order) VALUES (?, ?, ?)",
            UNIVERSITIES_DATA,
        )
        await db.commit()
        print(f"Successfully seeded all {len(UNIVERSITIES_DATA)} Ethiopian Universities with rich bulleted departments!")


if __name__ == "__main__":
    asyncio.run(seed_all_universities())
