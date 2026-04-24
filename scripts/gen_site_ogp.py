#!/usr/bin/env python3
"""Generate a site-level OGP image (1200x630) for the home page.

Writes assets/ogp.jpg — a static poster used by SNS shares of the site root.
"""

from __future__ import annotations

import pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "assets" / "ogp.jpg"

W, H = 1200, 630
BG_TOP = (10, 16, 32)
BG_BOTTOM = (11, 19, 34)
ACCENT = (232, 182, 77)
FG = (242, 238, 227)
FG_MUTE = (185, 179, 163)


def gradient_background(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, BG_TOP)
    top = BG_TOP
    bottom = BG_BOTTOM
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            img.putpixel((x, y), (r, g, b))
    return img


def radial_glow(size: tuple[int, int], center: tuple[int, int], radius: int, color=(232, 182, 77), alpha=80) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(
        (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        fill=color + (alpha,),
    )
    return layer.filter(ImageFilter.GaussianBlur(radius // 3))


def load_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/meiryob.ttc" if bold else "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
        "C:/Windows/Fonts/YuGothB.ttc" if bold else "C:/Windows/Fonts/YuGothR.ttc",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for f in candidates:
        p = pathlib.Path(f)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def main() -> int:
    base = gradient_background((W, H)).convert("RGBA")

    # decorative glows
    base.alpha_composite(radial_glow((W, H), (W * 3 // 4, 120), 360, ACCENT, 110))
    base.alpha_composite(radial_glow((W, H), (120, H - 100), 300, (76, 163, 217), 70))
    base.alpha_composite(radial_glow((W, H), (W // 2, H + 200), 400, (217, 78, 78), 60))

    # grid pattern, subtle
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 80):
        gd.line([(x, 0), (x, H)], fill=(232, 182, 77, 20), width=1)
    for y in range(0, H, 80):
        gd.line([(0, y), (W, y)], fill=(232, 182, 77, 20), width=1)
    base.alpha_composite(grid)

    draw = ImageDraw.Draw(base)

    # Accent bar + eyebrow
    draw.rectangle((80, 94, 80 + 60, 96), fill=ACCENT + (255,))
    font_eye = load_font(22, bold=False)
    draw.text((160, 82), "HIBIYA FESTIVAL 2026 / MUSIC WEEKEND", font=font_eye, fill=ACCENT + (255,))

    # Main title
    font_title_big = load_font(170, bold=True)
    font_title_med = load_font(130, bold=True)
    draw.text((76, 150), "HIBIYA", font=font_title_big, fill=FG + (255,))
    draw.text((76 + 60, 310), "LIVE", font=font_title_med, fill=ACCENT + (255,))
    draw.text((76, 440), "FESTIVAL", font=font_title_big, fill=FG + (255,))

    # Right side meta
    x_right = 760
    y = 200
    font_label = load_font(20, bold=True)
    font_value = load_font(34, bold=True)
    font_sub = load_font(22, bold=False)

    # DATE
    draw.line([(x_right, y - 10), (x_right + 320, y - 10)], fill=ACCENT + (255,), width=1)
    draw.text((x_right, y + 6), "DATE", font=font_label, fill=ACCENT + (255,))
    draw.text((x_right, y + 38), "2026.05.16 SAT", font=font_value, fill=FG + (255,))
    draw.text((x_right, y + 82), "— 05.17 SUN", font=font_value, fill=FG + (255,))

    # VENUE
    y2 = y + 160
    draw.line([(x_right, y2 - 10), (x_right + 320, y2 - 10)], fill=ACCENT + (255,), width=1)
    draw.text((x_right, y2 + 6), "VENUE", font=font_label, fill=ACCENT + (255,))
    draw.text((x_right, y2 + 38), "日比谷ステップ広場", font=font_sub, fill=FG + (255,))
    draw.text((x_right, y2 + 68), "HIBIYA FOOD HALL", font=font_sub, fill=FG + (255,))
    draw.text((x_right, y2 + 98), "日比谷OKUROJI", font=font_sub, fill=FG + (255,))

    # FREE badge
    y3 = y2 + 180
    draw.rectangle((x_right, y3, x_right + 150, y3 + 44), outline=ACCENT + (255,), width=2)
    draw.text((x_right + 18, y3 + 8), "FREE ENTRY", font=font_label, fill=ACCENT + (255,))

    out = base.convert("RGB")
    out.save(OUT_PATH, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"OGP image written: {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes, {W}x{H})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
