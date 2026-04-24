#!/usr/bin/env python3
"""Optimize artist photos for SNS sharing.

- Resizes images so the longest side is <= MAX_SIDE
- Re-saves JPGs at quality 85 (mozjpeg-ish) with progressive encoding
- Converts PNG -> JPG when no transparency is needed (keeps PNG if alpha is used meaningfully)
- Writes width/height into data/artists.json for each artist, to embed as og:image:width/height
"""

from __future__ import annotations

import json
import pathlib
import sys
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "artists.json"
PHOTO_DIR = ROOT / "assets" / "artists"
MAX_SIDE = 1600
JPEG_Q = 85
MAX_BYTES = 3 * 1024 * 1024  # 3MB cap; iterate quality down if exceeded


def has_meaningful_alpha(img: Image.Image) -> bool:
    if img.mode not in ("RGBA", "LA", "P"):
        return False
    if img.mode == "P":
        img = img.convert("RGBA")
    alpha = img.split()[-1]
    extrema = alpha.getextrema()
    return extrema[0] < 250  # any non-fully-opaque pixel => keep PNG


def save_jpeg(img: Image.Image, dst: pathlib.Path) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    q = JPEG_Q
    while True:
        img.save(dst, "JPEG", quality=q, optimize=True, progressive=True)
        if dst.stat().st_size <= MAX_BYTES or q <= 60:
            break
        q -= 5


def save_png(img: Image.Image, dst: pathlib.Path) -> None:
    img.save(dst, "PNG", optimize=True)


def process(src: pathlib.Path) -> tuple[str, int, int]:
    """Optimize image in-place (or convert to .jpg). Returns (final_filename, w, h)."""
    img = Image.open(src)
    # Apply EXIF orientation so the physical pixels match what viewers see.
    img = ImageOps.exif_transpose(img)

    # Resize if longest side exceeds limit
    w, h = img.size
    longest = max(w, h)
    if longest > MAX_SIDE:
        scale = MAX_SIDE / longest
        new_size = (round(w * scale), round(h * scale))
        img = img.resize(new_size, Image.LANCZOS)

    # Decide output format
    keep_png = src.suffix.lower() == ".png" and has_meaningful_alpha(img)
    if keep_png:
        save_png(img, src)
        final_name = src.name
    else:
        # If PNG without alpha, convert to .jpg (and remove original png)
        if src.suffix.lower() != ".jpg":
            jpg_path = src.with_suffix(".jpg")
            save_jpeg(img, jpg_path)
            if src != jpg_path and src.exists():
                src.unlink()
            final_name = jpg_path.name
        else:
            save_jpeg(img, src)
            final_name = src.name

    # Re-open to get final dimensions
    final_path = PHOTO_DIR / final_name
    with Image.open(final_path) as f:
        fw, fh = f.size
    return final_name, fw, fh


def main() -> int:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    changed = 0
    for a in data["artists"]:
        photo = a.get("photo")
        if not photo:
            continue
        src = PHOTO_DIR / photo
        if not src.exists():
            print(f"  [SKIP] {a['slug']}: file not found: {photo}", file=sys.stderr)
            continue
        before = src.stat().st_size
        final_name, w, h = process(src)
        final_path = PHOTO_DIR / final_name
        after = final_path.stat().st_size
        a["photo"] = final_name
        a["photo_width"] = w
        a["photo_height"] = h
        flag = "=" if final_name == photo else "→ " + final_name
        print(f"  {a['slug']:30s} {flag:28s} {before:>10,}B → {after:>10,}B  {w}x{h}")
        if before != after or final_name != photo:
            changed += 1

    DATA_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nOptimized {changed} photo(s). dims written to data/artists.json.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
