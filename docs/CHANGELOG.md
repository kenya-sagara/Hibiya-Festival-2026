# 変更履歴

本ファイルは HIBIYA LIVE FESTIVAL 2026 サイトの変更履歴を記録します。

## 2026-04-24

### 追加

- **各アーティストの専用ページ**を自動生成する仕組みを導入（SNS シェア対応）
  - `data/artists.json`：アーティスト情報を一元管理する SSOT を新設
  - `scripts/build.py`：JSONから `artists/<slug>.html` を生成する Python スクリプト
  - `assets/css/artist.css`：専用ページ＆シェアボタン用のスタイル
  - `assets/js/artist.js`：専用ページの URL コピー機能等
  - 各ページに OGP / Twitter Card（summary_large_image）を埋め込み、SNS 投稿時にバンド写真＋名前＋出演情報のプレビューが出る
  - X / LINE / Facebook シェアボタン、URLコピー、前後アーティストへのページャー、パンくず
  - 生成ページ数：24ページ（出演アーティストの重複を除いた固有数）
- メインページのアーティストカードから写真・名前クリックで各バンドの専用ページへ遷移できるように
  - カード自体にはSNSシェアボタンは置かず、シンプルな一覧を維持
  - 共有動作は各バンドの専用ページ側に集約
- `assets/js/main.js` を `data/artists.json` の fetch ベースに書き換え
  - アーティスト情報の重複管理を解消（JSON を更新すればサイト全体に反映）

### 変更

- 出演アーティストの並び順を「写真あり優先」から**タイムテーブル順（日付→時刻）**に変更
  - 影響範囲：`assets/js/main.js` の `buildArtists()` のソートロジック
  - 同一アーティストが複数会場で出演する場合は、最も早い出演枠を表示するよう調整
- アーティスト一覧のカードを大きく表示するよう調整
  - 影響範囲：`assets/css/style.css` の `.artists-grid` / `.artist__body` ほか
  - グリッド最小幅 240px → 340px、アーティスト名 15px → 18px、説明文 12px → 13.5px
- タイムテーブルを「タブ切替」から「2日を同時表示」に変更
  - 影響範囲：`index.html` SCHEDULE、`assets/css/style.css` （`.tabs` 系削除、`.day__head` / `.day__stages` 追加）、`assets/js/main.js` (`initTabs()` 削除)
- タイムテーブルの出演枠をアーティスト紹介カードへのアンカーリンクに変更
  - 各アーティストに `slug` フィールドを追加し、`id="artist-{slug}"` を付与
  - 遷移時はスムーズスクロール＋ゴールドの枠線・グロー＋浮き上がりで約2.8秒のハイライト
  - 同じアーティストを連続クリックしても毎回アニメーションが再生される（click ハンドラで強制リフローして再トリガ）
- 冨永悟×前田勇作DUO（旧「冨永悟(tb) DUO w/ 前田勇作(pf)」）の表記とプロフィールを差し替え、写真を追加（`assets/artists/tominaga-maeda-duo.jpg`）
- アーティスト写真の表示を `object-fit: cover`（はみ出し切り抜き）から `object-fit: contain`（全体表示＋余白）に変更
  - 影響範囲：`assets/css/style.css` の `.artist__photo img`
  - 理由：縦横比の異なる提供写真で顔やメンバーが切れてしまう問題を回避。余白部には背景グラデーションを施して見た目を整えた
- アーティスト写真カードのアスペクト比を `4:5`（縦長）から `4:3`（やや横長）に変更
  - 影響範囲：`assets/css/style.css` の `.artist__photo`
  - 理由：横位置の寄せ・集合写真が自然に収まるように

### 追加

- プロジェクト初期構築
  - 影響範囲：全体
  - 内容：
    - `index.html`：ヒーロー／ABOUT／SCHEDULE（5/16・5/17 タブ切替、3会場×2日間）／ARTISTS（写真グリッド）／VENUES（3会場カード）／ACCESS（拠点説明＋地図）／フッター
    - `assets/css/style.css`：ダーク＋ゴールドの全スタイル、レスポンシブ、アニメーション
    - `assets/js/main.js`：アーティスト一覧データ・グリッド生成、日替わりタブ、スクロール連動ヘッダー、モバイルナビ、scroll reveal
    - `assets/artists/`：出演者写真13点を URL セーフな slug にリネームして配置
  - 入力データ：
    - `_source/booking.xlsx`（「Hibiya Festival 2026」MUSIC WEEKEND ブッキング）
    - `_source/artists_raw/`（アーティスト写真2026）
- ドキュメント整備
  - `docs/OVERVIEW.md`、`docs/SETUP.md`、`docs/PROGRESS.md`、本ファイル、`docs/manuals/` を作成
