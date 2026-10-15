"""
Generate 1000x420 High-Res Banner for PrintPulse using Pillow
"""

import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 420
img = Image.new("RGBA", (W, H), (9, 13, 22, 255))
draw = ImageDraw.Draw(img)

# 1. Dark Gradient Background
for y in range(H):
    ratio = y / H
    r = int(9 + 20 * (1 - ratio) + 5 * ratio)
    g = int(13 + 12 * (1 - ratio) + 2 * ratio)
    b = int(22 + 45 * (1 - ratio) + 12 * ratio)
    draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

# Radial glow near top right
glow_x, glow_y = 750, 140
for radius in range(280, 0, -4):
    alpha = int(25 * (1.0 - radius / 280.0))
    glow_color = (59, 130, 246, alpha)
    draw.ellipse([glow_x - radius, glow_y - radius, glow_x + radius, glow_y + radius], fill=glow_color)

# 2. Tech Grid Lines
grid_step = 32
for x in range(0, W, grid_step):
    draw.line([(x, 0), (x, H)], fill=(59, 130, 246, 18), width=1)
for y in range(0, H, grid_step):
    draw.line([(0, y), (W, y)], fill=(59, 130, 246, 18), width=1)

# Fonts
try:
    font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    font_pill = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    font_stat_val = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    font_stat_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    font_stat_desc = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    font_badge = font_title = font_sub = font_pill = font_stat_val = font_stat_lbl = font_stat_desc = ImageFont.load_default()

# 3. Top Badge
badge_text = "● HACKTOBERFEST 2026 // SIDE HUSTLE CHALLENGE"
draw.rounded_rectangle([56, 44, 460, 74], radius=15, fill=(30, 58, 138, 160), outline=(96, 165, 250, 180), width=1)
draw.text((72, 51), badge_text, fill=(147, 197, 253, 255), font=font_badge)

# 4. Main Title
title = "PrintPulse"
draw.text((56, 92), title, fill=(255, 255, 255, 255), font=font_title)

# 5. Subtitle
sub1 = "Autonomous 3D Print Farm Scrap Risk Predictor & Quoting Agent"
sub2 = "Deterministic geometry parsing + TabPFN-3.5 Bayesian priors + DigitalOcean Gemma-4-31B"
draw.text((56, 156), sub1, fill=(203, 213, 225, 255), font=font_sub)
draw.text((56, 184), sub2, fill=(148, 163, 184, 255), font=font_sub)

# 6. Tech Pills
pills = [
    ("DigitalOcean Serverless (Gemma 4 31B)", (2, 132, 199), (56, 189, 248)),
    ("Prior Labs TabPFN-3.5", (139, 92, 246), (192, 132, 252)),
    ("Temporal Workflows", (16, 185, 129), (52, 211, 153))
]

px = 56
py = 336
for text, border_color, text_color in pills:
    pill_w = len(text) * 8 + 32
    draw.rounded_rectangle([px, py, px + pill_w, py + 36], radius=8, fill=(17, 24, 39, 230), outline=border_color, width=1)
    draw.text((px + 14, py + 10), text, fill=text_color, font=font_pill)
    px += pill_w + 14

# 7. Stat Card on the right
card_x0, card_y0 = 670, 140
card_x1, card_y1 = 944, 372
draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=14, fill=(17, 24, 39, 230), outline=(59, 130, 246, 120), width=1)

draw.text((card_x0 + 20, card_y0 + 20), "PRIOR LABS TABPFN-3.5", fill=(100, 116, 139, 255), font=font_stat_lbl)
draw.text((card_x0 + 20, card_y0 + 40), "0.0075 ms", fill=(56, 189, 248, 255), font=font_stat_val)
draw.text((card_x0 + 20, card_y0 + 78), "Zero-Shot Bayesian Prior", fill=(148, 163, 184, 255), font=font_stat_desc)

draw.line([(card_x0 + 20, card_y0 + 106), (card_x1 - 20, card_y0 + 106)], fill=(31, 41, 55, 255), width=1)

draw.text((card_x0 + 20, card_y0 + 120), "DO SERVERLESS INFERENCE", fill=(100, 116, 139, 255), font=font_stat_lbl)
draw.text((card_x0 + 20, card_y0 + 140), "8.8s / $0 Idle", fill=(192, 132, 252, 255), font=font_stat_val)
draw.text((card_x0 + 20, card_y0 + 178), "Gemma-4-31B-it on demand", fill=(148, 163, 184, 255), font=font_stat_desc)

img.convert("RGB").save("/root/printpulse/assets/cover.png", "PNG")
print("Successfully generated /root/printpulse/assets/cover.png (1000x420)")
