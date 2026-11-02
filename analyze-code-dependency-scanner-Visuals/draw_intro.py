#!/usr/bin/env python3
"""Dependency scanner intro: pearl diver pause above the oyster bed. Scenery only, no text."""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
random.seed(11)
V = os.environ.get("VARIANT", "")
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1200, 520
BLACK = (16, 18, 15); ASH = (233, 231, 221); YEL = (233, 197, 34); RED = (198, 58, 46)
img = Image.new("RGB", (W, H), (52, 64, 66)); d = ImageDraw.Draw(img, "RGBA")
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(120 - 88 * t), int(128 - 92 * t), int(124 - 92 * t)))
# soft light column around the central rope
for i in range(26):
    x0 = 600 - 190 + i * 15
    d.polygon([(x0, 0), (x0 + 90, 0), (x0 + 210, 430), (x0 + 60, 430)], fill=(255, 252, 230, 7))
# broken bright surface
for x in range(0, W, 46):
    d.line([(x, 4), (x + 26, 4)], fill=(246, 244, 230), width=3)
# hull underside crossing the top right corner, no name on it
d.polygon([(880, 0), (1200, 0), (1200, 64), (960, 44)], fill=BLACK)
d.line([(960, 44), (1200, 64)], fill=(8, 9, 8), width=4)
def rope(x, top, bottom, alpha, width):
    d.line([(x, top), (x + 4, bottom)], fill=(20, 20, 18, alpha), width=width)
    for yy in range(top + 34, bottom, 68):
        d.rectangle([x - 7, yy, x + 11, yy + 13], fill=(*YEL, alpha))
    d.ellipse([x - 15, bottom - 6, x + 19, bottom + 22], fill=(24, 24, 22, alpha), outline=(90, 88, 80, alpha), width=2)
thin = 1 if V == "1" else 3
rope(212, 58, 408, 110, max(1, thin - 1))
rope(968, 66, 420, 120, max(1, thin - 1))
rope(600, 40, 428, 255, thin + 1)
def diver(cx, cy, s, col=BLACK):
    d.line([(cx, cy), (cx - 34 * s, cy + 58 * s)], fill=col, width=max(3, int(13 * s)))
    d.line([(cx - 34 * s, cy + 58 * s), (cx - 62 * s, cy + 112 * s)], fill=col, width=max(3, int(10 * s)))
    d.line([(cx - 34 * s, cy + 58 * s), (cx - 6 * s, cy + 116 * s)], fill=col, width=max(3, int(10 * s)))
    d.polygon([(cx - 70 * s, cy + 108 * s), (cx - 92 * s, cy + 128 * s), (cx - 58 * s, cy + 126 * s)], fill=col)
    d.polygon([(cx - 12 * s, cy + 112 * s), (cx - 26 * s, cy + 138 * s), (cx + 2 * s, cy + 132 * s)], fill=col)
    d.ellipse([cx - 4 * s, cy - 30 * s, cx + 24 * s, cy - 2 * s], fill=col)
    d.line([(cx + 8 * s, cy + 6 * s), (cx + 4, cy + 44 * s)], fill=col, width=max(3, int(9 * s)))
    d.line([(cx + 2 * s, cy + 10 * s), (cx - 26 * s, cy + 40 * s)], fill=col, width=max(3, int(9 * s)))
diver(612, 168, 0.92)
# distant second diver near the bed, a shape only
diver(972, 330, 0.5, col=(30, 34, 32))
# oyster bed: packed clusters, ash rims, sand and stones between
d.rectangle([0, 428, W, H], fill=(104, 98, 84))
for _ in range(2600):
    x, y = random.uniform(0, W), random.uniform(430, H)
    d.point((x, y), fill=random.choice([(118, 110, 94), (92, 86, 72), (128, 120, 102)]))
for cx in range(20, W, 52):
    for k in range(3):
        x = cx + random.uniform(-14, 14); y = 448 + (cx % 3) * 18 + random.uniform(-6, 22)
        r = random.uniform(13, 21)
        d.ellipse([x - r, y - r * 0.62, x + r, y + r * 0.62], fill=(52, 52, 48), outline=ASH, width=2)
        d.arc([x - r * 0.6, y - r * 0.3, x + r * 0.6, y + r * 0.34], 10, 170, fill=(160, 156, 144), width=2)
# woven basket resting on the sand, shells inside
bx, by = (330, 452) if V != "1" else (330, 428)
d.polygon([(bx - 72, by), (bx + 72, by), (bx + 54, by + 52), (bx - 54, by + 52)], fill=(122, 96, 58))
for i in range(6):
    yy = by + 4 + i * 8
    d.line([(bx - 70 + i * 3, yy), (bx + 70 - i * 3, yy)], fill=(84, 64, 38), width=2)
for i in range(-3, 4):
    d.line([(bx + i * 18, by), (bx + i * 13, by + 52)], fill=(84, 64, 38), width=2)
d.line([(bx - 72, by), (bx + 72, by)], fill=RED, width=4)
for sx in (-34, -6, 26):
    d.ellipse([bx + sx - 15, by - 13, bx + sx + 15, by + 4], fill=(56, 56, 52), outline=ASH, width=2)
img = img.filter(ImageFilter.GaussianBlur(0.5))
out = os.path.join(HERE, "scratch", f"intro-v{V}.png") if V else os.path.join(HERE, "intro-banner.png")
os.makedirs(os.path.dirname(out), exist_ok=True); img.save(out); print("saved", out)
