# マニュアル：運営者向け

サイト運営・コンテンツ更新担当者向けの操作手順です。

## できること

| 項目 | 対応ファイル | 難易度 |
|------|-------------|-------|
| 出演者の追加・編集・削除 | `data/artists.json` → `python scripts/build.py` | ★☆☆ |
| 出演者写真の差し替え | `assets/artists/` に配置 + JSON を更新 → build 再実行 | ★☆☆ |
| タイムテーブル（時間・バンド名）の修正 | `index.html` の `.timetable` | ★☆☆ |
| 開催日時・会場情報の修正 | `index.html` の `.hero__meta` / `.venues` / `.access` | ★★☆ |
| 主催・協力クレジットの修正 | `index.html` のフッター `.site-footer__meta` | ★☆☆ |
| サイトURL（OGP用）の変更 | `data/artists.json` の `site.url` → build 再実行 | ★☆☆ |
| 配色・フォントの変更 | `assets/css/style.css` 先頭の `:root` 変数 | ★★☆ |
| レイアウトや新セクションの追加 | `index.html` + CSS | ★★★ |

## よくある更新の手順

### 1. 出演者を追加する

1. `assets/artists/` にアーティスト写真を配置（**ファイル名は URL セーフな英数小文字＋ハイフン**推奨、例：`after5-lab-band.jpg`）
2. `data/artists.json` の `artists` 配列に1オブジェクト追加：

```json
{
  "slug": "after5-lab-band",
  "name": "バンド名",
  "photo": "after5-lab-band.jpg",
  "tags": ["ビッグバンド"],
  "desc": "150文字前後のプロフィール",
  "slots": [
    { "venue": "日比谷ステップ広場", "day": "5.16 SAT", "time": "13:00", "end": "13:45" }
  ]
}
```

- `slug` は URL に使われる一意識別子。英数小文字＋ハイフン。以降変更しないこと（既存のSNSシェア先URLが壊れる）
- 1バンドが複数出演する場合は `slots` に複数オブジェクトを追加

3. 専用ページを再生成：

```bash
python scripts/build.py
```

4. タイムテーブルにも手動で反映（`index.html` の `.timetable`）：

```html
<li>
  <span class="timetable__time">13:00<em>–</em>13:45</span>
  <a class="timetable__act" href="#artist-after5-lab-band">バンド名</a>
</li>
```

### 2. 出演者写真を差し替える

1. 新しい写真を `assets/artists/` に同名で上書き
2. `data/artists.json` の `photo` フィールドを更新（ファイル名を変えた場合）
3. `python scripts/build.py` で専用ページを再生成
4. キャッシュ回避が必要な場合はファイル名を変える（例：`xxx-v2.jpg`）

### 3. サイトURL（OGP/SNSシェア）を変更する

本番ドメイン確定後などに、SNS でプレビュー表示される URL を変更したい場合：

1. `data/artists.json` の `site.url` を本番ドメインに変更
2. `python scripts/build.py` で全24ページを再生成
3. デプロイ

> 💡 `og:image` や `og:url` は **絶対URL**で出力する必要があるため、この設定が必須。相対パスだと SNS 側でプレビューが出ない場合がある。

### 3. 開催日時の表記を変更する

`index.html` の以下を確認：

- `<dl class="hero__meta">` ブロック（ヒーロー部分の日付）
- `.section--schedule` 各 `.stage__time`
- `.venues` 各 `.venue__hours`
- ACCESS セクションの説明文

### 4. 主催・協力クレジットを変更する

`index.html` 末尾の `<dl class="site-footer__meta">` 内 `<dt>/<dd>` を編集。

## できないこと（または要注意）

- **Excel を直接サイトが読み込むことはできません**：Excel を編集後、その内容を手動で `data/artists.json` と `index.html`（タイムテーブル）に反映してください
- **CMS 機能はありません**：コードの直接編集が必要です
- **アーティスト情報の変更は Python build が必要**：`data/artists.json` を触ったら必ず `python scripts/build.py` を実行してください
- **タイムテーブルと JSON の同期は手動**：現状 `index.html` のタイムテーブルと `data/artists.json` は別管理なので、バンド名や時間の変更は両方に反映が必要

## デプロイ手順

1. 本番ドメインが確定したら `data/artists.json` の `site.url` を更新
2. `python scripts/build.py` で専用ページを再生成
3. ローカルで動作確認（`docs/SETUP.md` 参照）
4. `_source/` ディレクトリは**公開対象に含めない**こと（.gitignoreで除外済み）
5. `index.html`、`artists/`、`assets/`、`data/` をホスティング環境にアップロード

## SNSシェアの確認

デプロイ後、SNSでシェアする前にプレビューを確認できます：

- **X (Twitter) Card Validator**: <https://cards-dev.twitter.com/validator>
- **Facebook Debugger**: <https://developers.facebook.com/tools/debug/>
- **LINE**: LINE トーク画面にURL貼付で自動プレビュー

キャッシュクリア（再取得）もこれらのツールから可能。

## 注意事項

- `_source/booking.xlsx` は現状の原本（2026-04-24時点）です。Excelの更新があった場合は、必ず同ディレクトリに最新を保存した上で、サイト側にも反映してください
- フォント読み込みは Google Fonts の CDN を使用しています。オフライン環境で動作させる場合は自前ホスティングに切り替えが必要です
- 地図は OpenStreetMap の埋め込みです。別の地図サービス（Google Maps 等）に変更する場合は、`.access__map` 内の `<iframe>` を差し替えてください
