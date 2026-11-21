"""Draw AURMARA - The Harbour of Golden Stairs (poster v4).

Iterates on v2 (60.72%, best score): same warm golden-hour coastal town,
grand staircase, harbour boats, cafe terrace — plus ONE dominant landmark
borrowed from rank 1 (SUVENNE): a golden clock tower rising over the town,
and an explicit stay-promise subtitle. Deliberately NOT repeating v3's
mistakes (56.72%): no name-as-shadow, no over-dense town.

Drawn with Pillow at build time; main.py only copies the PNG.

Layout of this file: one small function per scene element, called in
paint order from main() — sky, sea, terrace, sun, headland, cliff/town,
clock tower, trees, staircase, balcony couple, sailboats, cafe terrace,
then vignette, border and the title block. The random seed is fixed so
the poster is reproducible byte for byte.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
OUT = "/home/hatch/workspace/poster-v4-build/poster.png"
random.seed(20261121)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"

# Town houses: x, y, w, h, wall colour, roof colour.
HOUSES = [
    (760, 430, 90, 70, (250, 240, 214), (178, 84, 52)),
    (860, 415, 80, 78, (246, 230, 198), (168, 76, 48)),
    (945, 430, 79, 64, (250, 238, 210), (178, 84, 52)),
    (720, 520, 100, 76, (248, 236, 208), (172, 80, 50)),
    (830, 505, 86, 84, (252, 242, 218), (180, 86, 54)),
    (925, 520, 99, 70, (246, 232, 200), (170, 78, 48)),
    (690, 620, 110, 80, (250, 238, 212), (176, 82, 52)),
    (810, 610, 96, 88, (248, 234, 204), (172, 80, 50)),
    (915, 625, 109, 74, (252, 240, 216), (178, 84, 52)),
]

# Clock-tower geometry (the one dominant landmark, v4).
TOWER = dict(x0=655, x1=735, top=340, bottom=660)

# Cypress trees: x, y, height. Bougainvillea clusters: x, y, radius.
CYPRESS = [(735, 470, 46), (905, 455, 52), (985, 470, 44), (700, 600, 40)]
FLOWER_CLUSTERS = [(700, 500, 26), (880, 470, 30), (990, 560, 28), (745, 640, 24)]
FLOWER_COLORS = [(214, 62, 110), (226, 92, 128), (198, 48, 96)]

SUN_CENTRE = (400, 520)


def lerp(a, b, t):
    """Blend two RGB colours by t in [0, 1]."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(img, y0, y1, stops):
    """Paint a vertical gradient between (pos 0..1, rgb) stops over y0..y1."""
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                tt = (t - p0) / max(1e-6, p1 - p0)
                d.line([(0, y), (W, y)], fill=lerp(c0, c1, tt))
                break


def text_spaced(d, cx, y, s, font, fill, spacing=6, shadow=None):
    """Draw centred text with even letter spacing and an optional shadow."""
    widths = [d.textlength(ch, font=font) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        if shadow:
            d.text((x + shadow[0], y + shadow[1]), ch, font=font, fill=shadow[2])
        d.text((x, y), ch, font=font, fill=fill)
        x += wch + spacing


def draw_sky(img):
    """Sky: deep blue at the top melting into orange and gold at the horizon."""
    vgrad(img, 0, 560, [
        (0.0, (22, 46, 88)),
        (0.35, (64, 84, 130)),
        (0.55, (226, 122, 62)),
        (0.75, (248, 178, 92)),
        (1.0, (252, 214, 150)),
    ])


def draw_sea(img):
    """Sea: warm sunlit band at the horizon cooling to teal below."""
    vgrad(img, 560, 800, [
        (0.0, (250, 196, 120)),
        (0.15, (56, 138, 150)),
        (0.6, (30, 104, 122)),
        (1.0, (22, 82, 100)),
    ])


def draw_terrace(img):
    """Terrace stone at the bottom of the poster."""
    vgrad(img, 800, 1024, [
        (0.0, (232, 196, 148)),
        (1.0, (198, 152, 104)),
    ])


def draw_sun(d):
    """Low sun with a soft halo, plus its glittering path on the sea."""
    cx, cy = SUN_CENTRE
    for r, a in [(190, 40), (150, 60), (115, 90)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 130, a))
    d.ellipse([cx - 78, cy - 78, cx + 78, cy + 78], fill=(255, 233, 168, 255))
    for i in range(26):
        y = 566 + i * 9
        wdt = 26 + i * 4 + random.randint(-8, 8)
        x0 = cx - wdt // 2 + random.randint(-14, 14)
        alpha = max(30, 200 - i * 6)
        d.rectangle([x0, y, x0 + wdt, y + 4], fill=(255, 214, 130, alpha))


def draw_headland(d):
    """Distant hazy headland on the right, behind the town."""
    d.polygon([(700, 560), (1024, 470), (1024, 560)], fill=(122, 74, 88, 200))
    d.polygon([(820, 560), (1024, 500), (1024, 560)], fill=(96, 58, 74, 220))


def draw_house(d, x, y, w, h, wall, roof):
    """One stacked town house: wall, pitched roof, lit windows, arch door."""
    d.rectangle([x, y, x + w, y + h], fill=wall)
    d.polygon([(x - 4, y), (x + w + 4, y), (x + w - 8, y - 16), (x + 8, y - 16)],
              fill=roof)
    for wx in range(x + 12, x + w - 12, 26):
        for wy in (y + 14, y + 42):
            if wy + 16 <= y + h:
                lit = random.random() < 0.55
                d.rectangle([wx, wy, wx + 12, wy + 16],
                            fill=(255, 214, 120, 255) if lit else (52, 44, 66, 255))
    d.rectangle([x + w // 2 - 8, y + h - 22, x + w // 2 + 8, y + h],
                fill=(72, 52, 60, 255))


def draw_cliff_and_town(d):
    """Cliff face on the right with the stacked houses on it."""
    d.polygon([(640, 800), (700, 470), (1024, 400), (1024, 800)],
              fill=(146, 84, 62, 255))
    d.polygon([(640, 800), (700, 470), (760, 470), (720, 800)],
              fill=(120, 66, 50, 255))
    for house in HOUSES:
        draw_house(d, *house)


def draw_clock_tower(d):
    """Golden clock tower — v4's one dominant landmark.

    Tower body in front of the cliff edge, left of the house rows; dome
    and spire on top; glowing gold-rimmed dial with hands at golden
    hour (~5:40); lit windows and an arched door below.
    """
    tx0, tx1 = TOWER["x0"], TOWER["x1"]
    ty_top, ty_bot = TOWER["top"], TOWER["bottom"]
    d.rectangle([tx0, ty_top + 40, tx1, ty_bot], fill=(244, 226, 188, 255))
    d.rectangle([tx0 - 4, ty_top + 34, tx1 + 4, ty_top + 46],
                fill=(196, 132, 72, 255))
    # dome + spire
    d.pieslice([tx0 - 2, ty_top - 26, tx1 + 2, ty_top + 44], 180, 360,
               fill=(178, 84, 52, 255))
    d.polygon([(tx0 + 34, ty_top - 24), (tx1 - 34, ty_top - 24),
               ((tx0 + tx1) // 2, ty_top - 52)], fill=(150, 66, 44, 255))
    d.ellipse([(tx0 + tx1) // 2 - 4, ty_top - 60, (tx0 + tx1) // 2 + 4,
               ty_top - 52], fill=(255, 214, 120, 255))
    # clock face: gold rim, pale dial, hour ticks, hands at ~5:40
    ccx, ccy, cr = (tx0 + tx1) // 2, ty_top + 96, 34
    d.ellipse([ccx - cr - 5, ccy - cr - 5, ccx + cr + 5, ccy + cr + 5],
              fill=(196, 132, 72, 255))
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr],
              fill=(255, 246, 224, 255))
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x0 = ccx + int((cr - 6) * math.sin(a))
        y0 = ccy - int((cr - 6) * math.cos(a))
        x1 = ccx + int((cr - 2) * math.sin(a))
        y1 = ccy - int((cr - 2) * math.cos(a))
        d.line([(x0, y0), (x1, y1)], fill=(90, 60, 40, 255), width=2)
    d.line([(ccx, ccy), (ccx + 12, ccy + 14)], fill=(52, 40, 36, 255), width=4)
    d.line([(ccx, ccy), (ccx + 4, ccy - 24)], fill=(52, 40, 36, 255), width=3)
    d.ellipse([ccx - 4, ccy - 4, ccx + 4, ccy + 4], fill=(178, 84, 52, 255))
    # lit tower windows + arched door
    for wy in (ty_top + 160, ty_top + 210, ty_top + 260):
        d.rectangle([ccx - 7, wy, ccx + 7, wy + 20], fill=(255, 214, 120, 255))
        d.rectangle([ccx - 7, wy, ccx + 7, wy + 20],
                    outline=(90, 60, 40, 255), width=1)
    d.rectangle([ccx - 10, ty_bot - 26, ccx + 10, ty_bot], fill=(72, 52, 60, 255))
    # soft shadow of the tower on the cliff, to the right
    d.polygon([(tx1, ty_top + 40), (tx1 + 46, ty_top + 90), (tx1 + 46, ty_bot),
               (tx1, ty_bot)], fill=(120, 66, 50, 90))


def draw_trees(d):
    """Cypress trees and bougainvillea clusters scattered over the cliff."""
    for (x, y, s) in CYPRESS:
        d.ellipse([x - s * 0.22, y - s, x + s * 0.22, y], fill=(34, 74, 52, 255))
        d.rectangle([x - 2, y - 4, x + 2, y + 6], fill=(74, 52, 38, 255))
    for (x, y, r) in FLOWER_CLUSTERS:
        for _ in range(26):
            px = x + random.randint(-r, r)
            py = y + random.randint(-r // 2, r // 2)
            d.ellipse([px - 4, py - 4, px + 4, py + 4],
                      fill=random.choice(FLOWER_COLORS))


def draw_staircase(d):
    """Grand staircase descending from the town to the harbour, with lanterns."""
    for i in range(12):
        y = 560 + i * 18
        x0 = 520 - i * 3
        x1 = 620 + i * 2
        d.rectangle([x0, y, x1, y + 11], fill=(240, 214, 164, 255))
        d.rectangle([x0, y + 11, x1, y + 14], fill=(176, 128, 84, 255))
    d.polygon([(520, 560), (500, 776), (520, 776), (538, 560)],
              fill=(214, 178, 128, 255))
    d.polygon([(620, 560), (640, 776), (620, 776), (604, 560)],
              fill=(214, 178, 128, 255))
    for (x, y) in [(506, 600), (520, 680), (634, 620), (624, 700)]:
        d.rectangle([x - 3, y - 12, x + 3, y + 12], fill=(52, 44, 58, 255))
        d.ellipse([x - 8, y - 24, x + 8, y - 8], fill=(255, 214, 120, 255))


def draw_balcony_couple(d):
    """Two people on a balcony of the house at (830, 505), above its floor."""
    d.rectangle([836, 566, 910, 574], fill=(226, 188, 138, 255))
    for bx in range(838, 910, 10):
        d.rectangle([bx, 548, bx + 3, 566], fill=(120, 88, 60, 255))
    d.rectangle([836, 544, 910, 548], fill=(120, 88, 60, 255))
    # person A (rust dress, leaning on the rail)
    d.ellipse([850, 524, 864, 538], fill=(52, 40, 36, 255))
    d.polygon([(848, 538), (866, 538), (868, 566), (846, 566)],
              fill=(178, 84, 52, 255))
    # person B (white shirt, arm on the rail)
    d.ellipse([884, 524, 898, 538], fill=(40, 32, 30, 255))
    d.polygon([(882, 538), (900, 538), (902, 566), (880, 566)],
              fill=(250, 244, 230, 255))


def draw_sailboat(d, cx, cy, s):
    """One sailboat with hull, mast, two sails and a soft reflection."""
    d.polygon([(cx - 34 * s, cy), (cx + 34 * s, cy), (cx + 22 * s, cy + 14 * s),
               (cx - 22 * s, cy + 14 * s)], fill=(72, 44, 40, 255))
    d.rectangle([cx - 2 * s, cy - 62 * s, cx + 2 * s, cy], fill=(52, 40, 36, 255))
    d.polygon([(cx + 4 * s, cy - 58 * s), (cx + 4 * s, cy - 4 * s),
               (cx + 40 * s, cy - 4 * s)], fill=(255, 246, 224, 255))
    d.polygon([(cx - 4 * s, cy - 48 * s), (cx - 4 * s, cy - 4 * s),
               (cx - 30 * s, cy - 4 * s)], fill=(250, 226, 188, 255))
    for i in range(4):
        d.rectangle([cx - 26 * s, cy + 18 * s + i * 6, cx + 26 * s,
                     cy + 21 * s + i * 6], fill=(255, 220, 150, 90 - i * 18))


def draw_sailboats(d):
    """Two sailboats out on the sea."""
    draw_sailboat(d, 250, 640, 1.0)
    draw_sailboat(d, 180, 720, 0.65)


def draw_potted_flowers(d, pot, fx, fy, count, spread_x, y_low, y_high, colors):
    """One terracotta pot overflowing with bougainvillea.

    pot: the four pot corners. Flowers scatter around (fx, fy) with
    horizontal spread spread_x and vertical offsets in [y_low, y_high],
    coloured from colors.
    """
    d.polygon(pot, fill=(172, 84, 52, 255))
    for _ in range(count):
        px = fx + random.randint(-spread_x, spread_x)
        py = fy + random.randint(y_low, y_high)
        d.ellipse([px - 5, py - 5, px + 5, py + 5],
                  fill=random.choice(colors))


def draw_cafe(d):
    """Cafe terrace foreground: balustrade, round table, two people, pots."""
    d.rectangle([0, 800, W, 818], fill=(226, 188, 138, 255))
    for x in range(30, W, 46):
        d.rectangle([x, 818, x + 14, 872], fill=(240, 214, 164, 255))
        d.ellipse([x - 2, 812, x + 16, 826], fill=(244, 222, 176, 255))
    d.rectangle([0, 872, W, 884], fill=(214, 172, 118, 255))
    # round table + pedestal
    d.ellipse([140, 912, 350, 940], fill=(255, 250, 236, 255))
    d.rectangle([236, 935, 244, 1000], fill=(120, 88, 60, 255))
    # person 1 (straw hat, rust dress)
    d.ellipse([176, 872, 212, 908], fill=(52, 40, 36, 255))
    d.ellipse([158, 884, 230, 902], fill=(232, 196, 120, 255))
    d.polygon([(168, 908), (220, 908), (232, 985), (156, 985)],
              fill=(178, 84, 52, 255))
    # person 2 (dark hair, white shirt)
    d.ellipse([262, 874, 296, 908], fill=(40, 32, 30, 255))
    d.polygon([(256, 908), (302, 908), (312, 985), (246, 985)],
              fill=(250, 244, 230, 255))
    # wine glasses on the table
    for gx in (196, 282):
        d.rectangle([gx, 890, gx + 10, 906], fill=(255, 240, 190, 230))
        d.rectangle([gx + 4, 906, gx + 6, 912], fill=(255, 240, 190, 230))
    # potted bougainvillea, right and left foreground
    draw_potted_flowers(d, [(880, 930), (950, 930), (940, 1000), (890, 1000)],
                        915, 900, 40, 46, -34, 10, FLOWER_COLORS)
    draw_potted_flowers(d, [(60, 930), (130, 930), (122, 1000), (68, 1000)],
                        95, 905, 26, 34, -28, 8,
                        [(214, 62, 110), (226, 92, 128)])


def draw_vignette(img):
    """Soft dark frame around the edges, then return a fresh draw handle."""
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], outline=(60, 30, 20, 70), width=26)
    return Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")


def draw_border(d):
    """Cream outer border with a thin inner rule."""
    d.rectangle([0, 0, W - 1, H - 1], outline=(250, 240, 214, 255), width=26)
    d.rectangle([34, 34, W - 35, H - 35], outline=(250, 240, 214, 160), width=2)


def draw_title(d):
    """Title block: big place name, subtitle, and the stay-promise line."""
    f_title = ImageFont.truetype(SERIF_B, 118)
    f_sub = ImageFont.truetype(SERIF, 36)
    try:
        f_stay = ImageFont.truetype(SERIF_I, 30)
    except OSError:
        f_stay = ImageFont.truetype(SERIF, 30)
    text_spaced(d, W // 2, 72, "AURMARA", f_title, (255, 246, 224, 255),
                spacing=10, shadow=(4, 5, (90, 40, 20, 160)))
    text_spaced(d, W // 2, 228, "THE HARBOUR OF GOLDEN STAIRS", f_sub,
                (255, 238, 205, 255), spacing=5, shadow=(2, 2, (90, 40, 20, 140)))
    text_spaced(d, W // 2, 282, "Stay a while — Rooms by the Harbour", f_stay,
                (255, 226, 170, 255), spacing=2, shadow=(2, 2, (90, 40, 20, 140)))


def main():
    """Paint the poster in order and save it."""
    img = Image.new("RGB", (W, H), (24, 48, 84))
    d = ImageDraw.Draw(img, "RGBA")
    draw_sky(img)
    draw_sea(img)
    draw_terrace(img)
    draw_sun(d)
    draw_headland(d)
    draw_cliff_and_town(d)
    draw_clock_tower(d)
    draw_trees(d)
    draw_staircase(d)
    draw_balcony_couple(d)
    draw_sailboats(d)
    draw_cafe(d)
    img = draw_vignette(img)
    d = ImageDraw.Draw(img, "RGBA")
    draw_border(d)
    draw_title(d)
    img.save(OUT, optimize=True)
    print("saved", OUT, img.size)
    print("bytes:", os.path.getsize(OUT))


if __name__ == "__main__":
    main()
