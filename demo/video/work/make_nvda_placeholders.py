import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (250, 248, 243)
INK = (26, 24, 22)
MUTED = (92, 87, 78)
ACCENT = (13, 92, 92)
WARN = (155, 34, 38)

REG = "/mnt/c/Windows/Fonts/segoeui.ttf"
BOLD = "/mnt/c/Windows/Fonts/segoeuib.ttf"
HERE = os.path.dirname(os.path.abspath(__file__))


def f(path, size):
    return ImageFont.truetype(path, size)


def card(path, eyebrow, caption_lines, note):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 300), eyebrow, font=f(BOLD, 34), fill=ACCENT, anchor="ma")
    y = 420
    for line in caption_lines:
        d.text((W // 2, y), line, font=f(BOLD, 56), fill=INK, anchor="ma")
        y += 80
    d.text((W // 2, H - 140), note, font=f(REG, 28), fill=WARN, anchor="ma")
    img.save(path)
    print("wrote", path)


card(
    os.path.join(HERE, "nvda_before.png"),
    "WHAT NVDA SAYS — BEFORE",
    ['"dollar p over rho g dollar',
     'plus dollar v caret 2 over 2g dollar..."'],
    "Placeholder: real NVDA recording not provided before the deadline.",
)

card(
    os.path.join(HERE, "nvda_after.png"),
    "WHAT NVDA SAYS — AFTER LEGIBLE",
    ['"p over rho g, plus,',
     'v squared over 2 g, plus z, equals H."'],
    "Placeholder: real NVDA recording not provided before the deadline.",
)
