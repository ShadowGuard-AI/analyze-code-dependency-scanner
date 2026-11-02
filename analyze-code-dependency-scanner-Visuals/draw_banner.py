#!/usr/bin/env python3
"""Dependency scanner banner: three ropes from a named hull, down, at work, rising."""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(7)
V = os.environ.get("VARIANT", "")
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1200, 520
BLACK = (16, 18, 15); ASH = (233, 231, 221); YEL = (233, 197, 34); RED = (198, 58, 46)
img = Image.new("RGB", (W, H), (60, 72, 72)); d = ImageDraw.Draw(img, "RGBA")
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(128 - 92 * t), int(134 - 96 * t), int(130 - 94 * t)))
# hull across the top, name lettered along it
d.polygon([(0, 0), (W, 0), (W, 58), (120, 78), (0, 66)], fill=BLACK)
font = ImageFont.truetype(os.path.join(HERE, "fonts", "AtkinsonHyperlegibleMono.ttf"), 27 if V == "1" else 24)
name = "analyze-code-dependency-scanner"
if V == "1":
    d.text((14, 16), name, font=font, fill=ASH)  # flaw: runs past the hull taper
else:
    d.text((600, 15), name, font=font, fill=ASH, anchor="ma")
def diver(cx, cy, s, flip=1):
    col = BLACK
    d.line([(cx, cy), (cx - 34 * flip * s, cy + 58 * s)], fill=col, width=max(3, int(13 * s)))
    d.line([(cx - 34 * flip * s, cy + 58 * s), (cx - 62 * flip * s, cy + 110 * s)], fill=col, width=max(3, int(10 * s)))
    d.line([(cx - 34 * flip * s, cy + 58 * s), (cx - 4 * flip * s, cy + 114 * s)], fill=col, width=max(3, int(10 * s)))
    d.ellipse([cx - 14 * s, cy - 28 * s, cx + 14 * s, cy], fill=col)
    d.line([(cx, cy + 8 * s), (cx + 14 * flip * s, cy + 44 * s)], fill=col, width=max(3, int(9 * s)))
def basket(bx, by, full=False):
    d.polygon([(bx - 34, by), (bx + 34, by), (bx + 26, by + 36), (bx - 26, by + 36)], fill=(122, 96, 58))
    d.line([(bx - 34, by), (bx + 34, by)], fill=RED, width=4)
    n = 4 if full else 2
    for i in range(n):
        sx = bx - 22 + i * 14
        d.ellipse([sx - 10, by - 9, sx + 10, by + 4], fill=(56, 56, 52), outline=ASH, width=2)
ropes = [220, 600, 980]
for x in ropes:
    d.line([(x, 62), (x, 424)], fill=(22, 22, 20), width=4)
    for yy in range(110, 410, 62):
        d.rectangle([x - 9, yy, x + 9, yy + 14], fill=YEL)
    d.ellipse([x - 17, 412, x + 17, 440], fill=(26, 26, 24), outline=(100, 98, 90), width=2)
diver(238, 150, 0.95)            # left rope, on the way down
diver(618, 330, 0.9)             # middle rope, at the bed
basket(676, 420)
diver(962, 196, 0.95, flip=-1)   # right rope, already rising
basket(906, 268, full=True)
# bed across the lower third
d.rectangle([0, 436, W, H], fill=(102, 96, 82))
for _ in range(2200):
    px, py = random.uniform(0, W), random.uniform(438, H)
    d.point((px, py), fill=random.choice([(116, 108, 92), (90, 84, 70)]))
for cx in range(16, W, 48):
    for k in range(2):
        ox = cx + random.uniform(-10, 10); oy = 452 + (cx % 3) * 16 + random.uniform(-4, 16); r = random.uniform(12, 19)
        d.ellipse([ox - r, oy - r * 0.6, ox + r, oy + r * 0.6], fill=(52, 52, 48), outline=ASH, width=2)
img = img.filter(ImageFilter.GaussianBlur(0.5))
out = os.path.join(HERE, "scratch", f"banner-v{V}.png") if V else os.path.join(HERE, "banner.png")
os.makedirs(os.path.dirname(out), exist_ok=True); img.save(out); print("saved", out)
