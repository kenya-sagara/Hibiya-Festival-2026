#!/usr/bin/env python3
"""Generate PNG favicons from the brand mark.

Writes:
  - assets/favicon.png         (32x32, modern browsers / fallback)
  - assets/apple-touch-icon.png (180x180, iOS home screen)
"""

from __future__ import annotations

import pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

BG = (11, 19, 34)
ACCENT = (232, 182, 77)


def draw_h_mark(size: int, padded: bool = True) -> Image.Image:
    """Draw the brand 'H' mark on a dark rounded square."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = int(size * 0.18)
    # Rounded background
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=BG)

    # Subtle border
    border_pad = max(1, int(size * 0.07))
    draw.rounded_rectangle(
        (border_pad, border_pad, size - 1 - border_pad, size - 1 - border_pad),
        radius=max(1, radius - border_pad // 2),
        outline=ACCENT,
        width=max(1, size // 64),
    )

    # 'H' letterform: two vertical bars + crossbar
    if padded:
        v_pad = int(size * 0.22)
        h_inset = int(size * 0.22)
    else:
        v_pad = int(size * 0.18)
        h_inset = int(size * 0.18)

    bar_w = max(2, int(size * 0.10))
    left_x = h_inset
    right_x = size - h_inset - bar_w

    # Left vertical bar
    draw.rectangle((left_x, v_pad, left_x + bar_w, size - v_pad), fill=ACCENT)
    # Right vertical bar
    draw.rectangle((right_x, v_pad, right_x + bar_w, size - v_pad), fill=ACCENT)
    # Crossbar
    cross_y = size // 2 - bar_w // 2
    draw.rectangle((left_x, cross_y, right_x + bar_w, cross_y + bar_w), fill=ACCENT)

    return img


def main() -> int:
    # 32x32 favicon
    favicon = draw_h_mark(64).resize((32, 32), Image.LANCZOS)
    fav_path = ASSETS / "favicon.png"
    favicon.save(fav_path, "PNG", optimize=True)
    print(f"Wrote {fav_path} ({fav_path.stat().st_size:,} bytes, 32x32)")

    # 180x180 apple-touch-icon
    apple = draw_h_mark(360).resize((180, 180), Image.LANCZOS)
    apple_path = ASSETS / "apple-touch-icon.png"
    apple.save(apple_path, "PNG", optimize=True)
    print(f"Wrote {apple_path} ({apple_path.stat().st_size:,} bytes, 180x180)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
