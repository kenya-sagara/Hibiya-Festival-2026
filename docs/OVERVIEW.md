# HIBIYA LIVE FESTIVAL 2026 — システム概要

## 目的

2026年5月16日(土)・17日(日)に開催される「HIBIYA LIVE FESTIVAL 2026（Hibiya Festival 2026 MUSIC WEEKEND）」の情報発信用・告知用の静的ウェブサイト。

## 主要コンテンツ

- イベント概要・開催日時
- 3会場×2日間のタイムテーブル
- 出演アーティスト一覧（写真・プロフィール・出演情報）
- 会場紹介
- アクセス情報
- 主催・協力・運営クレジット

## 技術スタック

| 区分 | 採用技術 | 備考 |
|------|---------|------|
| マークアップ | HTML5 | 単一ページ（index.html） |
| スタイル | Pure CSS（CSS Custom Properties 使用） | フレームワーク不使用 |
| スクリプト | Vanilla JavaScript（ES2015+） | 外部ライブラリ不使用 |
| フォント | Google Fonts (Oswald / Cormorant Garamond / Noto Sans JP) | CDN読込 |
| 地図 | OpenStreetMap 埋め込み | APIキー不要 |

## 設計方針

- 外部依存を最小化し、静的ホスティングにそのまま配置できる構成
- ビルドツール不要（素のHTML/CSS/JS）
- アーティスト情報は `data/artists.json` で一元管理（Single Source of Truth）
- メインページは JSON を fetch して動的生成、専用ページは `scripts/build.py` で事前生成
- ダーク基調（`#0b1322`）＋ゴールドアクセント（`#e8b64d`）でナイトライフと日比谷の上質感を表現
- レスポンシブ対応（モバイル〜デスクトップ）
- `prefers-reduced-motion` に配慮
- 各アーティストに SNS 共有可能な固有URL（OGP / Twitter Card 付き）

## ディレクトリ構成

```
Hibiya-Festival-2026/
├── index.html               # メインページ
├── artists/                 # 各アーティスト専用ページ（build.py で自動生成）
│   └── <slug>.html          # OGP / Twitter Card 付き個別ページ
├── assets/
│   ├── css/
│   │   ├── style.css        # 全体共通スタイル
│   │   └── artist.css       # 専用ページ & シェアボタン用
│   ├── js/
│   │   ├── main.js          # メインページ制御（JSONフェッチ、カード生成）
│   │   └── artist.js        # 専用ページ制御（URLコピー等）
│   └── artists/             # 出演者写真（URLセーフな slug 名）
├── data/
│   └── artists.json         # アーティスト情報の SSOT
├── scripts/
│   └── build.py             # artists.json → 各専用ページを生成
├── docs/                    # 本ドキュメント群
│   ├── OVERVIEW.md
│   ├── SETUP.md
│   ├── CHANGELOG.md
│   ├── PROGRESS.md
│   └── manuals/
│       ├── MANUAL_閲覧者.md
│       └── MANUAL_運営者.md
└── _source/                 # 制作時の原典データ（公開対象外）
    ├── booking.xlsx
    ├── artists.zip
    └── artists_raw/
```

## アーティスト情報の管理フロー

```
data/artists.json (SSOT)
     │
     ├─ fetch ─→ assets/js/main.js  →  index.html 出演者グリッド（動的生成）
     │
     └─ read  ─→ scripts/build.py   →  artists/<slug>.html（静的生成）
```

- **SSOT（Single Source of Truth）**：`data/artists.json`。ここを更新 → `python scripts/build.py` で専用ページを再生成。
- **メインページ**：ブラウザが JSON を fetch してアーティストカードを動的描画。
- **専用ページ**：各バンドが SNS でシェアできる固有 URL を持つ。OGP/Twitter Card により、投稿プレビューでバンド写真と名前が表示される。

## 開催情報

- **日時**：
  - ① 日比谷ステップ広場 特設ステージ：5/16(土) 13:00–18:00 ／ 5/17(日) 12:00–17:00（雨天開催・荒天中止）
  - ② HIBIYA FOOD HALL：5/16(土) 12:00–14:00 / 17:00–20:00 ／ 5/17(日) 12:00–14:00 / 17:00–19:00
  - ③ 日比谷OKUROJI：5/16(土) 16:00–21:00 ／ 5/17(日) 12:00–17:00
- **料金**：無料
- **主催**：一般社団法人日比谷エリアマネジメント、東京ミッドタウン日比谷
- **協力**：日比谷OKUROJI事務局
- **業務**：アーティストマージ
- **イベント運営**：ニシヘヒガシヘ
