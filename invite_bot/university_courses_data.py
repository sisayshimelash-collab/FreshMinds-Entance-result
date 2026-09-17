"""
FreshMinds Academy — University 1st Semester Course Data Provider
Source of Truth: FreshMinds_Academy_Freshman_Course_Guide.md
"""

import os
import re
from typing import Dict, List, Optional

GUIDE_MD_PATH = os.path.join(os.path.dirname(__file__), "FreshMinds_Academy_Freshman_Course_Guide.md")

# Fallback structured dataset directly extracted from FreshMinds_Academy_Freshman_Course_Guide.md
UNIVERSITY_COURSES_DB: Dict[str, Dict[str, List[str]]] = {
    "Addis Ababa University (AAU)": {
        "Social": ["Global Trends", "Anthropology", "Emerging Technologies", "Moral & Ethical Education", "Economics", "Entrepreneurship", "Communicative English Skill One"],
        "Natural": ["Physics", "Physical Fitness", "Mathematics for Natural Science", "Communicative English Skill One", "Logic", "Psychology", "Geography", "History"]
    },
    "Adama Science & Technology University (AASTU)": {
        "Engineering": ["Anthropology", "Math", "Entrepreneurship", "Philosophy (Logic)", "Psychology", "Communicative English Skill One", "Geography", "Applied Maths", "Chemistry", "Python", "Civic"]
    },
    "Arba Minch University (AMU)": {
        "Social": ["Mathematics for Social Science", "Communicative English Skill One", "Geography", "Economics", "Psychology", "Logic"],
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "Critical Thinking", "Psychology", "Geography", "Physical Fitness"]
    },
    "Arsi University": {
        "Social": ["Logic", "Geography", "Economics", "Mathematics for Social Science", "Communicative English Skill One", "Psychology"],
        "Natural": ["Mathematics for Natural Science", "Communicative English Skill One", "Psychology", "Logic", "History", "Geography", "Physical Fitness", "General Physics"]
    },
    "Assosa University": {
        "Natural": ["Communicative English Skill One", "Economics", "Mathematics for Natural Science", "Emerging Technology", "Logic & Critical Thinking", "Physics"]
    },
    "Bahir Dar University (BDU)": {
        "Social": ["Anthropology", "Entrepreneurship", "Emerging Technologies", "Communicative English Skill One", "Economics", "Global Trends", "History"],
        "Natural": ["Mathematics for Natural Science", "General Physics", "Psychology", "Civics/Moral Education", "Communicative English Skill One", "Logic", "Geography", "Physical Fitness"]
    },
    "Bonga University": {
        "Social": ["Logic", "Anthropology", "Geography", "Economics", "Mathematics for Social Science", "Communicative English Skill One"]
    },
    "Borana University": {
        "Natural": ["Physics", "Geography", "Logic", "Communicative English Skill One", "Mathematics for Natural Science", "Psychology", "Physical Fitness"]
    },
    "Debre Berhan University": {
        "Social": ["Communicative English Skill One", "Economics", "Emerging Technology", "Logic", "Psychology", "Physical Education", "History"],
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "Psychology", "Social Anthropology", "Logic", "Geography"]
    },
    "Debre Markos University": {
        "Social": ["Communicative English Skill One", "Logic", "Global Trends", "History", "Geography", "Economics", "Inclusiveness"],
        "Natural": ["Physics", "Anthropology", "Psychology", "Civics", "Emerging Technology", "Mathematics for Natural Science", "Communicative English Skill One"]
    },
    "Debre Tabor University (DTU)": {
        "Social": ["Anthropology", "Mathematics for Social Science", "Geography", "History", "Logic", "Communicative English Skill One", "Economics"],
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "Physics", "Logic", "Psychology", "Geography", "Inclusiveness"]
    },
    "Dilla University (Green Land)": {
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "General Psychology", "Logic", "Geography"]
    },
    "Dire Dawa University": {
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "General Psychology", "Logic", "Geography"]
    },
    "Ethiopian Civil Service University (ECSU)": {
        "Social": ["Communicative English Skill One", "Mathematics for Social Science", "Logic", "Anthropology", "Geography", "Economics", "History"]
    },
    "Gondar University": {
        "Social": ["Communicative English Skill One", "Economics", "History", "Logic & Critical Thinking", "General Psychology", "Inclusiveness", "Entrepreneurship"],
        "Natural": ["Anthropology", "Emerging Technology", "Mathematics for Natural Science", "General Physics", "Global Trends", "Moral & Civic Education", "Geography", "Communicative English Skill One"]
    },
    "Haramaya University": {
        "Natural": ["Mathematics for Natural Science", "Physics", "Logic", "Psychology", "Geography", "Communicative English Skill One"]
    },
    "Hawassa University": {
        "Social": ["Economics", "Emerging Technology", "Psychology", "Logic", "Geography", "Communicative English Skill One"],
        "Natural": ["General Physics", "Mathematics for Natural Science", "Logic", "Social Anthropology", "Emerging Technology", "Communicative English Skill One", "Physical Fitness"]
    },
    "Injibara University": {
        "Natural": ["Mathematics for Natural Science", "Communicative English Skill One", "General Physics", "General Psychology", "Logic", "Geography", "Sport"]
    },
    "Jigjiga University": {
        "Social": ["Geography", "Economics", "Logic", "Psychology", "Communicative English Skill One", "Mathematics for Social Science", "Physical Fitness"]
    },
    "Jimma University": {
        "Social": ["Logic", "Psychology", "Communicative English Skill One", "Mathematics for Social Science", "Economics", "Geography", "Physical Fitness"],
        "Natural": ["Logic", "Psychology", "Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "Geography", "Sport/Physical Fitness"]
    },
    "Madda Walabu University": {
        "Social": ["Mathematics for Social Science", "Psychology", "Logic", "Geography", "Communicative English Skill One", "Economics", "HPE"],
        "Natural": ["Mathematics for Natural Science", "General Physics", "Psychology", "Logic", "Geography", "Communicative English Skill One", "HPE"]
    },
    "Mekelle University": {
        "Social": ["Emerging Technology", "History", "Economics", "Psychology", "Entrepreneurship", "Communicative English Skill One", "Physical Education"],
        "Natural": ["Mathematics for Natural Science", "Physics", "Logic", "Geography"]
    },
    "Mizan-Tepi University": {
        "Natural": ["Mathematics for Natural Science", "Physics", "Communicative English Skill One", "Psychology", "Logic", "Geography", "Physical Fitness"]
    },
    "Raya University": {
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "General Psychology", "Logic", "Geography"]
    },
    "Wachemo University": {
        "Social": ["Logic", "Mathematics for Social Science", "Communicative English Skill One", "Psychology", "Geography", "Economics", "Physical Exercise"],
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "Psychology", "Critical Thinking", "Geography", "Physical Fitness"]
    },
    "Werabe University": {
        "Natural": ["Psychology", "Anthropology", "Global Trends", "Communicative English Skill One", "Mathematics for Natural Science", "Physics", "Logic", "Emerging Technology", "HPE"]
    },
    "Wolaita Sodo University": {
        "Social": ["Logic", "Psychology", "Economics", "Mathematics for Social Science", "Geography", "Communicative English Skill One"],
        "Natural": ["Mathematics for Natural Science", "Communicative English Skill One", "General Physics", "Logic", "Psychology", "History", "Geography"]
    },
    "Woldia University": {
        "Social": ["Anthropology", "Psychology", "Global Trends", "Moral & Civic Education", "Entrepreneurship", "Communicative English Skill One", "History", "Economics"],
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "Emerging Technology", "Moral & Civic Education", "Geography", "Physical Fitness"]
    },
    "Wollega University": {
        "Social": ["Mathematics for Social Science", "Communicative English Skill One", "Psychology", "Logic", "Economics", "Geography", "Physical Fitness"],
        "Natural": ["Mathematics for Natural Science", "Physics", "Communicative English Skill One", "Psychology", "Logic", "Geography"]
    },
    "Wolkite University": {
        "Social": ["Anthropology", "Psychology", "Entrepreneurship", "Logic", "Mathematics for Social Science", "Communicative English Skill One", "Economics"],
        "Natural": ["Communicative English Skill One", "Mathematics for Natural Science", "General Physics", "General Psychology", "Logic", "Geography", "Physical Fitness"]
    },
    "Wollo University": {
        "Social": ["Communicative English Skill One", "Psychology", "Logic", "Economics", "Mathematics for Social Science", "Entrepreneurship", "Physical Fitness"],
        "Natural": ["Communicative English Skill One", "Physics", "Psychology", "Logic", "Geography", "Mathematics for Natural Science", "Physical Fitness"]
    }
}


# In-memory dynamic overrides dictionary for live admin edits
CUSTOM_OVERRIDDEN_COURSES: Dict[str, Dict[str, List[str]]] = {}


def register_custom_university_course(university_name: str, stream_name: str, courses: List[str]):
    """Registers or updates a university stream course list in memory."""
    clean_uni = university_name.strip()
    clean_stream = stream_name.strip()
    if clean_uni not in CUSTOM_OVERRIDDEN_COURSES:
        CUSTOM_OVERRIDDEN_COURSES[clean_uni] = {}
    CUSTOM_OVERRIDDEN_COURSES[clean_uni][clean_stream] = courses


def remove_custom_university(university_name: str):
    """Removes a university from memory overrides."""
    clean_uni = university_name.strip()
    CUSTOM_OVERRIDDEN_COURSES.pop(clean_uni, None)


def load_university_courses() -> Dict[str, Dict[str, List[str]]]:
    """Reads and parses FreshMinds_Academy_Freshman_Course_Guide.md directly and merges custom admin edits."""
    base_data = {}
    if os.path.exists(GUIDE_MD_PATH):
        try:
            with open(GUIDE_MD_PATH, "r", encoding="utf-8") as f:
                text = f.read()

            uni_sections = re.findall(r'### ([^\n]+)\n+\| Stream \| Courses \|\n\|---\|---\|\n((?:\| [^\n]+\n)+)', text)
            for uni_name, table_rows in uni_sections:
                uni_name = uni_name.strip()
                base_data[uni_name] = {}
                for row in table_rows.strip().split("\n"):
                    parts = [p.strip() for p in row.split("|") if p.strip()]
                    if len(parts) >= 2:
                        stream = parts[0]
                        courses = [c.strip() for c in parts[1].split(",") if c.strip()]
                        base_data[uni_name][stream] = courses
        except Exception:
            base_data = dict(UNIVERSITY_COURSES_DB)
    else:
        base_data = dict(UNIVERSITY_COURSES_DB)

    # Merge custom overrides
    for uni, streams in CUSTOM_OVERRIDDEN_COURSES.items():
        if uni not in base_data:
            base_data[uni] = {}
        for st, cl in streams.items():
            base_data[uni][st] = cl

    return base_data



def get_all_university_names() -> List[str]:
    """Returns sorted list of university names."""
    data = load_university_courses()
    return sorted(list(data.keys()))


def _normalize_name(s: str) -> str:
    s = s.lower().replace("university", "").replace("ዩኒቨርሲቲ", "")
    s = s.replace("birhan", "berhan").replace("markos", "marcos").replace("wollega", "welega").replace("sodo", "sdo")
    return re.sub(r'[^a-z0-9]', '', s)


def find_university_courses(query_name: str) -> Optional[tuple[str, Dict[str, List[str]]]]:
    """Finds university courses by exact name, normalized tokens, or substring keyword."""
    data = load_university_courses()
    clean = query_name.strip().lower()
    norm_query = _normalize_name(clean)

    # 1. Exact match
    for name, streams in data.items():
        if name.lower() == clean:
            return name, streams

    # 2. Normalized token match
    for name, streams in data.items():
        norm_name = _normalize_name(name)
        if norm_query and (norm_query == norm_name or norm_query in norm_name or norm_name in norm_query):
            return name, streams

    # 3. Substring / abbreviation match
    for name, streams in data.items():
        if clean in name.lower() or name.lower() in clean:
            return name, streams

    # 4. Keyword token match
    keyword = clean.replace("university", "").replace("ዩኒቨርሲቲ", "").strip()
    if keyword:
        for name, streams in data.items():
            if keyword in name.lower():
                return name, streams

    return None


