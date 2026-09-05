import os
from PIL import Image, ImageDraw, ImageFont
from lesson_parser import clean_lesson

def create_concept_slide(concept_title: str, explanation: str, slide_num: int, output_path: str, key_points: list = None):
    width, height = 1920, 1080
    bg_color = (15, 23, 42)        # Slate 900
    card_bg = (30, 41, 59)         # Slate 800
    accent_blue = (56, 189, 248)   # Sky 400
    accent_purple = (168, 85, 247) # Purple 500
    text_color = (241, 245, 249)   # Slate 100
    subtext_color = (203, 213, 225) # Slate 300
    border_color = (51, 65, 85)

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Header Card
    draw.rectangle([(80, 60), (1840, 160)], fill=card_bg, outline=border_color, width=2)
    header_text = f"BHARAT ACADEMIX  |  CONCEPT {slide_num}: {concept_title.upper()}"
    draw.text((120, 100), header_text, fill=accent_blue, font=font)

    # Main Body Card
    draw.rectangle([(80, 190), (1840, 990)], fill=card_bg, outline=border_color, width=2)

    # Decorative dots
    draw.ellipse([(120, 220), (136, 236)], fill=(239, 68, 68))
    draw.ellipse([(146, 220), (162, 236)], fill=(245, 158, 11))
    draw.ellipse([(172, 220), (188, 236)], fill=(34, 197, 94))

    # Explanation text wrapping
    words = explanation.split()
    lines = []
    curr = ""
    for w in words:
        if len(curr) + len(w) + 1 <= 85:
            curr += (" " if curr else "") + w
        else:
            lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)

    draw.text((120, 280), "CORE EXPLANATION:", fill=accent_purple, font=font)
    y_start = 320
    for line in lines[:10]:
        draw.text((120, y_start), line, fill=text_color, font=font)
        y_start += 32

    # Key takeaways / points
    if key_points:
        y_start += 30
        draw.text((120, y_start), "KEY TAKEAWAYS:", fill=accent_blue, font=font)
        y_start += 35
        for pt in key_points[:4]:
            draw.text((140, y_start), f"• {pt}", fill=subtext_color, font=font)
            y_start += 30

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path)
    print(f"[+] Concept slide generated: {output_path}")
    return output_path

def create_code_slide(concept_title: str, code_snippet: str, slide_num: int, output_path: str):
    width, height = 1920, 1080
    bg_color = (20, 24, 33)       # Dark slate blue background
    card_bg = (30, 36, 48)        # Elevated card container
    accent_blue = (61, 142, 248)  # Header accent
    text_color = (230, 237, 243)  # Code foreground
    border_color = (48, 54, 66)

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle([(100, 80), (1820, 160)], fill=card_bg, outline=border_color, width=2)
    header_text = f"TOPIC: {concept_title.upper()} | SLIDE {slide_num}"
    draw.text((130, 110), header_text, fill=accent_blue, font=font)

    draw.rectangle([(100, 200), (1820, 980)], fill=card_bg, outline=border_color, width=2)
    
    draw.ellipse([(130, 230), (146, 246)], fill=(255, 95, 86))   # Red
    draw.ellipse([(156, 230), (172, 246)], fill=(255, 189, 46))  # Yellow
    draw.ellipse([(182, 230), (198, 246)], fill=(39, 201, 63))   # Green

    y_start = 280
    for line in code_snippet.split("\n"):
        draw.text((140, y_start), line, fill=text_color, font=font)
        y_start += 28

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path)
    print(f"[+] Code slide generated: {output_path}")
    return output_path

if __name__ == "__main__":
    lessons = clean_lesson()
    concept = lessons[0]["concept"]
    codes = lessons[0]["codes"]

    if not codes:
        create_concept_slide(concept, lessons[0]["speech"], 1, "output/slide_01.png")
    else:
        for idx, snippet in enumerate(codes, start=1):
            out_file = f"output/slide_{idx:02d}.png"
            create_code_slide(concept, snippet, idx, out_file)