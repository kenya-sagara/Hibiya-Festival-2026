#!/usr/bin/env python3
"""Build per-artist HTML pages from data/artists.json.

Usage:
  python scripts/build.py [--site-url https://example.com]

Reads data/artists.json and writes:
  - artists/<slug>.html : per-artist pages (OGP / Twitter Card / JSON-LD)
  - sitemap.xml         : sitemap for search engines
  - index.html          : injects SSR'd artist grid + JSON-LD MusicEvent
"""

from __future__ import annotations

import argparse
import datetime as dt
import html as html_escape
import json
import pathlib
import re
import sys
import urllib.parse as up

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "artists.json"
OUT_DIR = ROOT / "artists"
INDEX_PATH = ROOT / "index.html"
SITEMAP_PATH = ROOT / "sitemap.xml"
PHOTO_DIR_WEB = "assets/artists"  # relative to site root
MAX_OG_DESC = 180  # characters

# Festival schedule (used for JSON-LD MusicEvent and sitemap lastmod)
EVENT_START_DATE = "2026-05-16"
EVENT_END_DATE = "2026-05-17"

# Parent event (umbrella program that this site's edition belongs to)
PARENT_EVENT_NAME = "HIBIYA LIVE FESTIVAL"
PARENT_EVENT_URL = "https://www.hibiya.tokyo-midtown.com/hibiya-live-festival/"

# Venues (single source of truth — kept in sync with assets/js/main.js)
VENUES = {
    "日比谷ステップ広場": {
        "name": "日比谷ステップ広場 特設ステージ",
        "address": "東京都千代田区有楽町1-1-2",
        "lat": 35.673798,
        "lng": 139.760017,
    },
    "HIBIYA FOOD HALL": {
        "name": "HIBIYA FOOD HALL（東京ミッドタウン日比谷 B1F）",
        "address": "東京都千代田区有楽町1-1-2 東京ミッドタウン日比谷 B1F",
        "lat": 35.674044,
        "lng": 139.759613,
    },
    "日比谷OKUROJI": {
        "name": "日比谷OKUROJI",
        "address": "東京都千代田区内幸町1-7",
        "lat": 35.671306,
        "lng": 139.759593,
    },
}


def esc(s: str) -> str:
    return html_escape.escape(s or "", quote=True)


def trim_desc(desc: str, limit: int = MAX_OG_DESC) -> str:
    if not desc:
        return "2026.5.16 SAT – 5.17 SUN ｜ HIBIYA LIVE FESTIVAL 2026"
    desc = re.sub(r"\s+", " ", desc).strip()
    if len(desc) <= limit:
        return desc
    return desc[: limit - 1] + "…"


def slot_summary(slots: list[dict]) -> str:
    return " / ".join(f"{s['day']} {s['time']} @ {s['venue']}" for s in slots)


def slot_iso_datetime(day: str, time_str: str) -> str:
    """Convert '5.16 SAT' + '13:00' -> '2026-05-16T13:00:00+09:00'."""
    m = re.match(r"\s*(\d{1,2})\.(\d{1,2})", day)
    if not m:
        return ""
    month = int(m.group(1))
    date = int(m.group(2))
    hh, mm = (time_str.split(":") + ["00"])[:2]
    return f"2026-{month:02d}-{date:02d}T{int(hh):02d}:{int(mm):02d}:00+09:00"


def build_photo_html(photo: str | None, name: str, web_root: str) -> str:
    if photo:
        src = f"{web_root}/{PHOTO_DIR_WEB}/{photo}"
        return (
            f'<figure class="artist-hero__photo">'
            f'<img src="{esc(src)}" alt="{esc(name)}" />'
            f"</figure>"
        )
    return (
        '<figure class="artist-hero__photo artist-hero__photo--placeholder">'
        '<span>COMING SOON</span>'
        "</figure>"
    )


def build_slots_html(slots: list[dict]) -> str:
    rows = []
    for s in slots:
        rows.append(
            f'<li class="slot">'
            f'<span class="slot__day">{esc(s["day"])}</span>'
            f'<span class="slot__time">{esc(s["time"])} – {esc(s.get("end", ""))}</span>'
            f'<span class="slot__venue">{esc(s["venue"])}</span>'
            f"</li>"
        )
    return "\n".join(rows)


def build_share_urls(page_url: str, text: str) -> dict:
    enc_url = up.quote(page_url, safe="")
    enc_text = up.quote(text, safe="")
    return {
        "x": f"https://twitter.com/intent/tweet?text={enc_text}&url={enc_url}",
        "line": f"https://social-plugins.line.me/lineit/share?url={enc_url}&text={enc_text}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={enc_url}",
    }


def build_nav(prev_artist, next_artist) -> str:
    parts = []
    if prev_artist:
        parts.append(
            f'<a class="artist-pager__prev" href="{esc(prev_artist["slug"])}.html">'
            f'<span class="artist-pager__label">PREV</span>'
            f'<span class="artist-pager__name">{esc(prev_artist["name"])}</span>'
            f"</a>"
        )
    else:
        parts.append('<span class="artist-pager__prev artist-pager__prev--disabled"></span>')

    parts.append(
        '<a class="artist-pager__back" href="../index.html#artists">'
        "出演者一覧へ"
        "</a>"
    )

    if next_artist:
        parts.append(
            f'<a class="artist-pager__next" href="{esc(next_artist["slug"])}.html">'
            f'<span class="artist-pager__label">NEXT</span>'
            f'<span class="artist-pager__name">{esc(next_artist["name"])}</span>'
            f"</a>"
        )
    else:
        parts.append('<span class="artist-pager__next artist-pager__next--disabled"></span>')

    return "\n".join(parts)


def build_event_subevent(artist: dict, slot: dict, site_url: str, site_name: str) -> dict:
    """Build a sub-event MusicEvent dict for one performance slot."""
    venue_info = VENUES.get(slot["venue"], {"name": slot["venue"], "address": ""})
    start_iso = slot_iso_datetime(slot["day"], slot["time"])
    end_time = slot.get("end") or ""
    end_iso = slot_iso_datetime(slot["day"], end_time) if end_time else ""

    sub = {
        "@type": "MusicEvent",
        "name": f"{artist['name']} @ {slot['venue']}",
        "startDate": start_iso,
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {
            "@type": "Place",
            "name": venue_info["name"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": venue_info.get("address", ""),
                "addressLocality": "千代田区",
                "addressRegion": "東京都",
                "addressCountry": "JP",
            },
        },
        "performer": {
            "@type": "MusicGroup",
            "name": artist["name"],
            "url": f"{site_url}/artists/{artist['slug']}.html",
        },
        "organizer": {
            "@type": "Organization",
            "name": "一般社団法人 日比谷エリアマネジメント",
        },
        "isAccessibleForFree": True,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "JPY",
            "availability": "https://schema.org/InStock",
            "url": site_url + "/",
        },
        "superEvent": {
            "@type": "MusicEvent",
            "name": site_name,
            "url": site_url + "/",
        },
    }
    if end_iso:
        sub["endDate"] = end_iso
    if "lat" in venue_info:
        sub["location"]["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": venue_info["lat"],
            "longitude": venue_info["lng"],
        }
    return sub


def build_event_jsonld(artists: list[dict], site_url: str, site_name: str, site_desc: str) -> str:
    """Build the top-page JSON-LD MusicEvent (with sub-events per performance)."""
    sub_events = []
    for a in artists:
        for s in a["slots"]:
            sub_events.append(build_event_subevent(a, s, site_url, site_name))

    # Distinct venues for the umbrella location
    venue_objs = []
    for v_key, v in VENUES.items():
        venue_objs.append({
            "@type": "Place",
            "name": v["name"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": v.get("address", ""),
                "addressLocality": "千代田区",
                "addressRegion": "東京都",
                "addressCountry": "JP",
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": v["lat"],
                "longitude": v["lng"],
            },
        })

    main_event = {
        "@context": "https://schema.org",
        "@type": "MusicEvent",
        "name": site_name,
        "alternateName": "Hibiya Festival 2026 MUSIC WEEKEND",
        "description": site_desc,
        "startDate": f"{EVENT_START_DATE}T12:00:00+09:00",
        "endDate": f"{EVENT_END_DATE}T21:00:00+09:00",
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "url": site_url + "/",
        "image": [f"{site_url}/assets/ogp.jpg"],
        "location": venue_objs,
        "organizer": [
            {
                "@type": "Organization",
                "name": "一般社団法人 日比谷エリアマネジメント",
            },
            {
                "@type": "Organization",
                "name": "東京ミッドタウン日比谷",
            },
        ],
        "isAccessibleForFree": True,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "JPY",
            "availability": "https://schema.org/InStock",
            "url": site_url + "/",
            "validFrom": f"{EVENT_START_DATE}T00:00:00+09:00",
        },
        "performer": [
            {
                "@type": "MusicGroup",
                "name": a["name"],
                "url": f"{site_url}/artists/{a['slug']}.html",
            }
            for a in artists
        ],
        "superEvent": {
            "@type": "MusicEvent",
            "name": PARENT_EVENT_NAME,
            "url": PARENT_EVENT_URL,
        },
        "subEvent": sub_events,
    }

    return json.dumps(main_event, ensure_ascii=False, indent=2)


def build_artist_jsonld(artist: dict, site_url: str, site_name: str, site_desc: str) -> str:
    """Build per-artist JSON-LD: MusicGroup with performerOf MusicEvent slots."""
    page_url = f"{site_url}/artists/{artist['slug']}.html"
    image_url = (
        f"{site_url}/{PHOTO_DIR_WEB}/{artist['photo']}"
        if artist.get("photo")
        else f"{site_url}/assets/ogp.jpg"
    )
    performances = [
        build_event_subevent(artist, s, site_url, site_name)
        for s in artist["slots"]
    ]
    music_group = {
        "@context": "https://schema.org",
        "@type": "MusicGroup",
        "name": artist["name"],
        "description": artist.get("desc") or site_desc,
        "image": image_url,
        "url": page_url,
        "genre": artist.get("tags", []),
        "performerIn": performances,
    }
    return json.dumps(music_group, ensure_ascii=False, indent=2)


def build_artist_card_html(a: dict) -> str:
    """SSR equivalent of assets/js/main.js buildArtists() for one artist card."""
    slug = a["slug"]
    name = a["name"]
    photo = a.get("photo")
    desc = a.get("desc", "")
    slots = sorted(a["slots"], key=lambda s: f'{s["day"]} {s["time"]}')

    venues = []
    for s in slots:
        if s["venue"] not in venues:
            venues.append(s["venue"])
    venue_label = " / ".join(venues)
    slots_line = " / ".join(f'{s["day"]} {s["time"]}–' for s in slots)

    if photo:
        photo_html = (
            f'<div class="artist__photo">'
            f'<img src="assets/artists/{esc(photo)}" alt="{esc(name)}" '
            f'loading="lazy" decoding="async" />'
            f"</div>"
        )
    else:
        photo_html = '<div class="artist__photo artist__photo--placeholder"></div>'

    desc_html = f'<p class="artist__desc">{esc(desc)}</p>' if desc else ""

    return (
        f'<article class="artist reveal" id="artist-{esc(slug)}">'
        f'<a class="artist__link" href="artists/{esc(slug)}.html" '
        f'aria-label="{esc(name)} の詳細ページを開く">'
        f"{photo_html}"
        f"</a>"
        f'<div class="artist__body">'
        f'<p class="artist__venue">{esc(venue_label)}</p>'
        f'<a class="artist__name-link" href="artists/{esc(slug)}.html">'
        f'<h3 class="artist__name">{esc(name)}</h3>'
        f"</a>"
        f"{desc_html}"
        f'<p class="artist__slot">{esc(slots_line)}</p>'
        f"</div>"
        f"</article>"
    )


def replace_marker_block(text: str, marker: str, payload: str) -> str:
    """Replace content between <!-- BEGIN:marker --> and <!-- END:marker -->."""
    pattern = re.compile(
        rf"(<!-- BEGIN:{re.escape(marker)}[^>]*-->)(.*?)(<!-- END:{re.escape(marker)} -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise RuntimeError(f"Marker block not found: {marker}")
    return pattern.sub(lambda m: f"{m.group(1)}\n{payload}\n{m.group(3)}", text)


def write_sitemap(artists: list[dict], site_url: str) -> None:
    today = dt.date.today().isoformat()
    urls = [
        {"loc": f"{site_url}/", "priority": "1.0", "changefreq": "weekly"},
    ]
    for a in artists:
        urls.append({
            "loc": f"{site_url}/artists/{a['slug']}.html",
            "priority": "0.8",
            "changefreq": "monthly",
        })

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in urls:
        lines.append("  <url>")
        lines.append(f'    <loc>{u["loc"]}</loc>')
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f'    <changefreq>{u["changefreq"]}</changefreq>')
        lines.append(f'    <priority>{u["priority"]}</priority>')
        lines.append("  </url>")
    lines.append("</urlset>")

    SITEMAP_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_index_html(artists: list[dict], site_url: str, site_name: str, site_desc: str) -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")

    # Inject JSON-LD MusicEvent
    event_json = build_event_jsonld(artists, site_url, site_name, site_desc)
    json_ld_block = (
        f'<script type="application/ld+json">\n{event_json}\n</script>'
    )
    text = replace_marker_block(text, "json-ld", json_ld_block)

    # Inject SSR'd artist grid
    cards = "\n".join(build_artist_card_html(a) for a in artists)
    text = replace_marker_block(text, "artists-grid", cards)

    INDEX_PATH.write_text(text, encoding="utf-8")


TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<meta name="theme-color" content="#0b1322" />
<meta name="description" content="{og_desc}" />
<title>{name} ｜ {site_name}</title>
<link rel="canonical" href="{page_url}" />

<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
<link rel="alternate icon" type="image/png" href="/assets/favicon.png" />
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />

<!-- Open Graph -->
<meta property="og:type" content="article" />
<meta property="og:site_name" content="{site_name}" />
<meta property="og:title" content="{name} ｜ {site_name}" />
<meta property="og:description" content="{og_desc}" />
<meta property="og:url" content="{page_url}" />
<meta property="og:image" content="{og_image}" />
<meta property="og:image:secure_url" content="{og_image}" />{og_image_dims}
<meta property="og:image:alt" content="{name}" />
<meta property="og:locale" content="ja_JP" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{name} ｜ {site_name}" />
<meta name="twitter:description" content="{og_desc}" />
<meta name="twitter:image" content="{og_image}" />
<meta name="twitter:image:alt" content="{name}" />

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Noto+Sans+JP:wght@300;400;500;700;900&family=Oswald:wght@400;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="../assets/css/style.css" />
<link rel="stylesheet" href="../assets/css/artist.css" />

<script type="application/ld+json">
{json_ld}
</script>
</head>
<body>

<header class="site-header" id="siteHeader">
  <a class="brand" href="../index.html" aria-label="{site_name} トップへ">
    <span class="brand__mark">H·LF</span>
    <span class="brand__text">HIBIYA LIVE FESTIVAL <em>2026</em></span>
  </a>
  <nav class="nav" aria-label="セクション">
    <a href="../index.html#about">ABOUT</a>
    <a href="../index.html#schedule">SCHEDULE</a>
    <a href="../index.html#artists">ARTISTS</a>
    <a href="../index.html#venues">VENUES</a>
    <a href="../index.html#access">ACCESS</a>
  </nav>
  <button class="nav-toggle" id="navToggle" aria-label="メニューを開く" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
</header>

<main class="artist-page">
  <nav class="breadcrumbs" aria-label="パンくず">
    <a href="../index.html">HOME</a>
    <span aria-hidden="true">/</span>
    <a href="../index.html#artists">ARTISTS</a>
    <span aria-hidden="true">/</span>
    <span aria-current="page">{name}</span>
  </nav>

  <section class="artist-hero">
    <div class="artist-hero__media">{photo_html}</div>
    <div class="artist-hero__info">
      <p class="artist-hero__eyebrow">ARTIST</p>
      <h1 class="artist-hero__name">{name}</h1>
      {tags_html}
      <ul class="artist-hero__slots">
        {slots_html}
      </ul>
      <div class="artist-hero__cta">
        <a class="btn btn--ghost" href="../index.html#schedule">タイムテーブルへ</a>
      </div>
    </div>
  </section>

  {profile_section}

  <section class="artist-share" aria-labelledby="share-title">
    <h2 class="artist-share__title" id="share-title">SHARE</h2>
    <p class="artist-share__lead">このアーティストを応援しよう。</p>
    <div class="share-buttons">
      <a class="share-btn share-btn--x" href="{share_x}" target="_blank" rel="noopener noreferrer" aria-label="Xでシェア">
        <span class="share-btn__icon" aria-hidden="true">𝕏</span>
        <span class="share-btn__label">X (Twitter)</span>
      </a>
      <a class="share-btn share-btn--line" href="{share_line}" target="_blank" rel="noopener noreferrer" aria-label="LINEでシェア">
        <span class="share-btn__icon" aria-hidden="true">LINE</span>
        <span class="share-btn__label">LINE</span>
      </a>
      <a class="share-btn share-btn--fb" href="{share_facebook}" target="_blank" rel="noopener noreferrer" aria-label="Facebookでシェア">
        <span class="share-btn__icon" aria-hidden="true">f</span>
        <span class="share-btn__label">Facebook</span>
      </a>
      <button class="share-btn share-btn--copy" type="button" data-copy-url="{page_url}" aria-label="URLをコピー">
        <span class="share-btn__icon" aria-hidden="true">⎘</span>
        <span class="share-btn__label">URLコピー</span>
      </button>
    </div>
  </section>

  <nav class="artist-pager" aria-label="前後のアーティスト">
    {pager_html}
  </nav>
</main>

<footer class="site-footer">
  <div class="site-footer__inner">
    <div class="site-footer__brand">
      <p class="site-footer__title">HIBIYA LIVE FESTIVAL <em>2026</em></p>
      <p class="site-footer__date">2026.05.16 SAT — 05.17 SUN</p>
    </div>
    <dl class="site-footer__meta">
      <div><dt>公式企画</dt><dd><a href="https://www.hibiya.tokyo-midtown.com/hibiya-live-festival/" target="_blank" rel="noopener noreferrer">HIBIYA LIVE FESTIVAL<span aria-hidden="true">↗</span></a></dd></div>
      <div><dt>主催</dt><dd>一般社団法人 日比谷エリアマネジメント ／ 東京ミッドタウン日比谷</dd></div>
      <div><dt>協力</dt><dd>日比谷OKUROJI</dd></div>
      <div><dt>事務局</dt><dd><a href="https://artistmerge.jp/" target="_blank" rel="noopener noreferrer">アーティストマージ</a></dd></div>
      <div><dt>イベント運営</dt><dd>ニシヘヒガシヘ</dd></div>
    </dl>
    <p class="site-footer__copy">© 2026 HIBIYA LIVE FESTIVAL / Hibiya Area Management Association.</p>
  </div>
</footer>

<script src="../assets/js/artist.js" defer></script>
</body>
</html>
"""


def sort_key(a: dict) -> str:
    # earliest slot decides timetable position
    earliest = min(a["slots"], key=lambda s: (s["day"], s["time"]))
    return f'{earliest["day"]} {earliest["time"]}'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--site-url",
        default=None,
        help="Absolute site URL (overrides data/artists.json site.url).",
    )
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    site = data["site"]
    site_url = (args.site_url or site["url"]).rstrip("/")
    site_name = site["name"]
    site_desc = site.get("description", "")

    artists = sorted(data["artists"], key=sort_key)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    for i, a in enumerate(artists):
        slug = a["slug"]
        name = a["name"]
        photo = a.get("photo")
        desc = a.get("desc", "")
        tags = a.get("tags", [])
        slots = a["slots"]

        page_url = f"{site_url}/artists/{slug}.html"
        og_image = (
            f"{site_url}/{PHOTO_DIR_WEB}/{photo}"
            if photo
            else f"{site_url}/assets/ogp-default.jpg"
        )
        pw = a.get("photo_width")
        ph = a.get("photo_height")
        og_image_dims = (
            f'\n<meta property="og:image:width" content="{pw}" />'
            f'\n<meta property="og:image:height" content="{ph}" />'
            if pw and ph
            else ""
        )

        share_summary = (
            f"{name} | {slot_summary(slots)} | {site_name} (5.16-5.17 日比谷 / 入場無料)"
        )
        og_desc = trim_desc(f"{desc} {slot_summary(slots)}".strip() if desc else slot_summary(slots))
        shares = build_share_urls(page_url, share_summary)

        tags_html = ""
        if tags:
            pills = " ".join(f'<span class="artist-tag">{esc(t)}</span>' for t in tags)
            tags_html = f'<p class="artist-hero__tags">{pills}</p>'

        profile_section = ""
        if desc:
            profile_section = (
                '<section class="artist-profile" aria-labelledby="profile-title">'
                '<h2 class="artist-profile__title" id="profile-title">PROFILE</h2>'
                f'<div class="artist-profile__body"><p>{esc(desc)}</p></div>'
                "</section>"
            )

        prev_artist = artists[i - 1] if i > 0 else None
        next_artist = artists[i + 1] if i < len(artists) - 1 else None
        pager_html = build_nav(prev_artist, next_artist)

        json_ld = build_artist_jsonld(a, site_url, site_name, site_desc)

        html_out = TEMPLATE.format(
            site_name=esc(site_name),
            name=esc(name),
            og_desc=esc(og_desc),
            og_image=esc(og_image),
            og_image_dims=og_image_dims,
            page_url=esc(page_url),
            photo_html=build_photo_html(photo, name, ".."),
            tags_html=tags_html,
            slots_html=build_slots_html(slots),
            profile_section=profile_section,
            share_x=esc(shares["x"]),
            share_line=esc(shares["line"]),
            share_facebook=esc(shares["facebook"]),
            pager_html=pager_html,
            json_ld=json_ld,
        )

        out_path = OUT_DIR / f"{slug}.html"
        out_path.write_text(html_out, encoding="utf-8")
        generated.append(out_path.name)

    print(f"Generated {len(generated)} artist pages into {OUT_DIR}", file=sys.stderr)
    for n in generated:
        print(f"  - {n}", file=sys.stderr)

    # Update index.html (SSR artist grid + JSON-LD MusicEvent)
    update_index_html(artists, site_url, site_name, site_desc)
    print(f"Updated {INDEX_PATH.name} (SSR artist grid + JSON-LD)", file=sys.stderr)

    # Generate sitemap.xml
    write_sitemap(artists, site_url)
    print(f"Wrote {SITEMAP_PATH.name} ({len(artists) + 1} URLs)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
