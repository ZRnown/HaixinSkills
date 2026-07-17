"""
备选方案：PIL 叠加叙事旁白文字（仅当 AI 生图无法正确产出文字时使用）。
simkai 楷体 + 半透明白底条 + 深灰文字，底部居中。

用户偏好：AI 生图直接带文字。此方案已被否定，仅保留作紧急回退。
"""
from PIL import Image, ImageDraw, ImageFont
import os

# ============================================================
# CONFIG — adjust per project
# ============================================================
WORKSPACE = r"E:\Users\admin\Desktop\王海鑫\Tutorial"
SRC_DIR = os.path.join(WORKSPACE, "FIXME_source_image_dir")
OUTPUT_DIR = os.path.join(WORKSPACE, "FIXME_output_dir")
FONT_PATH = r"C:\Windows\Fonts\simkai.ttf"

pages = [
    ("FIXME_01.jpeg", "第1句叙事旁白"),
    ("FIXME_02.jpeg", "第2句叙事旁白"),
    # ... fill in all 10 lines
]


def wrap_text(text, font, draw, max_width):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)
    return lines


os.makedirs(OUTPUT_DIR, exist_ok=True)

for i, (filename, text) in enumerate(pages, 1):
    src = os.path.join(SRC_DIR, filename)
    if not os.path.exists(src):
        print(f"[SKIP] {filename}")
        continue

    img = Image.open(src).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    font_size = max(30, int(h * 0.048))
    font = ImageFont.truetype(FONT_PATH, font_size)

    side_margin = int(w * 0.06)
    max_text_width = w - side_margin * 2
    lines = wrap_text(text, font, draw, max_text_width)

    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    line_spacing = int(font_size * 0.3)
    total_h = sum(line_heights) + line_spacing * (len(lines) - 1)

    margin_bottom = int(h * 0.08)
    padding = int(font_size * 0.7)
    y_start = h - margin_bottom - total_h - padding

    overlay = Image.new("RGBA", (w, total_h + padding * 2), (255, 255, 255, 200))
    img_rgba = img.convert("RGBA")
    img_rgba.paste(overlay, (0, y_start - padding), overlay)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    y = y_start
    for j, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        draw.text((x, y), line, font=font, fill=(40, 40, 40))
        y += line_heights[j] + line_spacing

    out_path = os.path.join(OUTPUT_DIR, f"{i:02d}_{filename}")
    img.save(out_path, quality=95)
    print(f"[OK] {i:02d}_{filename} ({len(lines)} lines)")

print("\nDone!", OUTPUT_DIR)
