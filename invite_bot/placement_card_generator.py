"""
FreshMinds Placement Card Generator — Dynamic Watermarked Image Card Builder
Generates a high-resolution branded placement result graphic with semi-transparent FreshMinds Academy background watermarks.
"""

import os
from PIL import Image, ImageDraw, ImageFont


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
    """
    Generates a 1080x1350 HD result card image with FreshMinds Academy background watermark.
    Returns absolute path to the generated image.
    """
    width, height = 1080, 1350

    # Create base dark navy gradient image
    img = Image.new("RGBA", (width, height), (13, 27, 42, 255))
    draw = ImageDraw.Draw(img)

    # 1. Draw Diagonal Background Watermark Grid
    watermark_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(watermark_layer)

    # Load default fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 44)
        subtitle_font = ImageFont.truetype("arialbd.ttf", 52)
        name_font = ImageFont.truetype("arialbd.ttf", 46)
        label_font = ImageFont.truetype("arial.ttf", 34)
        value_font = ImageFont.truetype("arialbd.ttf", 38)
        wm_font = ImageFont.truetype("arialbd.ttf", 64)
        footer_font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        wm_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Repeat diagonal watermark text "FRESHMINDS ACADEMY" across background
    wm_text = "FRESHMINDS ACADEMY  •  FRESHMINDS ACADEMY  •  "
    for y in range(-200, height + 400, 180):
        for x in range(-300, width + 500, 600):
            wm_draw.text((x, y), "FRESHMINDS ACADEMY", font=wm_font, fill=(255, 255, 255, 18))

    # Large Center Transparent Watermark Logo
    wm_draw.text((80, 580), "FRESHMINDS", font=wm_font, fill=(56, 189, 248, 25))
    wm_draw.text((220, 660), "ACADEMY", font=wm_font, fill=(56, 189, 248, 25))

    # Composite watermark onto base
    img = Image.alpha_composite(img, watermark_layer)
    draw = ImageDraw.Draw(img)

    # 2. Outer Decorative Border Frame
    draw.rectangle([(30, 30), (width - 30, height - 30)], outline=(56, 189, 248, 120), width=4)
    draw.rectangle([(42, 42), (width - 42, height - 42)], outline=(251, 191, 36, 100), width=2)

    # 3. Header Card Header
    draw.rectangle([(70, 70), (width - 70, 230)], fill=(30, 41, 59, 240), outline=(56, 189, 248, 150), width=2)
    draw.text((90, 95), "ETHIOPIAN MINISTRY OF EDUCATION", font=title_font, fill=(148, 163, 184))
    draw.text((90, 150), "UNIVERSITY PLACEMENT RESULT", font=subtitle_font, fill=(251, 191, 36))

    # 4. Main Information Container Box
    box_top, box_bottom = 270, 1140
    draw.rectangle([(70, box_top), (width - 70, box_bottom)], fill=(15, 23, 42, 230), outline=(56, 189, 248, 180), width=3)

    # Draw Fields Inside Box
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
        # Draw Label
        draw.text((110, curr_y), label, font=label_font, fill=(148, 163, 184))
        curr_y += 42
        # Draw Value
        draw.text((110, curr_y), val, font=name_font if label == "STUDENT NAME" else value_font, fill=color)
        curr_y += 62
        # Horizontal Separator line
        draw.line([(110, curr_y), (width - 110, curr_y)], fill=(51, 65, 85, 180), width=2)
        curr_y += 30

    # 5. Footer Marketing Watermark Banner
    draw.rectangle([(70, 1170), (width - 70, 1280)], fill=(30, 41, 59, 250), outline=(251, 191, 36, 200), width=3)
    draw.text((100, 1192), "🎓 FRESHMINDS ACADEMY — @FreshMinds_Academy", font=footer_font, fill=(251, 191, 36))
    draw.text((100, 1234), "Join Telegram Channel for 1st Year Modules & Video Lessons", font=label_font, fill=(248, 250, 252))

    # Save Image
    out_dir = os.path.dirname(output_filename)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img.save(output_filename, "PNG")
    return os.path.abspath(output_filename)


if __name__ == "__main__":
    out_path = generate_placement_card_image(
        student_name="RUTH DESSALE YEHUALAW",
        reg_number="00176600",
        university="DEBREBIRHAN UNIVERSITY (DBU)",
        stream="Natural Science",
        score="347",
        school="Sample High School",
        region="Amhara",
        output_filename="test_watermark_card.png",
    )
    print("Generated watermark placement card image at:", out_path)

