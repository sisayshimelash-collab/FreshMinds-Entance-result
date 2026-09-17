from freshminds_card_generator import (
    generate_placement_card_image,
    generate_university_course_card_image,
    generate_gpa_report_card_image,
    generate_stats_card_image,
    generate_leaderboard_card_image,
    generate_invite_card_image,
    generate_resources_card_image,
)

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


