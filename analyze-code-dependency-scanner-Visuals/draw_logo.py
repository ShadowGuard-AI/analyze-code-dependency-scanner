#!/usr/bin/env python3
"""Dependency scanner logo: one weighted rope, one diver, the bed below. Name in stacked lines."""
import os
from PIL import Image, ImageDraw, ImageFont
V = os.environ.get("VARIANT", "")
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 900, 760
BLACK = (16, 18, 15); ASH = (233, 231, 221); YEL = (233, 197, 34); RED = (198, 58, 46)
img = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(img)
font = ImageFont.truetype(os.path.join(HERE, "fonts", "AtkinsonHyperlegibleMono.ttf"), 40)
x = 450
d.line([(x, 18), (x, 402)], fill=(210, 208, 196), width=5)
d.rectangle([x - 26, 196, x + 26, 216], fill=YEL)  # painted depth band at the diver's depth
d.ellipse([x - 30, 388, x + 30, 424], fill=(36, 36, 33), outline=(120, 118, 108), width=3)  # lead weight
# diver midway, profile, one hand on the rope, basket in the other hand
cx, cy = x + 6, 176
d.line([(cx, cy), (cx - 40, cy + 66)], fill=ASH, width=15)
d.line([(cx - 40, cy + 66), (cx - 74, cy + 122)], fill=ASH, width=12)
d.line([(cx - 40, cy + 66), (cx - 8, cy + 126)], fill=ASH, width=12)
d.polygon([(cx - 84, cy + 118), (cx - 108, cy + 140), (cx - 66, cy + 138)], fill=ASH)
d.polygon([(cx - 16, cy + 122), (cx - 30, cy + 150), (cx - 2, cy + 144)], fill=ASH)
d.ellipse([cx - 6, cy - 34, cx + 26, cy - 2], fill=ASH)
d.line([(cx + 10, cy + 8), (x + 2, cy + 52)], fill=ASH, width=11)
d.line([(cx + 4, cy + 12), (cx - 44, cy + 48)], fill=ASH, width=11)
bx, by = cx - 86, cy + 52
d.polygon([(bx - 30, by), (bx + 30, by), (bx + 22, by + 34), (bx - 22, by + 34)], fill=(150, 120, 70))
d.line([(bx - 30, by), (bx + 30, by)], fill=RED, width=5)
for i in range(3):
    d.line([(bx - 27 + i * 2, by + 9 + i * 8), (bx + 27 - i * 2, by + 9 + i * 8)], fill=(96, 74, 42), width=2)
# oyster bed: plain dark ovals with ash rims; v1 crowds the weight, v2 leaves it clear
spread = 34 if V == "1" else 62
for i, ox in enumerate(range(90, 830, spread)):
    y = 448 + (i % 2) * 14; r = 26 if V == "1" else 21
    d.ellipse([ox - r, y - r * 0.6, ox + r, y + r * 0.6], fill=(52, 52, 48), outline=ASH, width=3)
words = ["analyze", "code", "dependency", "scanner"]
for i, wtxt in enumerate(words):
    d.text((450, 492 + i * 62), wtxt, font=font, fill=ASH, anchor="ma")
out = os.path.join(HERE, "scratch", f"logo-v{V}.png") if V else os.path.join(HERE, "logo.png")
os.makedirs(os.path.dirname(out), exist_ok=True); img.save(out); print("saved", out)
if not V:
    img.resize((64, 54)).save(os.path.join(HERE, "scratch", "logo64-ship.png"))
