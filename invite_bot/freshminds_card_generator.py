"""
FreshMinds Graphic Card Generator — Unified HD Watermarked Card Engine
Generates HD watermarked image cards with FreshMinds Academy background branding for:
1. Placement Result Cards
2. University 1st Semester Course Guide Cards
3. GPA Calculation Report Cards
4. Referral & Leaderboard Stats Cards
"""

import os
from PIL import Image, ImageDraw, ImageFont


def _draw_watermark_background(width: int, height: int) -> Image.Image:
    """Creates a base 1080px dark navy gradient image with semi-transparent diagonal watermarks."""
    img = Image.new("RGBA", (width, height), (13, 27, 42, 255))

    # Watermark layer
    wm_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(wm_layer)

    try:
        wm_font = ImageFont.truetype("arialbd.ttf", 64)
    except Exception:
        wm_font = ImageFont.load_default()

    # Repeat diagonal watermark text "FRESHMINDS ACADEMY" across background
    for y in range(-200, height + 400, 180):
        for x in range(-300, width + 500, 600):
            wm_draw.text((x, y), "FRESHMINDS ACADEMY", font=wm_font, fill=(255, 255, 255, 18))

    # Large Center Transparent Watermark Logo
    center_y = (height // 2) - 100
    wm_draw.text((80, center_y), "FRESHMINDS", font=wm_font, fill=(56, 189, 248, 25))
    wm_draw.text((220, center_y + 80), "ACADEMY", font=wm_font, fill=(56, 189, 248, 25))

    img = Image.alpha_composite(img, wm_layer)
    draw = ImageDraw.Draw(img)

    # Decorative Border Frame
    draw.rectangle([(30, 30), (width - 30, height - 30)], outline=(56, 189, 248, 120), width=4)
    draw.rectangle([(42, 42), (width - 42, height - 42)], outline=(251, 191, 36, 100), width=2)

    return img


def generate_placement_card_image(
    student_name: str,
    reg_number: str,
    university: str,
    stream: str,
    score: str = "N/A",
    school: str = "N/A",
    region: str = "N/A",
    output_filename: str = "placement_result.png",
) -> str:
    """Generates a 1080x1350 HD result card image with FreshMinds Academy background watermark."""
    width, height = 1080, 1350
    img = _draw_watermark_background(width, height)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 44)
        subtitle_font = ImageFont.truetype("arialbd.ttf", 52)
        name_font = ImageFont.truetype("arialbd.ttf", 46)
        label_font = ImageFont.truetype("arial.ttf", 34)
        value_font = ImageFont.truetype("arialbd.ttf", 38)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Header Box
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(56, 189, 248, 150), width=2)
    draw.text((90, 95), "ETHIOPIAN MINISTRY OF EDUCATION", font=title_font, fill=(148, 163, 184))
    draw.text((90, 150), "UNIVERSITY PLACEMENT RESULT", font=subtitle_font, fill=(251, 191, 36))

    # Main Content Box
    box_top, box_bottom = 270, 1140
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)

    curr_y = box_top + 45
    fields = [
        ("STUDENT NAME", student_name.upper(), (248, 250, 252)),
        ("ADMISSION / REG NO", reg_number, (56, 189, 248)),
        ("ASSIGNED UNIVERSITY", university.upper(), (251, 191, 36)),
        ("ASSIGNED FIELD / STREAM", stream.upper(), (248, 250, 252)),
    ]

    if score and score != "N/A":
        fields.append(("EXAM TOTAL SCORE", score, (56, 189, 248)))
    if school and school != "N/A":
        fields.append(("SCHOOL NAME", school, (226, 232, 240)))
    if region and region != "N/A":
        fields.append(("REGION", region, (226, 232, 240)))

    for label, val, color in fields:
        draw.text((110, curr_y), label, font=label_font, fill=(148, 163, 184))
        curr_y += 42
        draw.text((110, curr_y), val, font=name_font if label == "STUDENT NAME" else value_font, fill=color)
        curr_y += 62
        draw.line([(110, curr_y), (width - 110, curr_y)], fill=(51, 65, 85, 180), width=2)
        curr_y += 30

    # Footer Watermark Banner
    draw.rectangle([(70, 1170), (width - 70, 1280)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1192), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1234), "Join Telegram Channel for 1st Year Modules & Video Lessons", font=label_font, fill=(248, 250, 252))

    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


def generate_university_course_card_image(
    university_name: str,
    streams_dict: dict,
    output_filename: str = "uni_courses_card.png",
) -> str:
    """Generates a 1080x1400 HD University 1st Semester Course Guide graphic with FreshMinds watermark."""
    width, height = 1080, 1400
    img = _draw_watermark_background(width, height)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 46)
        sub_font = ImageFont.truetype("arial.ttf", 36)
        stream_font = ImageFont.truetype("arialbd.ttf", 40)
        course_font = ImageFont.truetype("arial.ttf", 32)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        stream_font = ImageFont.load_default()
        course_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Header Box
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(251, 191, 36, 180), width=3)
    draw.text((90, 95), university_name.upper(), font=title_font, fill=(251, 191, 36))
    draw.text((90, 158), "1ST SEMESTER FRESHMAN COURSE GUIDE", font=sub_font, fill=(56, 189, 248))

    # Main Content Box
    box_top, box_bottom = 260, 1200
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)

    curr_y = box_top + 40
    for stream_name, courses in streams_dict.items():
        draw.text((110, curr_y), f"● {stream_name.upper()} STREAM COURSES:", font=stream_font, fill=(56, 189, 248))
        curr_y += 50
        for c in courses[:8]:  # show up to 8 courses per stream
            draw.text((130, curr_y), f"•  {c}", font=course_font, fill=(248, 250, 252))
            curr_y += 42
        curr_y += 20
        draw.line([(110, curr_y), (width - 110, curr_y)], fill=(51, 65, 85, 180), width=2)
        curr_y += 30

    # Footer Watermark Banner
    draw.rectangle([(70, 1230), (width - 70, 1340)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1250), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1292), "Join Telegram for 1st Year Modules & Video Explanations", font=sub_font, fill=(248, 250, 252))

    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


def generate_gpa_report_card_image(
    gpa: float,
    total_ch: int,
    total_pts: float,
    breakdown: list,
    output_filename: str = "gpa_report.png",
) -> str:
    """Generates a 1080x1350 HD GPA Calculation Report graphic with FreshMinds watermark."""
    width, height = 1080, 1350
    img = _draw_watermark_background(width, height)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 46)
        sub_font = ImageFont.truetype("arial.ttf", 36)
        gpa_font = ImageFont.truetype("arialbd.ttf", 72)
        item_font = ImageFont.truetype("arial.ttf", 34)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        gpa_font = ImageFont.load_default()
        item_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Header Box
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(56, 189, 248, 180), width=3)
    draw.text((90, 95), "FRESHMINDS GPA CALCULATOR", font=title_font, fill=(248, 250, 252))
    draw.text((90, 158), "OFFICIAL SEMESTER REPORT CARD", font=sub_font, fill=(56, 189, 248))

    # Main GPA Display Box
    draw.rectangle([(70, 260), (width - 70, 460)], fill=(15, 23, 42, 240), outline=(251, 191, 36, 200), width=3)
    draw.text((110, 290), "CALCULATED SEMESTER GPA", font=sub_font, fill=(148, 163, 184))
    draw.text((110, 345), f"{gpa:.2f} / 4.00", font=gpa_font, fill=(251, 191, 36))
    draw.text((600, 365), f"Total Cr.Hr: {total_ch}  |  Points: {total_pts:.1f}", font=sub_font, fill=(56, 189, 248))

    # Courses Breakdown Box
    box_top, box_bottom = 490, 1150
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)
    draw.text((110, box_top + 30), "COURSES GRADE BREAKDOWN:", font=sub_font, fill=(56, 189, 248))

    curr_y = box_top + 85
    for item in breakdown[:9]:
        cname = item.get("name", f"Course {item.get('num')}")
        ch = item.get("ch", 0)
        grade = item.get("grade", "N/A")
        pts = item.get("pts", 0.0)
        draw.text((130, curr_y), f"• {cname[:28]} ({ch} Cr.Hr) ➜ Grade: {grade} ({pts:.1f} pts)", font=item_font, fill=(248, 250, 252))
        curr_y += 50

    # Footer Watermark Banner
    draw.rectangle([(70, 1180), (width - 70, 1290)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1202), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1244), "Join Telegram Channel for Freshman Courses & Mobile App", font=sub_font, fill=(248, 250, 252))

    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


def generate_stats_card_image(
    first_name: str,
    active_points: int,
    total_joins: int,
    rank: int | str,
    output_filename: str = "stats_card.png",
) -> str:
    """Generates a 1080x1350 HD Personal Competition Stats card with FreshMinds watermark."""
    width, height = 1080, 1350
    img = _draw_watermark_background(width, height)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 46)
        sub_font = ImageFont.truetype("arial.ttf", 36)
        name_font = ImageFont.truetype("arialbd.ttf", 44)
        stat_lbl_font = ImageFont.truetype("arial.ttf", 34)
        stat_val_font = ImageFont.truetype("arialbd.ttf", 48)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        stat_lbl_font = ImageFont.load_default()
        stat_val_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Header Box
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(56, 189, 248, 180), width=3)
    draw.text((90, 95), "FRESHMINDS INVITE COMPETITION", font=title_font, fill=(251, 191, 36))
    draw.text((90, 158), f"PERSONAL PERFORMANCE CARD — {first_name.upper()}", font=sub_font, fill=(248, 250, 252))

    # Main Stats Display Box
    box_top, box_bottom = 260, 1150
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)

    curr_y = box_top + 50
    rank_str = f"#{rank}" if isinstance(rank, int) else str(rank)
    stats_data = [
        ("🏆 YOUR CURRENT LEADERBOARD RANK", rank_str, (251, 191, 36)),
        ("🔥 TOTAL ACTIVE COMPETITION POINTS", f"{active_points} PTS", (56, 189, 248)),
        ("👥 TOTAL SUCCESSFUL REFERRED FRIENDS", f"{total_joins} USERS", (74, 222, 128)),
    ]

    for lbl, val, color in stats_data:
        draw.text((110, curr_y), lbl, font=stat_lbl_font, fill=(148, 163, 184))
        curr_y += 45
        draw.text((110, curr_y), val, font=stat_val_font, fill=color)
        curr_y += 75
        draw.line([(110, curr_y), (width - 110, curr_y)], fill=(51, 65, 85, 180), width=2)
        curr_y += 35

    # Motivational Tip Box inside Main
    draw.rectangle([(110, curr_y + 10), (width - 110, box_bottom - 40)], fill=(30, 41, 59, 200), outline=(251, 191, 36, 120), width=2)
    draw.text((130, curr_y + 35), "💡 PRO TIP: Share your referral link with school groups", font=stat_lbl_font, fill=(251, 191, 36))
    draw.text((130, curr_y + 80), "and classmates to boost your ranking and win top prizes!", font=stat_lbl_font, fill=(248, 250, 252))

    # Footer Watermark Banner
    draw.rectangle([(70, 1180), (width - 70, 1290)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1202), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1244), "Join Telegram Channel for Freshman Courses & Mobile App", font=sub_font, fill=(248, 250, 252))

    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


def generate_leaderboard_card_image(
    comp_title: str,
    top_users: list,
    my_rank: int | str,
    my_points: int,
    output_filename: str = "leaderboard_card.png",
) -> str:
    """Generates a 1080x1400 HD Top Referrers Leaderboard graphic with FreshMinds watermark."""
    width, height = 1080, 1400
    img = _draw_watermark_background(width, height)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 46)
        sub_font = ImageFont.truetype("arial.ttf", 36)
        row_font = ImageFont.truetype("arialbd.ttf", 36)
        item_font = ImageFont.truetype("arial.ttf", 32)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        row_font = ImageFont.load_default()
        item_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Header Box
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(251, 191, 36, 180), width=3)
    draw.text((90, 95), "🏆 LEADERBOARD RANKINGS", font=title_font, fill=(251, 191, 36))
    draw.text((90, 158), comp_title.upper() if comp_title else "FRESHMINDS INVITE COMPETITION", font=sub_font, fill=(56, 189, 248))

    # Main Board Box
    box_top, box_bottom = 260, 1200
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)

    curr_y = box_top + 35
    draw.text((110, curr_y), "🥇 TOP REFERRERS BOARD:", font=row_font, fill=(251, 191, 36))
    curr_y += 55

    badges = ["🥇", "🥈", "🥉", "4️⃣"]
    for idx, u in enumerate(top_users[:4]):
        b = badges[idx] if idx < len(badges) else f"{idx+1}."
        fname = u.get("first_name", "Anonymous")
        pts = u.get("points", 0)
        draw.text((130, curr_y), f"{b} {fname[:20]}", font=row_font, fill=(248, 250, 252))
        draw.text((700, curr_y), f"{pts} PTS", font=row_font, fill=(56, 189, 248))
        curr_y += 50
        draw.line([(110, curr_y), (width - 110, curr_y)], fill=(51, 65, 85, 180), width=2)
        curr_y += 25

    # Personal Rank Section
    rank_str = f"#{my_rank}" if isinstance(my_rank, int) else str(my_rank)
    draw.rectangle([(110, curr_y + 10), (width - 110, box_bottom - 30)], fill=(30, 41, 59, 220), outline=(56, 189, 248, 150), width=2)
    draw.text((130, curr_y + 35), f"👤 YOUR CURRENT POSITION: {rank_str}", font=row_font, fill=(251, 191, 36))
    draw.text((130, curr_y + 85), f"⭐ YOUR TOTAL POINTS: {my_points} PTS", font=item_font, fill=(248, 250, 252))

    # Footer Watermark Banner
    draw.rectangle([(70, 1230), (width - 70, 1340)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1250), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1292), "Join Telegram Channel for 1st Year Modules & Video Explanations", font=sub_font, fill=(248, 250, 252))

    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


def generate_invite_card_image(
    first_name: str,
    invite_link: str,
    output_filename: str = "invite_card.png",
) -> str:
    """Generates a 1080x1350 HD Referral & Earn Promo graphic with FreshMinds watermark."""
    width, height = 1080, 1350
    img = _draw_watermark_background(width, height)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 46)
        sub_font = ImageFont.truetype("arial.ttf", 36)
        name_font = ImageFont.truetype("arialbd.ttf", 44)
        lbl_font = ImageFont.truetype("arial.ttf", 34)
        link_font = ImageFont.truetype("arialbd.ttf", 34)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        lbl_font = ImageFont.load_default()
        link_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Header Box
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(56, 189, 248, 180), width=3)
    draw.text((90, 95), "FRESHMINDS REFER & WIN", font=title_font, fill=(251, 191, 36))
    draw.text((90, 158), f"OFFICIAL REFERRAL CARD — {first_name.upper()}", font=sub_font, fill=(248, 250, 252))

    # Main Card Box
    box_top, box_bottom = 260, 1150
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)

    curr_y = box_top + 45
    draw.text((110, curr_y), "🚀 YOUR EXCLUSIVE REFERRAL LINK:", font=lbl_font, fill=(148, 163, 184))
    curr_y += 45
    draw.rectangle([(110, curr_y), (width - 110, curr_y + 80)], fill=(30, 41, 59, 240), outline=(56, 189, 248, 200), width=2)
    draw.text((130, curr_y + 20), invite_link, font=link_font, fill=(56, 189, 248))
    curr_y += 120

    benefits = [
        "🎁 1. Invite 1st year freshman students to earn competition points.",
        "📚 2. Unlock free university modules, exam models & tutorials.",
        "📱 3. Get early VIP beta access to FreshMinds Freshman App!",
    ]
    draw.text((110, curr_y), "🌟 WHY SHARE THIS BOT?", font=name_font, fill=(251, 191, 36))
    curr_y += 55
    for b in benefits:
        draw.text((120, curr_y), b, font=lbl_font, fill=(248, 250, 252))
        curr_y += 50

    # Footer Watermark Banner
    draw.rectangle([(70, 1180), (width - 70, 1290)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1202), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1244), "Join Telegram Channel for Freshman Courses & Mobile App", font=sub_font, fill=(248, 250, 252))

    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


def generate_resources_card_image(
    course_name: str = "FRESHMAN RESOURCES",
    output_filename: str = "resources_card.png",
) -> str:
    """Generates a 1080x1350 HD Freshman Resources graphic with FreshMinds watermark."""
    width, height = 1080, 1350
    img = _draw_watermark_background(width, height)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 46)
        sub_font = ImageFont.truetype("arial.ttf", 36)
        header_font = ImageFont.truetype("arialbd.ttf", 42)
        lbl_font = ImageFont.truetype("arial.ttf", 34)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        lbl_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Header Box
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(251, 191, 36, 180), width=3)
    draw.text((90, 95), "FRESHMINDS COURSE RESOURCE HUB", font=title_font, fill=(251, 191, 36))
    draw.text((90, 158), course_name.upper(), font=sub_font, fill=(56, 189, 248))

    # Main Card Box
    box_top, box_bottom = 260, 1150
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)

    curr_y = box_top + 50
    items = [
        ("📖 OFFICIAL MODULES", "Ministry of Education 1st semester modules in clean PDF"),
        ("📝 SUMMARY HANDOUTS", "Concise chapter summaries & key concept notes"),
        ("📑 EXAM BANKS", "Midterm & Final past university exam models with answers"),
        ("🎥 VIDEO TUTORIALS", "Step-by-step video lesson explanations & drive links"),
    ]

    for title, desc in items:
        draw.text((110, curr_y), title, font=header_font, fill=(56, 189, 248))
        curr_y += 45
        draw.text((110, curr_y), desc, font=lbl_font, fill=(248, 250, 252))
        curr_y += 65
        draw.line([(110, curr_y), (width - 110, curr_y)], fill=(51, 65, 85, 180), width=2)
        curr_y += 35

    # Footer Watermark Banner
    draw.rectangle([(70, 1180), (width - 70, 1290)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1202), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1244), "Join Telegram Channel for Freshman Courses & Mobile App", font=sub_font, fill=(248, 250, 252))

    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


