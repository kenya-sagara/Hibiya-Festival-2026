# 変更履歴

本ファイルは HIBIYA LIVE FESTIVAL 2026 サイトの変更履歴を記録します。

## 2026-04-25

### 変更（アクセスマップ）

- 地図タイルを **CARTO Dark → CARTO Voyager**（明るめ・カラー）に切替して視認性を改善
- アクセスセクションの地図を OpenStreetMap iframe（1ピン）から **Leaflet.js + CARTO Voyager タイル** に置換
- **3会場すべてに番号付きピン（01/02/03）** をゴールド色で表示し、クリックで会場名と最寄駅をポップアップ表示
- ダーク基調にあわせたタイル＆コントロール配色、自動 fitBounds で3会場を一画面に収める
- API キー不要・無料（OSM + CARTO 無償利用、商用は別途確認）

### 追加・変更（Google Sheet 最新版反映）

- **横濱良太郎** を出演編成ごとに2エントリに分割
  - 5/16 FOOD HALL → 「横濱良太郎(Tb) standards」(yokohama-ryotaro-standards)
  - 5/17 OKUROJI → 「横濱良太郎(Tb) Quartet」(yokohama-ryotaro-quartet)
- **後藤天太** を出演編成ごとに2エントリに分割
  - 5/17 FOOD HALL → 「後藤天太(Sax) クインテット」(goto-quintet)
  - 5/17 OKUROJI → 「後藤天太(Sax) × 宮本憲(Gt) Duo」(goto-miyamoto-duo) ※新規プロフィール付き
- **石脇サンタ × 田中亮輔 Duo** にプロフィールと写真を追加
- アーティスト名に楽器略号を統一表記
  - 榎本有希 / 瀬川千鶴 → (Sax)/(Gt)（旧 Saxophone/Guitar）
  - 中島有美 / 眞間麻美 → (Vo)/(P)
  - 古川翼 → (Sax)、豊嶋さおり → (Tap)、冨永悟/前田勇作 → (Tb)/(P)
  - 松下美月/吉田一成 → (Sax)/(Gt)
- **楽器略号の凡例を SCHEDULE セクションに追加**（Sax/Gt/Vo/P/Tb/Tp/Bs/Ds/Per/Tap など、馴染みのない方向け）
- 青山学院大学 Royal Sounds の YBBJC を「ヤマノ・ビッグバンド・ジャズ・コンテスト」と注釈追記

### 変更（注意書きの誤解防止）

- 「雨天開催 / 荒天中止」を DAY 見出しから削除し、**日比谷ステップ広場 特設ステージ のステージカードのみ**に移動
  - 以前は DAY01/02 の見出しに表示されており、HIBIYA FOOD HALL や 日比谷OKUROJI にも掛かる誤解を招く表記だったため
  - 屋内会場（FOOD HALL / OKUROJI）には同注意書きは表示されない

### 変更（フッタ）

- フッタから「料金: 無料」を削除（ヒーローセクションで既に表記されているため）
- 「事務局業務」→「事務局」に表記簡素化
- 結果、フッタのクレジット4項目（主催 / 協力 / 事務局 / イベント運営）がデスクトップで1行に収まる

### 追加（SNSシェア最適化）

- **写真の最適化**を実施：全アーティスト写真を最大辺1600px・JPEG quality 85 で再生成し、EXIF回転も適用
  - After5 Lab Band が 41MB → 297KB まで縮小（クローラーのタイムアウト・失敗を防止）
  - TamiKiyo / TamiKiyo & Friends の PNG を JPEG に変換（775KB→52KB / 1.5MB→111KB）
  - `data/artists.json` に `photo_width` / `photo_height` を保存
- 全アーティスト専用ページと `index.html` の OGP に **`og:image:width` / `og:image:height` / `og:image:alt` / `og:image:secure_url`** を追加
- **サイト共通の OGP 画像** `assets/ogp.jpg`（1200×630）を自動生成（`scripts/gen_site_ogp.py`）し、`index.html` に Twitter Card / OGP を完備
  - トップページのSNSシェアでもイベントタイトル＋日程＋会場が映えるカードが出るように

### 追加（続）

- Good Neighbors Big Band のプロフィールと写真を追加（2018年結成、看板ボーカリストとの100曲超レパートリーを紹介）

### 変更

- フッタのクレジット表記を修正
  - 「協力: 日比谷OKUROJI 事務局」→「協力: 日比谷OKUROJI」
  - 「業務: アーティストマージ」→「事務局業務: アーティストマージ」
  - `index.html`、`scripts/build.py` のテンプレート、`docs/OVERVIEW.md` を同時修正し専用ページを再生成

### 追加

- **独自ドメイン**：`https://hibiya-festival.artistmerge.jp` で公開開始
  - リポジトリ直下に `CNAME` ファイルを配置
  - `data/artists.json` の `site.url` を更新し、全アーティスト専用ページのOGP絶対URLを新ドメインに切替
- **Axis Quintet（アクシス・クインテット）** を新規追加（5/16 HIBIYA FOOD HALL 18:00 枠、旧「松坂光輝 Quintet」を差し替え）
- **Albariño 〜葡萄系ビッグバンド第21弾〜** / **Barbera 〜葡萄系ビッグバンド第22弾〜** のプロフィール・写真を追加
- 写真：`axis-quintet.jpg` / `albarino-budoukei-21.jpg` / `barbera-budoukei-22.jpg` の3点追加

### 変更

- 既存の17点の写真は差分なし（更新版ZIPを取り込み、内容同一を確認）
- Albariño / Barbera の表記を「〜葡萄系…〜」の波括弧付きに統一（Excel表記に合わせ）

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
