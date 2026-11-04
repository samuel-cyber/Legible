"""Render the stats card and end card for the demo video with Pillow.

Static 1920x1080 PNGs, styled to match the web app (warm off-white, near-
black ink, deep teal accent). Numbers are copied verbatim from README.md.
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (250, 248, 243)
INK = (26, 24, 22)
MUTED = (92, 87, 78)
ACCENT = (13, 92, 92)
LINE = (227, 221, 208)
PANEL = (255, 255, 255)

FONT_DIR = "/mnt/c/Windows/Fonts"
REG = os.path.join(FONT_DIR, "segoeui.ttf")
BOLD = os.path.join(FONT_DIR, "segoeuib.ttf")
LIGHT = os.path.join(FONT_DIR, "segoeuisl.ttf")

OUT = os.path.dirname(os.path.abspath(__file__))


def f(path, size):
    return ImageFont.truetype(path, size)


def rrect(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


def center_text(draw, cx, y, text, font, fill, anchor="ma"):
    draw.text((cx, y), text, font=font, fill=fill, anchor=anchor)


def stats_card(path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    eyebrow_f = f(BOLD, 30)
    title_f = f(BOLD, 56)
    num_f = f(BOLD, 96)
    label_f = f(REG, 30)

    center_text(d, W // 2, 90, "LEGIBLE", eyebrow_f, ACCENT)
    center_text(d, W // 2, 150, "Results on real lecture notes", title_f, INK)

    stats = [
        ("152", "equations from real\nlecture notes"),
        ("0", "incorrect equations\npublished"),
        ("303 / 303", "injected test errors\ncaught"),
        ("3", "real Muse Spark\nmisreadings caught"),
        ("23.7%", "correct equations withheld\n(the trade-off)"),
    ]

    n = len(stats)
    margin = 90
    gap = 36
    tile_w = (W - 2 * margin - gap * (n - 1)) // n
    tile_h = 420
    top = 360

    for i, (num, label) in enumerate(stats):
        x0 = margin + i * (tile_w + gap)
        x1 = x0 + tile_w
        rrect(d, (x0, top, x1, top + tile_h), 24, fill=PANEL, outline=LINE, width=2)
        cx = (x0 + x1) // 2
        # shrink the number font a touch if it's wide (e.g. "303 / 303")
        nf = num_f if len(num) <= 5 else f(BOLD, 64)
        center_text(d, cx, top + 70, num, nf, ACCENT)
        ly = top + 230
        for line in label.split("\n"):
            center_text(d, cx, ly, line, label_f, MUTED)
            ly += 42

    center_text(d, W // 2, H - 90,
                "Every number here comes from an actual run of the code in this repository.",
                f(LIGHT, 28), MUTED)

    img.save(path)
    print("wrote", path)


def end_card(path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    tagline_f = f(BOLD, 64)
    sub_f = f(REG, 36)
    brand_f = f(BOLD, 40)

    center_text(d, W // 2, H // 2 - 170, "Legible", f(BOLD, 88), ACCENT)

    lines = ["When it can't verify an equation,", "it refuses to guess."]
    y = H // 2 - 40
    for line in lines:
        center_text(d, W // 2, y, line, tagline_f, INK)
        y += 84

    y += 40
    center_text(d, W // 2, y, "github.com/samuel-cyber/Legible", sub_f, ACCENT)
    y += 70
    center_text(d, W // 2, y, "Built with Meta Muse Spark", sub_f, MUTED)

    img.save(path)
    print("wrote", path)


if __name__ == "__main__":
    stats_card(os.path.join(OUT, "stats_card.png"))
    end_card(os.path.join(OUT, "end_card.png"))
