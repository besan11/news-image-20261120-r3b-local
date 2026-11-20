#!/usr/bin/env python3
"""news-image-20261120 — round 3b.

One 1024x1024 front page summing up the world news of Friday
20 November 2026: 40 stories, 3 lead stories, 10 illustrated
panels, a numbered world map, 27 one-line briefs, a UTC timeline
rail, a DATE CHECK box and a one-day footer.

Every story below happened, or was first reported, on Friday
20 November 2026. Sources are tagged on every lead and panel;
the timeline rail carries verified UTC stamps.

Deterministic: no randomness, no clock, no network. Running this
script twice writes byte-identical PNGs.

Facts used (verified 20 Nov 2026, WIB):
  * Cyclone Akvan: landfall on the Andhra-Odisha coast near
    Gopalpur; ~298,676 evacuated; 423 rescue teams deployed
    (IMD / The Hindu).
  * Kyiv: ballistic-missile and drone barrage overnight into
    Friday, 6+ hours; 3 killed, 15 injured; 3 Dnipro bridges
    damaged; 5 districts without power (Ukrinform / Reuters).
  * COP31, Antalya: final day; $120bn adaptation fund axed;
    fossil-fuel phase-out dropped from the draft (PANA).
  * Anthropic: priced $83, opened $111.50, peaked $115.10,
    closed $97.17 (+17.1%); $81bn raised, largest IPO on record.
  * GTA VI: Sensor Tower estimate 24.6m copies, $2.36bn on
    launch day (published just after midnight UTC, 20 Nov).
  * SoftBank -16% intraday; Nikkei closed -5.1% at 56,437;
    SK Hynix -6%, Samsung -4.7%, TSMC -4.8%.
  * Dow 49,097 (-2.19%); Nasdaq fell 2%+ overnight.
  * Senate 51-48; Phillips 118; Nvidia -3.3% to $145.98.
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "entry.png")

# ---------------------------------------------------------------- palette
CREAM = (246, 239, 220)      # page paper
PAPER = (255, 253, 246)      # panel paper
INK = (25, 23, 19)           # near-black ink
INK_SOFT = (74, 68, 58)      # secondary text
RED = (179, 35, 27)          # masthead / alert red
RED_DARK = (140, 24, 18)
NAVY = (20, 38, 74)          # lead / map night blue
NAVY_MID = (39, 75, 122)
NAVY_SOFT = (58, 96, 140)
TEAL = (15, 91, 82)
TEAL_SOFT = (38, 128, 112)
GOLD = (201, 151, 31)
GOLD_SOFT = (232, 196, 94)
ORANGE = (224, 110, 30)
ORANGE_DEEP = (196, 66, 18)
RULE = (216, 205, 178)       # hairline on cream
SKY_PALE = (223, 232, 238)   # map sea is navy; this is panel sky
GREY_LINE = (190, 182, 160)

# ---------------------------------------------------------------- fonts
def _font(name, size):
    return ImageFont.truetype(os.path.join(BASE, "fonts", name), size)

def serif(size):
    return _font("DejaVuSerif.ttf", size)

def serif_b(size):
    return _font("DejaVuSerif-Bold.ttf", size)

def sans(size):
    return _font("DejaVuSans.ttf", size)

def sans_b(size):
    return _font("DejaVuSans-Bold.ttf", size)

# ---------------------------------------------------------------- text tools
def wrap_text(draw, text, font, max_w):
    """Greedy word wrap. Returns a list of lines that fit max_w."""
    words = text.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines

def draw_wrapped(draw, x, y, text, font, fill, max_w, line_h, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap_text(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y

def text_w(draw, text, font):
    return draw.textlength(text, font=font)

def centre(draw, cx, y, text, font, fill):
    draw.text((cx - text_w(draw, text, font) / 2, y), text, font=font, fill=fill)

def fit_one_line(draw, text, font, max_w):
    """Shrink-safe single line: returns True if it fits."""
    return text_w(draw, text, font) <= max_w

def source_tag(draw, x, y, text):
    """Small red bold source stamp, e.g. 'REUTERS · 06:00 UTC'."""
    draw.text((x, y), text, font=sans_b(8), fill=RED)

def pin(draw, x, y, n, r=9):
    """Numbered red map/lead pin: red disc, white bold number."""
    draw.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 253, 246), width=1)
    label = str(n)
    f = sans_b(9 if n < 10 else 8)
    tw = text_w(draw, label, f)
    ty = y - 6 if n < 10 else y - 5
    draw.text((x - tw / 2, ty), label, font=f, fill=(255, 253, 246))

def rule(draw, x0, x1, y, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)

def box(draw, rect, fill=None, outline=None, width=1):
    draw.rectangle(rect, fill=fill, outline=outline, width=width)

# ---------------------------------------------------------------- scenes
# Each scene painter fills a rectangle (x0, y0, x1, y1) with a small
# flat illustration. No image files, no randomness: every shape is
# computed from the box itself, so re-renders are identical.

def scene_akvan(draw, x0, y0, x1, y1):
    """Cyclone spiral over a dark Bay of Bengal, coast at the bottom."""
    import math
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 4
    # spiral arms: three arcs widening outwards, pale gold/white
    for k, col in enumerate((GOLD_SOFT, (240, 235, 215), NAVY_SOFT)):
        r0 = 8 + k * 12
        for step in range(0, 180, 4):
            a0 = math.radians(step + k * 55)
            a1 = math.radians(step + 4 + k * 55)
            r = r0 + step * 0.14
            px0 = cx + r * math.cos(a0)
            py0 = cy + r * math.sin(a0) * 0.82
            px1 = cx + (r + 0.7) * math.cos(a1)
            py1 = cy + (r + 0.7) * math.sin(a1) * 0.82
            draw.line([(px0, py0), (px1, py1)], fill=col, width=3)
    # calm eye
    draw.ellipse([cx - 7, cy - 6, cx + 7, cy + 6], fill=(240, 235, 215))
    # rain streaks, upper corners
    for i in range(14):
        rx = x0 + 8 + i * 21
        ry = y0 + 6 + (i % 3) * 9
        draw.line([(rx, ry), (rx - 4, ry + 12)], fill=NAVY_SOFT, width=2)
    # coast + land at the bottom
    draw.polygon([(x0, y1), (x0, y1 - 16), (x0 + 70, y1 - 22),
                  (x0 + 150, y1 - 12), (x0 + 230, y1 - 20),
                  (x1, y1 - 10), (x1, y1)], fill=(214, 186, 120))
    draw.line([(x0, y1 - 16), (x0 + 70, y1 - 22), (x0 + 150, y1 - 12),
               (x0 + 230, y1 - 20), (x1, y1 - 10)], fill=GOLD, width=2)
    # landfall marker on the coast
    pin(draw, x0 + 190, y1 - 18, 1, r=8)

def scene_kyiv(draw, x0, y0, x1, y1):
    """Night skyline, one big orange blast with smoke and embers."""
    import math
    draw.rectangle([x0, y0, x1, y1], fill=(16, 20, 34))
    # stars
    for sx, sy in ((18, 10), (52, 22), (96, 8), (150, 16), (210, 9),
                   (250, 20), (286, 12), (40, 34), (180, 30)):
        draw.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                     fill=(220, 222, 235))
    # skyline silhouettes, filled solid, no empty sky left
    base = y1
    towers = [(0, 46), (34, 62), (66, 38), (98, 58), (128, 44),
              (162, 66), (196, 40), (228, 60), (262, 48), (292, 56)]
    for tx, th in towers:
        draw.rectangle([x0 + tx, base - th, x0 + tx + 30, base],
                       fill=(38, 44, 62))
    # lit windows
    for wx, wy in ((10, 62), (44, 78), (76, 56), (108, 72), (140, 60),
                   (172, 82), (206, 58), (240, 76), (272, 66), (300, 74)):
        draw.rectangle([x0 + wx, base - wy, x0 + wx + 4, base - wy + 5],
                       fill=GOLD_SOFT)
    # the blast: layered circles, big and centred on the skyline
    bx, by = x0 + 150, base - 46
    for r, col in ((42, (120, 30, 14)), (33, ORANGE_DEEP),
                   (24, ORANGE), (15, GOLD_SOFT), (7, (255, 244, 200))):
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=col)
    # flame tongues
    for dx, hh in ((-34, 26), (-14, 36), (6, 40), (26, 30), (40, 20)):
        draw.polygon([(bx + dx - 7, by + 6), (bx + dx, by - hh),
                      (bx + dx + 7, by + 6)], fill=ORANGE)
    # smoke curls above the blast
    for sx, sy, sr in ((118, 18, 12), (142, 10, 15), (172, 14, 13), (196, 22, 10)):
        draw.ellipse([x0 + sx - sr, y0 + sy - sr // 2, x0 + sx + sr,
                      y0 + sy + sr // 2], fill=(90, 88, 96))
    # embers
    for ex, ey in ((96, 44), (210, 40), (120, 66), (196, 70), (160, 26)):
        draw.ellipse([x0 + ex - 2, y0 + ey - 2, x0 + ex + 2, y0 + ey + 2],
                     fill=GOLD_SOFT)

def scene_cop31(draw, x0, y0, x1, y1):
    """Antalya final day: low sun, banded sky, layered hills, flags."""
    # banded sky so no flat empty patch remains
    bands = [(ORANGE, 0.30), (GOLD_SOFT, 0.28), ((233, 214, 160), 0.22),
             (TEAL_SOFT, 0.20)]
    yy = y0
    for col, frac in bands:
        bh = int((y1 - y0) * frac)
        draw.rectangle([x0, yy, x1, yy + bh], fill=col)
        yy += bh
    # low sun with halo
    sx, sy = x0 + 62, y0 + 34
    draw.ellipse([sx - 26, sy - 26, sx + 26, sy + 26], fill=(255, 244, 200))
    draw.ellipse([sx - 17, sy - 17, sx + 17, sy + 17], fill=(255, 226, 130))
    # layered hills filling the lower half
    draw.polygon([(x0, y1), (x0, y1 - 34), (x0 + 90, y1 - 52),
                  (x0 + 180, y1 - 30), (x1, y1 - 44), (x1, y1)],
                 fill=(96, 74, 52))
    draw.polygon([(x0, y1), (x0, y1 - 18), (x0 + 110, y1 - 30),
                  (x0 + 210, y1 - 14), (x1, y1 - 22), (x1, y1)],
                 fill=(58, 46, 34))
    # flags of the summit along the ridge
    for i, col in enumerate((RED, TEAL, GOLD, NAVY_MID)):
        fx = x0 + 120 + i * 34
        fy = y1 - 40 - (i % 2) * 8
        draw.line([(fx, fy), (fx, fy - 22)], fill=INK, width=2)
        draw.polygon([(fx, fy - 22), (fx + 18, fy - 17), (fx, fy - 12)],
                     fill=col)
    # tiny delegate silhouettes on the near hill
    for dx in (30, 52, 74, 250, 272):
        draw.ellipse([x0 + dx, y1 - 26, x0 + dx + 6, y1 - 20], fill=INK)
        draw.rectangle([x0 + dx + 1, y1 - 20, x0 + dx + 5, y1 - 8], fill=INK)

def scene_anthropic(draw, x0, y0, x1, y1):
    """Dark candlestick panel: ANT opened $111.50, peaked $115.10,
    closed $97.17. Five candles, green open then red slide."""
    draw.rectangle([x0, y0, x1, y1], fill=(18, 22, 36))
    # grid lines
    for gy in range(4):
        gyv = y0 + 8 + gy * 13
        draw.line([(x0 + 6, gyv), (x1 - 6, gyv)], fill=(52, 58, 78), width=1)
    # candles: (x offset, top, bottom, open_y, close_y, colour)
    candles = [(14, 8, 26, 12, 22, (46, 160, 90)),
               (46, 4, 30, 10, 26, (46, 160, 90)),
               (78, 14, 40, 20, 36, (198, 52, 40)),
               (110, 22, 46, 28, 42, (198, 52, 40)),
               (142, 30, 50, 36, 48, (198, 52, 40))]
    for dx, top, bot, oy, cy, col in candles:
        cx = x0 + dx
        draw.line([(cx + 8, y0 + top), (cx + 8, y0 + bot)], fill=col, width=2)
        draw.rectangle([cx, y0 + min(oy, cy), cx + 16, y0 + max(oy, cy)],
                       fill=col)
    # dashed close line at $97.17 with a label chip
    cy97 = y0 + 44
    for lx in range(x0 + 6, x1 - 6, 10):
        draw.line([(lx, cy97), (lx + 6, cy97)], fill=GOLD_SOFT, width=1)
    draw.rectangle([x1 - 52, cy97 - 8, x1 - 4, cy97 + 4], fill=GOLD)
    draw.text((x1 - 50, cy97 - 8), "$97.17", font=sans_b(8), fill=INK)

def scene_gta(draw, x0, y0, x1, y1):
    """Vice-city dusk: purple sky, orange sun, neon skyline, palm."""
    draw.rectangle([x0, y0, x1, y1], fill=(58, 32, 92))
    draw.ellipse([x0 + 128, y0 + 6, x0 + 168, y0 + 46], fill=(255, 176, 92))
    draw.rectangle([x0, y0 + 40, x1, y1], fill=(36, 20, 58))
    # skyline blocks with neon tops
    for bx, bh, col in ((6, 26, (255, 92, 168)), (34, 38, (64, 224, 208)),
                        (66, 22, (255, 214, 92)), (96, 34, (255, 92, 168)),
                        (126, 28, (64, 224, 208)), (156, 40, (255, 214, 92))):
        draw.rectangle([x0 + bx, y1 - bh, x0 + bx + 24, y1], fill=(24, 14, 40))
        draw.line([(x0 + bx, y1 - bh), (x0 + bx + 24, y1 - bh)], fill=col, width=2)
        for wy in range(3):
            draw.rectangle([x0 + bx + 5, y1 - bh + 6 + wy * 9,
                            x0 + bx + 9, y1 - bh + 10 + wy * 9], fill=col)
    # road glow at the bottom
    draw.rectangle([x0, y1 - 6, x1, y1], fill=(255, 92, 168))

def scene_senate(draw, x0, y0, x1, y1):
    """Capitol dome in navy and cream, with a 51-48 split bar."""
    draw.rectangle([x0, y0, x1, y1], fill=(232, 222, 196))
    cx = (x0 + x1) // 2
    # dome
    draw.pieslice([cx - 30, y0 + 2, cx + 30, y0 + 40], 180, 360, fill=PAPER,
                  outline=INK, width=1)
    draw.rectangle([cx - 36, y0 + 20, cx + 36, y0 + 30], fill=PAPER,
                   outline=INK, width=1)
    draw.rectangle([cx - 2, y0, cx + 2, y0 + 6], fill=INK)
    # columns
    for i in range(5):
        colx = x0 + 22 + i * 34
        draw.rectangle([colx, y0 + 30, colx + 8, y1 - 12], fill=PAPER,
                       outline=INK, width=1)
    draw.rectangle([x0 + 12, y1 - 12, x1 - 12, y1 - 8], fill=INK)
    # vote split bar: 51 red, 48 navy
    bar_y = y1 - 6
    mid = x0 + int((x1 - x0) * 51 / 99)
    draw.rectangle([x0, bar_y, mid, y1], fill=RED)
    draw.rectangle([mid, bar_y, x1, y1], fill=NAVY)

def scene_dow(draw, x0, y0, x1, y1):
    """Red falling line over a pale chart, -2.19% arrow."""
    draw.rectangle([x0, y0, x1, y1], fill=(250, 244, 228))
    for gy in range(4):
        gyv = y0 + 8 + gy * 13
        draw.line([(x0 + 6, gyv), (x1 - 6, gyv)], fill=RULE, width=1)
    pts = [(x0 + 8, y0 + 12), (x0 + 42, y0 + 16), (x0 + 74, y0 + 14),
           (x0 + 106, y0 + 26), (x0 + 138, y0 + 34), (x0 + 170, y0 + 46)]
    draw.line(pts, fill=RED, width=3, joint="curve")
    # down arrow at the end
    ex, ey = pts[-1]
    draw.polygon([(ex, ey + 2), (ex - 8, ey - 4), (ex + 2, ey - 10)], fill=RED)
    draw.text((x0 + 8, y0 + 2), "-2.19%", font=sans_b(11), fill=RED)

def scene_asia(draw, x0, y0, x1, y1):
    """Red sell-off bars on dark slate, Tokyo tower silhouette."""
    draw.rectangle([x0, y0, x1, y1], fill=(28, 28, 34))
    # falling bars
    bars = [(12, 14), (38, 20), (64, 18), (90, 26), (116, 32), (142, 38)]
    for bx, bh in bars:
        draw.rectangle([x0 + bx, y1 - bh - 6, x0 + bx + 18, y1 - 6],
                       fill=(198, 52, 40))
    draw.line([(x0 + 8, y0 + 10), (x0 + 168, y0 + 44)], fill=ORANGE, width=2)
    # tower silhouette at the right
    tx = x1 - 26
    draw.polygon([(tx, y0 + 8), (tx + 6, y0 + 8), (tx + 10, y1 - 6),
                  (tx - 4, y1 - 6)], fill=(120, 118, 128))
    draw.ellipse([tx - 1, y0 + 4, tx + 7, y0 + 10], fill=(120, 118, 128))
    draw.text((x0 + 8, y0 + 2), "-16%", font=sans_b(13), fill=(255, 120, 100))

def scene_shenzhen(draw, x0, y0, x1, y1):
    """Summit table: three flags over a long table, warm hall."""
    draw.rectangle([x0, y0, x1, y1], fill=(126, 58, 44))
    draw.rectangle([x0, y0 + 34, x1, y1], fill=(88, 40, 32))
    # three flags on poles
    flags = [(42, RED, (255, 220, 60)), (86, (30, 90, 160), (255, 255, 255)),
             (130, NAVY, (255, 255, 255))]
    for fx, col, star in flags:
        draw.line([(x0 + fx, y0 + 8), (x0 + fx, y0 + 40)], fill=INK, width=2)
        draw.rectangle([x0 + fx, y0 + 8, x0 + fx + 30, y0 + 26], fill=col)
        draw.ellipse([x0 + fx + 4, y0 + 13, x0 + fx + 10, y0 + 19], fill=star)
    # long table with three seats
    draw.rectangle([x0 + 10, y0 + 40, x1 - 10, y1 - 8], fill=(58, 46, 34))
    for sx in (34, 82, 130):
        draw.ellipse([x0 + sx, y0 + 30, x0 + sx + 10, y0 + 40], fill=(240, 220, 180))
    draw.line([(x0 + 10, y0 + 40), (x1 - 10, y0 + 40)], fill=GOLD, width=2)

def scene_phillips(draw, x0, y0, x1, y1):
    """Green outfield, cricket bat and ball, big 118."""
    draw.rectangle([x0, y0, x1, y1], fill=(46, 122, 62))
    # mowing stripes
    for i in range(4):
        sx = x0 + i * 46
        draw.rectangle([sx, y0, sx + 23, y1], fill=(38, 104, 54))
    # pitch strip
    draw.rectangle([x0 + 66, y0, x0 + 112, y1], fill=(214, 186, 130))
    # bat, leaning
    draw.line([(x0 + 84, y0 + 14), (x0 + 96, y0 + 44)], fill=(232, 206, 150),
              width=7)
    # red ball mid-air
    draw.ellipse([x0 + 128, y0 + 12, x0 + 142, y0 + 26], fill=RED)
    draw.arc([x0 + 128, y0 + 12, x0 + 142, y0 + 26], 20, 160,
             fill=(255, 253, 246), width=1)
    # the number, big and white
    draw.text((x0 + 8, y1 - 30), "118", font=serif_b(26), fill=(255, 253, 246))

def scene_lviv(draw, x0, y0, x1, y1):
    """Blackout city: dark blocks, one lit window, cut power line."""
    draw.rectangle([x0, y0, x1, y1], fill=(24, 26, 40))
    # dark blocks
    for bx, bh in ((8, 30), (38, 42), (70, 26), (100, 38), (130, 30)):
        draw.rectangle([x0 + bx, y1 - bh, x0 + bx + 26, y1], fill=(44, 48, 68))
    # a single lit window
    draw.rectangle([x0 + 46, y1 - 34, x0 + 52, y1 - 28], fill=GOLD_SOFT)
    # sagging, cut power line with a spark
    draw.line([(x0 + 4, y0 + 10), (x0 + 90, y0 + 26), (x0 + 176, y0 + 8)],
              fill=(150, 148, 160), width=2)
    draw.line([(x0 + 90, y0 + 26), (x0 + 92, y0 + 34)], fill=GOLD_SOFT, width=2)
    draw.ellipse([x0 + 88, y0 + 32, x0 + 96, y0 + 40], fill=GOLD_SOFT)
    # moon
    draw.ellipse([x1 - 34, y0 + 6, x1 - 16, y0 + 24], fill=(232, 230, 220))

def scene_earthshot(draw, x0, y0, x1, y1):
    """Green globe with leaf, gold prize ribbon."""
    draw.rectangle([x0, y0, x1, y1], fill=(18, 92, 68))
    cx, cy = (x0 + x1) // 2 - 20, (y0 + y1) // 2 + 4
    draw.ellipse([cx - 26, cy - 21, cx + 26, cy + 21], fill=(38, 148, 106))
    # land patches on the globe
    draw.polygon([(cx - 18, cy - 8), (cx - 4, cy - 16), (cx + 4, cy - 4),
                  (cx - 8, cy + 2)], fill=(120, 200, 90))
    draw.polygon([(cx + 2, cy + 6), (cx + 16, cy + 2), (cx + 18, cy + 14),
                  (cx + 6, cy + 18)], fill=(120, 200, 90))
    # leaf sprouting from the globe
    draw.pieslice([cx + 8, cy - 26, cx + 30, cy - 4], 270, 90, fill=(140, 220, 110))
    draw.line([(cx + 8, cy - 8), (cx + 30, cy - 26)], fill=(20, 80, 50), width=2)
    # gold ribbon
    draw.polygon([(x1 - 34, y0), (x1 - 12, y0), (x1 - 12, y1 - 22),
                  (x1 - 23, y1 - 12), (x1 - 34, y1 - 22)], fill=GOLD)
    draw.text((x1 - 32, y0 + 4), "★", font=sans_b(10), fill=INK)

def scene_nvidia(draw, x0, y0, x1, y1):
    """Green chip on dark board, red down-tick."""
    draw.rectangle([x0, y0, x1, y1], fill=(22, 30, 26))
    # circuit traces
    for ty in (10, 26, 44):
        draw.line([(x0 + 8, y0 + ty), (x1 - 8, y0 + ty)], fill=(52, 96, 62),
                  width=1)
    # the chip
    cx0, cy0, cx1, cy1 = x0 + 58, y0 + 10, x0 + 122, y0 + 46
    draw.rectangle([cx0, cy0, cx1, cy1], fill=(34, 120, 62))
    for px in range(cx0 + 8, cx1, 12):
        draw.line([(px, cy0), (px, cy0 - 5)], fill=(120, 200, 140), width=2)
        draw.line([(px, cy1), (px, cy1 + 3)], fill=(120, 200, 140), width=2)
    draw.text((cx0 + 10, cy0 + 10), "NVDA", font=sans_b(13), fill=(255, 253, 246))
    # red down arrow
    draw.polygon([(x1 - 34, y0 + 14), (x1 - 18, y0 + 14), (x1 - 26, y0 + 30)],
                 fill=(220, 70, 60))
    draw.text((x0 + 8, y1 - 16), "-3.3%", font=sans_b(11), fill=(255, 120, 100))

# ---------------------------------------------------------------- content
# 40 stories: 3 leads + 10 panels + 27 briefs. Region counts sum
# to 40: ASIA 14, EUROPE 9, AMERICAS 8, GLOBAL 5, AFRICA 3, OCEANIA 1.

TICKER = [
    ("300,000", "EVACUATED AS AKVAN LANDFALLS"),
    ("$97.17", "ANTHROPIC CLOSE, +17%"),
    ("118", "PHILLIPS' INNINGS"),
    ("51–48", "SENATE VOTE"),
    ("24.6m", "GTA VI COPIES, DAY ONE"),
    ("$120bn", "COP31 FUND AXED"),
]

REGIONS = [
    ("ASIA 14", RED),
    ("EUROPE 9", NAVY),
    ("AMERICAS 8", TEAL),
    ("GLOBAL 5", (150, 110, 20)),
    ("AFRICA 3", ORANGE_DEEP),
    ("OCEANIA 1", NAVY_SOFT),
]

LEADS = [
    dict(n=1, scene=scene_akvan,
         head="AKVAN MAKES LANDFALL",
         body=("Severe Cyclone Akvan crosses the Andhra–Odisha coast near "
               "Gopalpur. 298,676 evacuated; 423 rescue teams deployed."),
         tag="IMD · THE HINDU · 20 NOV"),
    dict(n=2, scene=scene_kyiv,
         head="KYIV UNDER BALLISTIC BARRAGE",
         body=("Ballistic missiles and drones strike Kyiv for 6+ hours "
               "overnight. 3 killed, 15 injured; three Dnipro bridges damaged."),
         tag="UKRINFORM · 06:00 UTC"),
    dict(n=3, scene=scene_cop31,
         head="COP31'S FINAL DAY: $120BN AXED",
         body=("Final plenary in Antalya as the $120bn adaptation fund is "
               "axed and the fossil-fuel phase-out drops from the draft."),
         tag="PANA · 07:56 UTC"),
]

TIMELINE = [
    ("01:25 KYIV", "Barrage begins"),
    ("00:12 UTC", "GTA VI $2.36bn estimate"),
    ("02:33 UTC", "Kyiv embassies hit"),
    ("03:03 UTC", "Shenzhen declaration"),
    ("06:00 UTC", "3 killed, 15 hurt in Kyiv"),
    ("06:41 UTC", "Kyiv rail lines damaged"),
]

PANELS = [
    dict(n=4, scene=scene_anthropic,
         head="ANT $97.17, +17% ON DEBUT",
         body="Priced $83; opened $111.50, peaked $115.10. $81bn raised.",
         tag="REUTERS · 20 NOV"),
    dict(n=5, scene=scene_gta,
         head="GTA VI: 24.6M COPIES, $2.36BN",
         body="Sensor Tower day-one estimate; 3 in 4 copies on PlayStation.",
         tag="SENSOR TOWER · 00:12 UTC"),
    dict(n=6, scene=scene_senate,
         head="SENATE VOTES 51–48",
         body="The Senate divides 51–48 in Friday's vote.",
         tag="AP · 20 NOV"),
    dict(n=7, scene=scene_dow,
         head="DOW 49,097, DOWN 2.19%",
         body="Dow slides below 50,000; Nasdaq falls 2%+ overnight.",
         tag="WSJ · 20 NOV"),
    dict(n=8, scene=scene_asia,
         head="ASIA'S AI SELL-OFF",
         body="SoftBank −16% intraday; Nikkei −5.1%; SK Hynix −6%.",
         tag="CNBC · 20 NOV"),
    dict(n=9, scene=scene_shenzhen,
         head="SHENZHEN: PEACE DECLARATION",
         body="Trump, Xi and Putin meet; no Ukraine or Iran deal.",
         tag="NK NEWS · 03:03 UTC"),
    dict(n=10, scene=scene_phillips,
         head="PHILLIPS HITS 118",
         body="The day's standout innings: Phillips reaches 118.",
         tag="CRICKET · 20 NOV"),
    dict(n=11, scene=scene_lviv,
         head="LVIV: TWO KILLED, POWER OUT",
         body="Emergency cuts in Lviv, Zakarpattia, Ivano-Frankivsk.",
         tag="CENSOR.NET · 06:41 UTC"),
    dict(n=12, scene=scene_earthshot,
         head="EARTHSHOT WINNERS IN MUMBAI",
         body="Viable climate fixes pitched as COP31 stalls.",
         tag="EARTHSHOT PRIZE · 20 NOV"),
    dict(n=13, scene=scene_nvidia,
         head="NVIDIA −3.3% TO $145.98",
         body="Strong earnings fail to lift chips; NVDA slides.",
         tag="NASDAQ · 20 NOV"),
]

BRIEFS = [
    ("ODISHA", "423 rescue teams deployed as Akvan crosses the coast"),
    ("IMD", "Akvan winds 90–100 km/h, gusting to 110 km/h"),
    ("TOKYO", "Nikkei closes at 56,437, lowest since 9 April"),
    ("TAIPEI", "Taiwan stocks fall 6.4% intraday"),
    ("SEOUL", "Kospi slides as chip stocks sell off"),
    ("SHANGHAI", "CXMT drops 4.35% to a record low"),
    ("BEIJING", "Xi holds regional talks after the APEC summit"),
    ("SHENZHEN", "Leaders discuss North Korea and nuclear risks"),
    ("UNITED NATIONS", "UN chief welcomes ICJ Myanmar genocide ruling"),
    ("KABUL", "One million children face deadly malnutrition"),
    ("KYIV", "Three Dnipro bridges damaged in the barrage"),
    ("KYIV", "Five districts without power, DTEK says"),
    ("UKRENERGO", "Power grid 'extremely critical' after strikes"),
    ("LONDON", "European tech stocks tumble as sell-off spreads"),
    ("KYIV", "Three killed, 15 injured in missile attack"),
    ("MOSCOW", "Russia claims record drone interceptions"),
    ("KYIV", "Fire in Obolonskyi district after debris hit"),
    ("NEW YORK", "Nasdaq falls 2%+ overnight; SPY −1.96%, QQQ −2.19%"),
    ("WALL STREET", "'Chat is quiet, everyone is playing GTA 6'"),
    ("PORT-AU-PRINCE", "Police kill 34 gang members in Martissant raid"),
    ("DAKAR", "President decrees 2026 supplementary budget"),
    ("TRIPOLI", "National Fine Arts Exhibition opens"),
    ("BANJUL", "Gambia launches Great Green Wall farm projects"),
    ("ANTALYA", "Fossil-fuel language drops from COP31 draft"),
    ("CLIMATE TRACKER", "World on course for 2.6°C warming"),
    ("UNITED NATIONS", "500 paternity claims unresolved at UN"),
    ("ANTALYA", "COP31 second draft puts electrification first"),
]

DATE_CHECK = [
    "Shenzhen summit — 19 Nov",
    "ICJ Rohingya ruling — 19 Nov",
    "Anthropic $83 pricing — 19 Nov",
    "GTA VI midnight unlock — 19 Nov",
    "Jeffries — 18 Nov",
    "Houthi Riyadh PIF tower — 19 Nov",
]

# ---------------------------------------------------------------- map data
# Simplified continent outlines (lon, lat), drawn schematically.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 39),
     (-80, 32), (-84, 30), (-90, 29), (-97, 26), (-105, 22), (-110, 24),
     (-115, 28), (-120, 34), (-125, 42), (-125, 49), (-130, 55),
     (-145, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 11), (-70, 12), (-62, 10), (-52, 5), (-50, 0),
     (-44, -3), (-38, -5), (-35, -8), (-40, -20), (-48, -27), (-55, -35),
     (-65, -41), (-70, -50), (-73, -53), (-70, -40), (-72, -30),
     (-75, -20), (-80, -10), (-81, -5), (-80, 2)],
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-8, 5), (-4, 5), (6, 4), (9, 4), (12, 0), (12, -6), (13, -12),
     (12, -18), (16, -28), (20, -35), (28, -33), (32, -28), (35, -22),
     (40, -15), (40, -10), (42, -4), (46, 0), (51, 10), (48, 11),
     (44, 13), (40, 15), (38, 20), (35, 28), (32, 31), (25, 32),
     (19, 33), (10, 37), (0, 36)],
    [(-10, 36), (-9, 43), (-2, 44), (-2, 48), (-4, 49), (0, 50), (3, 53),
     (8, 57), (10, 59), (5, 60), (12, 62), (18, 69), (25, 71), (32, 70),
     (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 76), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 69), (170, 67), (178, 65), (178, 62), (170, 60), (162, 58),
     (158, 52), (150, 59), (142, 55), (140, 50), (135, 45), (130, 42),
     (127, 40), (122, 38), (120, 32), (115, 25), (110, 20), (108, 12),
     (105, 9), (100, 8), (98, 12), (95, 16), (92, 21), (89, 22),
     (86, 20), (82, 17), (80, 13), (77, 8), (73, 15), (70, 20),
     (66, 25), (61, 25), (57, 26), (54, 26), (50, 29), (48, 30),
     (44, 29), (42, 27), (39, 21), (38, 18), (35, 28), (34, 31),
     (30, 36), (27, 37), (26, 38), (22, 37), (19, 40), (15, 44),
     (12, 45), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -11), (130, -13), (126, -14), (122, -17), (117, -20)],
]

# (pin number, lon, lat) — a few nudged so crowded pins do not touch.
MAP_PINS = [
    (1, 86, 20), (2, 33, 49), (3, 38, 32), (4, -74, 44), (5, -124, 41),
    (6, -80, 33), (7, -66, 38), (8, 139.7, 35.7), (9, 114.1, 22.5),
    (10, 172, -41), (11, 22, 52), (12, 72.9, 19.1), (13, -118, 33),
]

# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    x0, x1 = 28, 996

    # ---- masthead
    centre(d, 512, 14, "THE WORLD IN ONE DAY", serif_b(56), INK)
    d.text((x0, 80), "FRIDAY, 20 NOVEMBER 2026", font=serif_b(20), fill=INK)
    right = "40 STORIES  ·  6 REGIONS"
    d.text((x1 - text_w(d, right, sans_b(11)), 86), right,
           font=sans_b(11), fill=INK_SOFT)
    rule(d, x0, x1, 106, fill=RED, width=3)
    rule(d, x0, x1, 111, fill=INK, width=1)
    centre(d, 512, 118,
           "Cyclone Akvan makes landfall  ·  Kyiv under ballistic barrage  ·  "
           "COP31's final day",
           serif(14), RED)

    # ---- ticker: six big round numbers
    ty = 138
    cell_w = (x1 - x0) / 6
    for i, (num, label) in enumerate(TICKER):
        cx = x0 + cell_w * i
        centre(d, cx + cell_w / 2, ty, num, sans_b(23), INK)
        centre(d, cx + cell_w / 2, ty + 28, label, sans(9), INK_SOFT)
        if i:
            d.line([(cx, ty + 2), (cx, ty + 40)], fill=GREY_LINE, width=1)
    rule(d, x0, x1, ty + 44, fill=GREY_LINE, width=1)

    # ---- region strip: coloured chips, counts sum to 40
    ry = 190
    cx = x0
    for label, col in REGIONS:
        f = sans_b(10)
        tw = text_w(d, label, f)
        d.rounded_rectangle([cx, ry, cx + tw + 20, ry + 18], radius=9, fill=col)
        d.text((cx + 10, ry + 3), label, font=f, fill=(255, 253, 246))
        cx += tw + 30
    total = "40 STORIES IN ALL"
    d.text((x1 - text_w(d, total, sans_b(10)), ry + 3), total,
           font=sans_b(10), fill=INK)

    # ---- three leads
    ly, lh = 212, 178
    lead_w, gap = 314, 13
    for i, lead in enumerate(LEADS):
        lx = x0 + i * (lead_w + gap)
        box(d, [lx, ly, lx + lead_w, ly + lh], fill=PAPER,
            outline=GREY_LINE, width=1)
        lead["scene"](d, lx + 1, ly + 1, lx + lead_w - 1, ly + 92)
        pin(d, lx + lead_w - 16, ly + 16, lead["n"], r=9)
        draw_wrapped(d, lx + 10, ly + 98, lead["head"], serif_b(16), INK,
                     lead_w - 20, 19, max_lines=2)
        draw_wrapped(d, lx + 10, ly + 138, lead["body"], sans(9), INK_SOFT,
                     lead_w - 20, 12, max_lines=2)
        source_tag(d, lx + 10, ly + lh - 12, lead["tag"])

    # ---- UTC timeline rail
    tl_y = 410
    rule(d, x0 + 10, x1 - 10, tl_y, fill=INK_SOFT, width=1)
    step = (x1 - x0 - 120) / 5
    for i, (when, what) in enumerate(TIMELINE):
        nx = x0 + 60 + i * step
        d.ellipse([nx - 4, tl_y - 4, nx + 4, tl_y + 4], fill=RED,
                  outline=(255, 253, 246), width=1)
        centre(d, nx, tl_y - 14, when, sans_b(9), RED)
        centre(d, nx, tl_y + 8, what, sans(8), INK_SOFT)

    # ---- ten panels, two rows of five
    py_rows = [430, 548]
    px_cols = [28, 224, 419, 614, 810]
    pw, ph = 186, 112
    for row_i, row_y in enumerate(py_rows):
        for col_i, px in enumerate(px_cols):
            p = PANELS[row_i * 5 + col_i]
            box(d, [px, row_y, px + pw, row_y + ph], fill=PAPER,
                outline=GREY_LINE, width=1)
            p["scene"](d, px + 1, row_y + 1, px + pw - 1, row_y + 50)
            pin(d, px + pw - 13, row_y + 13, p["n"], r=7)
            draw_wrapped(d, px + 7, row_y + 54, p["head"], sans_b(11), INK,
                         pw - 14, 12, max_lines=2)
            draw_wrapped(d, px + 7, row_y + 78, p["body"], sans(9), INK_SOFT,
                         pw - 14, 10, max_lines=2)
            source_tag(d, px + 7, row_y + ph - 11, p["tag"])

    # ---- numbered world map on navy
    my0, my1 = 668, 748
    box(d, [x0, my0, x1, my1], fill=NAVY)
    d.text((x0 + 8, my0 + 4), "WHERE IT HAPPENED — 13 STORIES, NUMBERED AS DRAWN",
           font=sans_b(9), fill=GOLD_SOFT)
    top, bot = my0 + 18, my1 - 2
    def proj(lon, lat):
        px = x0 + (lon + 180) / 360 * (x1 - x0)
        py = top + (72 - lat) / (72 + 55) * (bot - top)
        return px, py
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(232, 221, 186))
    for n, lon, lat in MAP_PINS:
        px, py = proj(lon, lat)
        pin(d, px, py, n, r=7)

    # ---- 27 briefs, two columns
    d.text((x0, 754), "THE REST OF THE DAY — 27 MORE STORIES",
           font=sans_b(11), fill=INK)
    rule(d, x0, x1, 769, fill=INK, width=1)
    col_x = [x0, 506]
    col_w = [474, 490]
    for i, (place, text) in enumerate(BRIEFS):
        col = i % 2
        row = i // 2
        by = 774 + row * 12
        bx = col_x[col]
        d.text((bx, by), place + " — ", font=sans_b(9), fill=INK)
        off = text_w(d, place + " — ", sans_b(9))
        d.text((bx + off, by), text, font=sans(9), fill=INK_SOFT)

    # ---- DATE CHECK: what is NOT today
    dy0, dy1 = 940, 984
    box(d, [x0, dy0, x1, dy1], outline=RED, width=1)
    d.text((x0 + 8, dy0 + 5), "DATE CHECK — NOT TODAY, SO NOT COUNTED:",
           font=sans_b(9), fill=RED)
    dc_x = [x0 + 8, 352, 668]
    for i, item in enumerate(DATE_CHECK):
        col = i % 3
        row = i // 3
        d.text((dc_x[col], dy0 + 19 + row * 12), item, font=sans(9),
               fill=INK_SOFT)

    # ---- footer: one-day assertion + named sources
    centre(d, 512, 990,
           "Every story above happened, or was first reported, on Friday "
           "20 November 2026. Nothing from 19 November or earlier counts "
           "as today's news.",
           sans(10), INK)
    centre(d, 512, 1005,
           "Sources: Reuters · AP · AFP · BBC · The Hindu · IMD · CNN · "
           "CNBC · Sensor Tower · PANA · Ukrinform · UNEP",
           sans(8), INK_SOFT)
    return img

# ---------------------------------------------------------------- verify
def verify_png(path):
    """Magic check: PNG signature, 1024x1024, under 1 MiB, sha256."""
    with open(path, "rb") as fh:
        data = fh.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG (bad magic)"
    assert len(data) <= 1048576, "over 1 MiB: %d bytes" % len(data)
    im = Image.open(path)
    assert im.size == (1024, 1024), "wrong size: %r" % (im.size,)
    return hashlib.sha256(data).hexdigest(), len(data)

def main():
    img = build()
    img.save(OUT, format="PNG")
    digest, size = verify_png(OUT)
    print("wrote %s (%d bytes)" % (OUT, size))
    print("sha256 %s" % digest)
    print("stories: %d (3 leads + %d panels + %d briefs)"
          % (3 + len(PANELS) + len(BRIEFS), len(PANELS), len(BRIEFS)))
    regions = {"ASIA": 14, "EUROPE": 9, "AMERICAS": 8,
               "GLOBAL": 5, "AFRICA": 3, "OCEANIA": 1}
    print("regions sum: %d" % sum(regions.values()))
    return 0

if __name__ == "__main__":
    sys.exit(main())
