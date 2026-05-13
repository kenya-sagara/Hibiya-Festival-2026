#!/usr/bin/env python3
"""Generate per-venue PDF posters for HIBIYA LIVE FESTIVAL 2026.

Output (CMYK, 3 mm bleed, no crop marks):
  - assets/posters/poster-step-hiroba.pdf  (B1: 728 x 1030 mm)
  - assets/posters/poster-food-hall.pdf    (B1: 728 x 1030 mm)
  - assets/posters/poster-okuroji.pdf      (A1: 594 x 841 mm)

Each poster:
  - Festival logotype block (HIBIYA / LIVE / FESTIVAL stacked)
  - Date strip
  - Venue name (large)
  - That venue's timetable (Day 1 / Day 2)
  - QR code -> https://hibiya-festival.artistmerge.jp/
  - FREE ENTRY badge + organizer credits

All colors are CMYK. The QR code is drawn as vector rectangles (K only) so
it stays crisp at any print size and prints with single-channel black.
"""

from __future__ import annotations

import json
import pathlib
from collections import defaultdict
from typing import Iterable

import qrcode
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "artists.json"
OUT_DIR = ROOT / "assets" / "posters"

SITE_URL = "https://hibiya-festival.artistmerge.jp/"
BLEED = 3 * mm
MARGIN = 30 * mm  # safe area inside trim

# CMYK theme palettes. The "dark" theme matches the website (navy + gold,
# cream text). The "white" theme inverts to a paper-white background with
# deep navy text, useful for high-light venues where dark posters wash out.
# All values are within Japan Color 2001 Coated gamut.
THEMES = {
    "dark": {
        "BG":      colors.CMYKColor(0.95, 0.85, 0.40, 0.65),  # very-dark navy
        "ACCENT":  colors.CMYKColor(0.05, 0.30, 0.85, 0.00),  # warm gold
        "FG":      colors.CMYKColor(0.00, 0.02, 0.10, 0.05),  # paper-warm cream
        "FG_MUTE": colors.CMYKColor(0.10, 0.12, 0.25, 0.35),  # muted beige
    },
    "white": {
        "BG":      colors.CMYKColor(0.00, 0.02, 0.06, 0.00),  # warm paper white
        "ACCENT":  colors.CMYKColor(0.10, 0.55, 1.00, 0.10),  # deep amber gold
        "FG":      colors.CMYKColor(0.95, 0.85, 0.40, 0.75),  # very-dark navy text
        "FG_MUTE": colors.CMYKColor(0.55, 0.50, 0.40, 0.30),  # muted brown-grey
    },
}
K_BLACK = colors.CMYKColor(0, 0, 0, 1)  # pure K for QR
WHITE = colors.CMYKColor(0, 0, 0, 0)

# Sheet sizes (trim, mm, portrait)
SIZES = {
    "B1": (728, 1030),
    "A1": (594, 841),
}

VENUES = [
    {
        "slug": "step-hiroba",
        "name": "日比谷ステップ広場",
        "subname": "特設ステージ",
        "size": "B1",
        "schedule_key": "日比谷ステップ広場",
        "note": "雨天開催・荒天中止",
    },
    {
        "slug": "food-hall",
        "name": "HIBIYA FOOD HALL",
        "subname": "東京ミッドタウン日比谷 B1F",
        "size": "B1",
        "schedule_key": "HIBIYA FOOD HALL",
        "note": "",
    },
    {
        "slug": "okuroji",
        "name": "日比谷OKUROJI",
        "subname": "HIBIYA OKUROJI",
        "size": "A1",
        "schedule_key": "日比谷OKUROJI",
        "note": "",
    },
]

# Font registration: prefer Yu Gothic / Yu Mincho / Impact on Windows; fall
# back gracefully. JP-NAME uses Mincho (serif) for the performer line — gives
# the schedule a refined jazz-poster feel rather than utilitarian Gothic.
FONT_CANDIDATES = {
    "JP-B": [
        ("C:/Windows/Fonts/YuGothB.ttc", 0),
        ("C:/Windows/Fonts/meiryob.ttc", 0),
        ("C:/Windows/Fonts/msgothic.ttc", 0),
    ],
    "JP-R": [
        ("C:/Windows/Fonts/YuGothR.ttc", 0),
        ("C:/Windows/Fonts/meiryo.ttc", 0),
        ("C:/Windows/Fonts/msgothic.ttc", 0),
    ],
    "JP-NAME": [
        ("C:/Windows/Fonts/YuMinDB.ttc", 0),  # Yu Mincho Demibold
        ("C:/Windows/Fonts/YuMinB.ttc", 0),   # Yu Mincho Bold (older)
        ("C:/Windows/Fonts/yumin.ttf", 0),
        ("C:/Windows/Fonts/msmincho.ttc", 0),
        ("C:/Windows/Fonts/YuGothB.ttc", 0),  # fallback to gothic
    ],
    "LAT-B": [
        ("C:/Windows/Fonts/impact.ttf", 0),
        ("C:/Windows/Fonts/ariblk.ttf", 0),
        ("C:/Windows/Fonts/arialbd.ttf", 0),
    ],
    "LAT-NAME": [
        ("C:/Windows/Fonts/timesbi.ttf", 0),    # Times Bold Italic — jazz feel
        ("C:/Windows/Fonts/cambriai.ttf", 0),
        ("C:/Windows/Fonts/constanbi.ttf", 0),
        ("C:/Windows/Fonts/arialbi.ttf", 0),
    ],
    "LAT-R": [
        ("C:/Windows/Fonts/arial.ttf", 0),
        ("C:/Windows/Fonts/segoeui.ttf", 0),
    ],
}


def register_fonts() -> dict[str, str]:
    resolved: dict[str, str] = {}
    for name, candidates in FONT_CANDIDATES.items():
        for path, idx in candidates:
            p = pathlib.Path(path)
            if not p.exists():
                continue
            try:
                pdfmetrics.registerFont(TTFont(name, str(p), subfontIndex=idx))
                resolved[name] = name
                break
            except Exception:
                continue
        if name not in resolved:
            # ReportLab built-in fallback (Latin only)
            resolved[name] = "Helvetica-Bold" if "B" in name else "Helvetica"
    return resolved


def load_schedule() -> dict[str, list[dict]]:
    data = json.load(open(DATA, encoding="utf-8"))
    by_venue: dict[str, list[dict]] = defaultdict(list)
    for a in data["artists"]:
        for s in a["slots"]:
            by_venue[s["venue"]].append({
                "day": s["day"],
                "time": s["time"],
                "end": s["end"],
                "name": a["name"],
            })
    for v in by_venue:
        by_venue[v].sort(key=lambda x: (x["day"], x["time"]))
    return by_venue


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def fit_size(c: canvas.Canvas, text: str, font: str, target_w: float, base: float = 100.0) -> float:
    """Return the font size (pt) that makes `text` exactly `target_w` wide."""
    w = c.stringWidth(text, font, base)
    if w <= 0:
        return base
    return base * target_w / w


def draw_qr(c: canvas.Canvas, x: float, y: float, size: float, url: str) -> None:
    """Vector-draw a QR code as K-only black squares on a white quiet zone."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    n = len(matrix)
    quiet = 4  # modules (standard QR quiet zone)
    cell = size / (n + quiet * 2)

    # White background incl. quiet zone
    c.setFillColor(WHITE)
    c.rect(x, y, size, size, stroke=0, fill=1)

    # Black modules (offset by quiet zone)
    c.setFillColor(K_BLACK)
    ox = x + quiet * cell
    oy = y + quiet * cell
    overlap = 0.05  # tiny overlap to avoid hairline gaps in some viewers
    for ry, row in enumerate(matrix):
        for rx, on in enumerate(row):
            if not on:
                continue
            px = ox + rx * cell
            py = oy + size - 2 * quiet * cell - (ry + 1) * cell
            c.rect(px, py, cell + overlap, cell + overlap, stroke=0, fill=1)


def draw_centered(c: canvas.Canvas, text: str, font: str, size: float, cx: float, y: float) -> None:
    w = c.stringWidth(text, font, size)
    c.setFont(font, size)
    c.drawString(cx - w / 2, y, text)


def _runs(text: str) -> Iterable[tuple[bool, str]]:
    """Yield (is_ascii, run) tuples — adjacent same-script characters merged."""
    if not text:
        return
    cur_ascii = ord(text[0]) < 128
    buf = [text[0]]
    for ch in text[1:]:
        is_ascii = ord(ch) < 128
        if is_ascii == cur_ascii:
            buf.append(ch)
        else:
            yield cur_ascii, "".join(buf)
            cur_ascii = is_ascii
            buf = [ch]
    yield cur_ascii, "".join(buf)


def mixed_width(c: canvas.Canvas, text: str, lat_font: str, jp_font: str, size: float) -> float:
    """Width of `text` rendered with `lat_font` for ASCII and `jp_font` for the rest."""
    return sum(c.stringWidth(s, lat_font if a else jp_font, size) for a, s in _runs(text))


def draw_mixed(c: canvas.Canvas, x: float, y: float, text: str,
               lat_font: str, jp_font: str, size: float) -> float:
    """Draw `text` with `lat_font` for ASCII chars, `jp_font` otherwise. Returns width drawn."""
    cur_x = x
    for is_ascii, run in _runs(text):
        font = lat_font if is_ascii else jp_font
        c.setFont(font, size)
        c.drawString(cur_x, y, run)
        cur_x += c.stringWidth(run, font, size)
    return cur_x - x


# ---------------------------------------------------------------------------
# Poster layout
# ---------------------------------------------------------------------------

def draw_poster(venue: dict, schedule: list[dict], fonts: dict[str, str],
                theme: str = "dark") -> pathlib.Path:
    sheet_w_mm, sheet_h_mm = SIZES[venue["size"]]
    sheet_w = sheet_w_mm * mm
    sheet_h = sheet_h_mm * mm
    page_w = sheet_w + 2 * BLEED
    page_h = sheet_h + 2 * BLEED

    # The "white" theme is the chosen design and gets the default filename;
    # any other theme is suffixed (e.g. -dark) so variants don't collide.
    suffix = "" if theme == "white" else f"-{theme}"
    out_path = OUT_DIR / f"poster-{venue['slug']}{suffix}.pdf"
    c = canvas.Canvas(str(out_path), pagesize=(page_w, page_h))
    c.setTitle(f"HIBIYA LIVE FESTIVAL 2026 — {venue['name']}")
    c.setAuthor("HIBIYA LIVE FESTIVAL 2026")
    c.setSubject("A1/B1 venue poster")

    palette = THEMES[theme]
    BG = palette["BG"]
    ACCENT = palette["ACCENT"]
    FG = palette["FG"]
    FG_MUTE = palette["FG_MUTE"]

    JP_B = fonts["JP-B"]
    JP_R = fonts["JP-R"]
    JP_NAME = fonts.get("JP-NAME", JP_B)
    LAT_B = fonts["LAT-B"]
    LAT_NAME = fonts.get("LAT-NAME", LAT_B)
    LAT_R = fonts["LAT-R"]

    # ---- Background (extends to bleed) -------------------------------------
    c.setFillColor(BG)
    c.rect(0, 0, page_w, page_h, stroke=0, fill=1)

    # Subtle accent vertical bar on the left edge of safe area
    bar_x = BLEED + MARGIN
    c.setFillColor(ACCENT)
    c.rect(bar_x, BLEED + MARGIN, 6 * mm, sheet_h - 2 * MARGIN, stroke=0, fill=1)

    # Inner safe area
    safe_x = BLEED + MARGIN + 18 * mm  # leave room for the bar
    safe_y0 = BLEED + MARGIN
    safe_w = sheet_w - 2 * MARGIN - 18 * mm
    safe_top = BLEED + sheet_h - MARGIN

    # ---- Eyebrow -----------------------------------------------------------
    eyebrow = "HIBIYA FESTIVAL 2026 / MUSIC WEEKEND"
    eb_size = (sheet_w_mm / 728) * 18
    c.setFont(LAT_R, eb_size)
    c.setFillColor(ACCENT)
    c.drawString(safe_x, safe_top - eb_size * 1.2, eyebrow)

    # ---- Logotype (HIBIYA / LIVE / FESTIVAL) -------------------------------
    # Auto-fit: "FESTIVAL" is the widest; use it to set the main size so the
    # logotype block sits flush left and never overflows the safe area.
    # Kept compact so the timetable + large QR get most of the canvas.
    title_target_w = safe_w * 0.45
    main_size = fit_size(c, "FESTIVAL", LAT_B, title_target_w)
    sub_size = main_size * 0.70  # "LIVE"

    line_h_main = main_size * 0.78
    line_h_sub = sub_size * 0.78
    block_top = safe_top - eb_size * 2.4
    line1_y = block_top - line_h_main
    line2_y = line1_y - line_h_sub - main_size * 0.02
    line3_y = line2_y - line_h_main - sub_size * 0.02

    c.setFont(LAT_B, main_size)
    c.setFillColor(FG)
    c.drawString(safe_x, line1_y, "HIBIYA")

    c.setFont(LAT_B, sub_size)
    c.setFillColor(ACCENT)
    c.drawString(safe_x, line2_y, "LIVE")

    c.setFont(LAT_B, main_size)
    c.setFillColor(FG)
    c.drawString(safe_x, line3_y, "FESTIVAL")

    block_bottom = line3_y - main_size * 0.05

    # ---- Date strip --------------------------------------------------------
    rule_y = block_bottom - 18 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.line(safe_x, rule_y, safe_x + safe_w, rule_y)

    label_size = (sheet_w_mm / 728) * 22
    c.setFont(LAT_R, label_size)
    c.setFillColor(ACCENT)
    c.drawString(safe_x, rule_y - label_size * 1.2, "DATE")

    date_size = (sheet_w_mm / 728) * 64
    c.setFont(LAT_B, date_size)
    c.setFillColor(FG)
    date_y = rule_y - label_size * 1.4 - date_size
    c.drawString(safe_x, date_y, "2026.05.16 SAT — 05.17 SUN")

    # ---- VENUE block -------------------------------------------------------
    venue_top = date_y - 18 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.line(safe_x, venue_top, safe_x + safe_w, venue_top)
    c.setFont(LAT_R, label_size)
    c.setFillColor(ACCENT)
    c.drawString(safe_x, venue_top - label_size * 1.2, "VENUE")

    venue_size = fit_size(c, venue["name"], JP_B, safe_w * 0.92)
    venue_size = min(venue_size, (sheet_w_mm / 728) * 120)
    c.setFont(JP_B, venue_size)
    c.setFillColor(FG)
    venue_y = venue_top - label_size * 1.4 - venue_size
    c.drawString(safe_x, venue_y, venue["name"])

    sub_size_v = (sheet_w_mm / 728) * 26
    c.setFont(JP_R, sub_size_v)
    c.setFillColor(FG_MUTE)
    venue_sub_y = venue_y - sub_size_v * 1.4
    c.drawString(safe_x, venue_sub_y, venue["subname"])

    venue_block_bottom = venue_sub_y
    if venue["note"]:
        note_size = (sheet_w_mm / 728) * 22
        c.setFont(JP_R, note_size)
        c.setFillColor(FG_MUTE)
        venue_block_bottom = venue_sub_y - note_size * 1.6
        c.drawString(safe_x, venue_block_bottom, "※ " + venue["note"])

    # ---- Timetable ---------------------------------------------------------
    # Reserve footer area first so the timetable can be auto-fit to the
    # remaining vertical space — no overflow into the QR / credits.
    footer_h = 210 * mm if venue["size"] == "B1" else 165 * mm
    footer_y = BLEED + MARGIN
    footer_top = footer_y + footer_h

    tt_top = venue_block_bottom - 22 * mm

    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.line(safe_x, tt_top, safe_x + safe_w, tt_top)
    c.setFont(LAT_R, label_size)
    c.setFillColor(ACCENT)
    c.drawString(safe_x, tt_top - label_size * 1.2, "TIMETABLE")

    # Group by day (5.16 SAT precedes 5.17 SUN by lexical sort)
    by_day: dict[str, list[dict]] = defaultdict(list)
    for s in schedule:
        by_day[s["day"]].append(s)
    days = sorted(by_day.keys())
    n_days = len(days)
    n_rows = sum(len(v) for v in by_day.values())

    # Target sizes (will scale down if the schedule won't fit)
    target_day = (sheet_w_mm / 728) * 64
    target_time = (sheet_w_mm / 728) * 46
    target_gap = (sheet_w_mm / 728) * 10

    # Natural required height = day headers + rows + per-day gaps
    natural_h = (
        n_days * (target_day * 1.2)
        + n_rows * (target_time + target_gap)
        + max(0, n_days - 1) * (target_gap * 2)
    )
    available_h = (tt_top - label_size * 1.4 - 8 * mm) - footer_top - 12 * mm
    # Allow modest scale-up to fill the allotted area for impact at A0/A1/B1
    # print sizes, but cap it so longer schedules still look balanced.
    raw_scale = available_h / natural_h if natural_h > 0 else 1.0
    scale = max(0.55, min(1.4, raw_scale))

    day_size = target_day * scale
    time_size = target_time * scale
    name_size = time_size * 0.88
    row_gap = target_gap * scale

    cursor_y = tt_top - label_size * 1.4 - 8 * mm
    time_col_w = c.stringWidth("00:00–00:00", LAT_B, time_size) + 12 * mm

    for di, day in enumerate(days):
        c.setFont(LAT_B, day_size)
        c.setFillColor(ACCENT)
        c.drawString(safe_x, cursor_y - day_size, day)
        cursor_y -= day_size * 1.2

        for slot in by_day[day]:
            time_str = f"{slot['time']}–{slot['end']}"
            c.setFont(LAT_B, time_size)
            c.setFillColor(FG)
            c.drawString(safe_x, cursor_y - time_size, time_str)

            # Performer name — italic serif (Latin) + Mincho (Japanese) for a
            # refined jazz-poster feel, with auto-shrink to safe width.
            name_x = safe_x + time_col_w
            name_max = safe_w - time_col_w
            name_actual = name_size
            while (mixed_width(c, slot["name"], LAT_NAME, JP_NAME, name_actual)
                   > name_max and name_actual > 10):
                name_actual -= 1
            c.setFillColor(FG)
            baseline_offset = (time_size - name_actual) * 0.10
            draw_mixed(c, name_x, cursor_y - time_size + baseline_offset,
                       slot["name"], LAT_NAME, JP_NAME, name_actual)
            cursor_y -= time_size + row_gap

        if di < n_days - 1:
            cursor_y -= row_gap * 2  # gap between days

    # ---- Footer: QR (large) + FREE badge + credits ------------------------
    # Top rule of footer
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.line(safe_x, footer_top, safe_x + safe_w, footer_top)

    # QR (right side) — large for scannability from a distance
    qr_size = 185 * mm if venue["size"] == "B1" else 145 * mm
    qr_x = BLEED + sheet_w - MARGIN - qr_size
    qr_y = footer_y + 4 * mm
    draw_qr(c, qr_x, qr_y, qr_size, SITE_URL)

    # QR captions (above QR, inside footer band)
    qr_caption_jp_size = (sheet_w_mm / 728) * 22
    qr_caption_en_size = (sheet_w_mm / 728) * 16
    c.setFont(JP_R, qr_caption_jp_size)
    c.setFillColor(FG)
    c.drawString(qr_x, qr_y + qr_size + 8 * mm, "出演詳細・最新情報はこちら")
    c.setFont(LAT_R, qr_caption_en_size)
    c.setFillColor(ACCENT)
    c.drawString(qr_x, qr_y + qr_size + 8 * mm + qr_caption_jp_size * 1.3,
                 "SCAN FOR DETAILS")
    url_size = (sheet_w_mm / 728) * 14
    c.setFont(LAT_R, url_size)
    c.setFillColor(FG_MUTE)
    c.drawString(qr_x, qr_y - url_size * 1.4, "hibiya-festival.artistmerge.jp")

    # Left column: FREE ENTRY badge + credits stacked beneath
    left_w = qr_x - safe_x - 16 * mm

    badge_w = min(left_w, (sheet_w_mm / 728) * 260)
    badge_h = (sheet_w_mm / 728) * 80
    badge_x = safe_x
    badge_y = footer_top - 16 * mm - badge_h
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2.5)
    c.rect(badge_x, badge_y, badge_w, badge_h, stroke=1, fill=0)
    free_size = badge_h * 0.55
    c.setFont(LAT_B, free_size)
    c.setFillColor(ACCENT)
    free_w = c.stringWidth("FREE ENTRY", LAT_B, free_size)
    c.drawString(badge_x + (badge_w - free_w) / 2,
                 badge_y + (badge_h - free_size) / 2 + free_size * 0.15,
                 "FREE ENTRY")
    free_jp_size = (sheet_w_mm / 728) * 18
    c.setFont(JP_R, free_jp_size)
    c.setFillColor(FG_MUTE)
    c.drawString(badge_x, badge_y - free_jp_size * 1.4, "入場無料 / 出入り自由")

    # Credits (compact, single line each, bottom-anchored to footer floor)
    credits = [
        ("主催", "一般社団法人 日比谷エリアマネジメント／東京ミッドタウン日比谷"),
        ("協力", "日比谷OKUROJI"),
        ("総合企画", "HIBIYA LIVE FESTIVAL"),
        ("事務局", "アーティストマージ"),
        ("運営", "ニシヘヒガシヘ"),
    ]
    cred_size = (sheet_w_mm / 728) * 13
    cred_label_w = cred_size * 5.2
    cred_y = footer_y
    for label, val in reversed(credits):
        c.setFont(JP_R, cred_size)
        c.setFillColor(ACCENT)
        c.drawString(safe_x, cred_y, label)
        c.setFillColor(FG_MUTE)
        c.drawString(safe_x + cred_label_w, cred_y, val)
        cred_y += cred_size * 1.6

    c.showPage()
    c.save()
    return out_path


def main(argv: list[str] | None = None) -> int:
    import sys
    argv = list(argv if argv is not None else sys.argv[1:])

    # CLI: [venue_slug] [theme]
    # venue_slug: one of the VENUES slugs, or "all" / omitted
    # theme: "white" (default — chosen design), "dark", or "both"
    only = None
    theme_arg = "white"
    if argv:
        a0 = argv[0]
        if a0 in ("dark", "white", "both"):
            theme_arg = a0
        else:
            only = None if a0 == "all" else a0
    if len(argv) >= 2:
        theme_arg = argv[1]

    themes = ["dark", "white"] if theme_arg == "both" else [theme_arg]
    if any(t not in THEMES for t in themes):
        print(f"unknown theme: {theme_arg!r} (choose from: dark, white, both)")
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fonts = register_fonts()
    schedule = load_schedule()

    targets = [v for v in VENUES if (only is None or v["slug"] == only)]
    if not targets:
        print(f"unknown venue slug: {only!r} (choose from: {[v['slug'] for v in VENUES]})")
        return 2

    for venue in targets:
        slots = schedule.get(venue["schedule_key"], [])
        for theme in themes:
            path = draw_poster(venue, slots, fonts, theme=theme)
            size_kb = path.stat().st_size // 1024
            sw, sh = SIZES[venue["size"]]
            print(f"  wrote {path.relative_to(ROOT)}  "
                  f"({venue['size']}: {sw}x{sh} mm + 3mm bleed, theme={theme}, {size_kb} KB)")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
