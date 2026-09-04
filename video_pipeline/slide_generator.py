import os
from PIL import Image, ImageDraw, ImageFont
from lesson_parser import clean_lesson

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

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"[+] Slide generated: {output_path}")

if __name__ == "__main__":
    lessons = clean_lesson()
    concept = lessons[0]["concept"]
    codes = lessons[0]["codes"]

    if not codes:
        codes = ["# Overview\n# No code block present for this segment."]

    for idx, snippet in enumerate(codes, start=1):
        out_file = f"output/slide_{idx:02d}.png"
        create_code_slide(concept, snippet, idx, out_file)