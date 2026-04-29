# 変更履歴

本ファイルは HIBIYA LIVE FESTIVAL 2026 サイトの変更履歴を記録します。

## 2026-04-30

### 追加（アーティスト個別ページの自己完結化：開催情報＋会場アクセス）

SNS から個別ページに直接来訪した人でも、戻らずに「いつ・どこで・どう行くか」が分かるよう、各ページに以下を追加。

- **Hero の日時・会場をサイズアップ**：`.slot__day` `.slot__time` を 14px → `clamp(20-24px, 2.4vw, 26-28px)` の display フォントに拡大。会場名にピン絵文字（📍）と、当該会場カードへのアンカーリンクを付与
- **EVENT INFO バナー**：開催期間（5.16 SAT — 5.17 SUN）／ 3会場 ／ 入場無料 を、PROFILE の下に告知バナーとして配置。`全タイムテーブルを見る ↗` のCTAでメインページの SCHEDULE へ
- **VENUE & ACCESS セクション**：3会場のカード（番号 / 会場名 / 住所 / 最寄駅 / Google Maps リンク）を表示。当該アーティストの出演会場には `venue-card--highlight` を付与し、ゴールド枠＋背景＋「出演」フラグで強調。Hero の会場名タップで対応カードへスクロール（`scroll-margin-top: 100px` 付き）
- **Google Maps ディープリンク**：`https://www.google.com/maps/search/?api=1&query=<encoded address>` を `gmaps_url()` ヘルパで生成。端末標準のマップで開ける
- **Leaflet は意図的に載せない**：26 ページ × Leaflet.js（38KB）＋ CARTO タイルは過大。インタラクティブマップはメインページに集約し、個別ページはカード＋ Maps リンクで軽量に
- **`scripts/build.py`**：`VENUES` 辞書に `stations` / `num` / `anchor` を追加。`build_festival_info_html()` / `build_venues_access_html(artist)` を新設し、TEMPLATE に差し込み
- **`assets/css/artist.css`**：`.slot` の刷新と、`.festival-info` / `.artist-venues` / `.venue-card`（含 `--highlight` 装飾）のスタイルを追加

### 変更（Happy Flight Jazz Orchestra の写真差し替え）

- 提供素材（バンド全員でのライブ写真）に差し替え（`assets/artists/happy-flight-jazz-orchestra.jpg`、943×654）
- `data/artists.json` の `photo_width` / `photo_height` を更新
- `artists/happy-flight-jazz-orchestra.html` の OGP / Twitter Card 画像寸法を再生成

## 2026-04-29

### 追加（総合企画 HIBIYA LIVE FESTIVAL との関係を明示）

本サイトは東京ミッドタウン日比谷／日比谷エリアマネジメントが運営する [HIBIYA LIVE FESTIVAL](https://www.hibiya.tokyo-midtown.com/hibiya-live-festival/) の 2026 年版「MUSIC WEEKEND」であることを、視覚・構造化データの両面で明示。

- **ヒーローの冠ラベル**：`HIBIYA FESTIVAL 2026 / MUSIC WEEKEND` を `HIBIYA LIVE FESTIVAL ↗ / 2026 MUSIC WEEKEND` に変更し、総合企画名は HIBIYA LIVE FESTIVAL ページへの外部リンクに（`target="_blank" rel="noopener noreferrer"`）
- **About セクション**：本文末尾に `PART OF` ラベル付きの注記ブロックを追加し、本イベントが総合企画 HIBIYA LIVE FESTIVAL の一環であることと、総合ページへの導線を1段落で明記。説明は「演劇」と「音楽」を軸とする都市型エンターテインメント・フェスティバルである旨を反映
- **フッター**：`総合企画` 行を新設し、HIBIYA LIVE FESTIVAL ページへの恒常リンクを配置（`主催 / 協力 / 事務局 / イベント運営` の上）
- **構造化データ（JSON-LD）**：トップページ `MusicEvent` に `superEvent`（`@type: MusicEvent`, `name: "HIBIYA LIVE FESTIVAL"`, 総合企画URL）を追加。これにより `総合企画 → 2026年版 → 各ライブ枠`（`subEvent`）の 3 階層の関係が検索エンジンに正しく伝わるように
- **`scripts/build.py`**：総合企画名／URLを定数化（`PARENT_EVENT_NAME` / `PARENT_EVENT_URL`、内部識別子のため Schema.org の `superEvent` 命名を踏襲）。アーティスト個別ページの TEMPLATE フッターにも同じ「総合企画」行を反映
- **CSS**：`.hero__eyebrow-parent` / `.about__parent` のスタイルを追加（ゴールド・アンダーライン＋枠線で控えめに強調）

### 変更（文言の統一：「親」→「総合」）

ユーザー向け文言の「親イベント／親企画／親サイト」表記をいったん「公式企画／公式サイト」に統一したが、本サイト（`hibiya-festival.artistmerge.jp`）も MUSIC WEEKEND の公式サイトであるため誤解を招く。`HIBIYA LIVE FESTIVAL`（4.25–5.31 にわたる総合企画）と区別するため、最終的に「**総合企画／総合ページ**」に統一。

- `index.html`：About 注記ブロック本文・aria-label・フッター行ラベル
- `scripts/build.py`：アーティスト個別ページ TEMPLATE のフッター行ラベル
- `docs/` 各ファイル
- `scripts/build.py` 内のコード識別子 `PARENT_EVENT_*` は Schema.org の `superEvent` に対応する内部命名として据え置き

### 変更（「2日間」表現を緩和）

本サイトは MUSIC WEEKEND（5.16–5.17 の 2 日間）を扱うが、ヒーロー見出しが `HIBIYA LIVE FESTIVAL` であるため、「2日間」と書くと総合企画自体が 2 日間と誤読される。総合企画は 4.25–5.31 にわたるため、以下を変更：

- **Hero タグライン**：`街が、ステージになる2日間。` → `音楽の週末、街がステージになる。`
- **About 本文**：`歴史と文化が息づく日比谷エリアを舞台に、週末の2日間、街全体がひとつのライブ会場になる。` → `歴史と文化が息づく日比谷エリアを舞台に、5月の週末、街全体がひとつのライブ会場になる。`

### 修正（出演組数の表記）

About 本文と統計バッジの「総勢30組以上 / 30+ ACTS」表記を、`data/artists.json` の実数（26 組）に合わせて `総勢26組 / 26 ACTS` に修正。

### 変更（About 注記の位置づけを「サブイベント」から「詳細情報サイト」へ）

About 注記ブロックの主語を「本イベント」→「本サイト」に変更。HIBIYA LIVE FESTIVAL の中の一サブイベントというより、「総合企画の中の MUSIC WEEKEND にフォーカスし、より詳しい情報をお届けする専用サイト」という位置づけを明示。

- 旧：`本イベントは、…HIBIYA LIVE FESTIVAL の一環として開催されます。HIBIYA LIVE FESTIVAL の他プログラム・最新情報は総合ページをご覧ください。`
- 新：`本サイトは、…HIBIYA LIVE FESTIVAL のうち、5月16・17日に開催される MUSIC WEEKEND にフォーカスし、より詳しい情報をお届けする専用サイトです。フェスティバル全体の最新情報・他プログラムは総合ページをご覧ください。`

## 2026-04-28

### 追加（後藤天太(Sax) クインテット）

- 写真を追加（`assets/artists/goto-quintet.jpg`、1067×1600）
- プロフィール文を追加：「第一線で活躍するミュージシャン達による白熱のクインテット。 最高にかっこいいステージをお届けします。 是非お見逃しなく。 メンバー 後藤天太(Sax)武藤勇樹(Key)宮本憲(Gt)森田悠介(Bs)橋本現輝(Ds)」
- メンバー表記をプロジェクト規約（`Sax/Key/Gt/Bs/Ds`）に統一
- index.html のアーティストグリッド、`artists/goto-quintet.html`、OGP / Twitter Card / JSON-LD MusicGroup を一括反映

### 追加（SEO 強化）

検索エンジンと SNS に対する正しい情報露出を強化するため、以下を一括導入。

- **`sitemap.xml` の自動生成**：トップ + 全アーティスト個別ページ（計 27 URL）を網羅。`scripts/build.py` 実行時に同時生成
- **`robots.txt`**：`Sitemap:` ディレクティブで sitemap を明示。`/_source/` はクロール対象外に
- **構造化データ（JSON-LD）を全ページに埋め込み**
  - トップ：`MusicEvent`（フェス全体）。`subEvent` で各出演枠を `MusicEvent` として展開し、`location` に3会場の `Place`（住所＋GeoCoordinates）、`offers.price=0` で入場無料を明示、`performer` に全アーティストを列挙
  - 各アーティストページ：`MusicGroup`（プロフィール／写真／genre＝tags）+ `performerIn` に当該アーティストの全出演枠を `MusicEvent` として埋め込み
- **アーティストグリッドの SSR 化**：トップの `#artistsGrid` をビルド時に静的出力するように変更。これまでは JS 描画のみで JS 非実行クローラ／一部 SNS スクレイパーには空に見えていたが、HTML だけで全 26 アーティストカード（写真・名前・出演枠・個別ページへの内部リンク）が読み取れるようになった
  - `assets/js/main.js` は SSR 済みなら描画をスキップする条件分岐を追加（二重描画防止）
- **favicon / apple-touch-icon を追加**
  - `assets/favicon.svg`（ブランドカラーの "H" マーク）
  - `assets/favicon.png`（32×32, PNG フォールバック）
  - `assets/apple-touch-icon.png`（180×180）
  - `scripts/gen_favicon.py` で PNG 系を再生成可能
  - トップ・全アーティストページの `<head>` に `<link rel="icon">` / `<link rel="apple-touch-icon">` を追加

### 変更（`scripts/build.py`）

- `index.html` のマーカーブロック（`BEGIN:json-ld` / `BEGIN:artists-grid`）をビルド時に自動上書き
- 会場メタ情報（住所・緯度経度）を Python 側にも保持（Leaflet 側 `assets/js/main.js` と整合）
- 開始・終了時刻を ISO 8601（`+09:00` 付き）に変換するヘルパを追加

## 2026-04-27

### 追加・変更（柴田一輝(Key)、帆足昌太(Bs)、2人ぼっち）

- 表記をプロジェクト規約に合わせて **「柴田一輝(Key)、帆足昌太(Bs)、2人ぼっち」** に統一（楽器略号付与、ベース表記は Bs）
- 写真を追加（`assets/artists/shibata-hoashi-futaribochi.jpg`、1414×2000）
- プロフィール文を追加：「都会の夜に溶け込む、洗練されたサウンド。繊細さと爆発力を併せ持つプレイで、スタンダードからオリジナルまで自在に行き来する。一音ごとに交わされる会話のようなインタープレイが、唯一無二の時間を生み出します。」
- タグに **キーボード / ベース** を追加
- OGP / Twitter Card / 個別ページ（`artists/shibata-hoashi-futaribochi.html`）・index タイムテーブル・前後ページャ（古川翼、松下美月）の表記もあわせて更新

### 変更（榎本有希(Sax) × 瀬川千鶴(Gt)）

- メイン写真（`assets/artists/enomoto-segawa.jpg`）を提供素材に差し替え（寸法は 1346×1063 で同一）

### 変更（TamiKiyo / TamiKiyo & Friends プロフィール文）

- **TamiKiyo**：メンバー本名を併記する形に更新（「VocalのTamie（梶多美江）／PianoのKiyo（山口記世）によるDuo」）。語尾と装飾を提供文に合わせ、♪ 等の記号も反映
- **TamiKiyo & Friends**：構成メンバー（Sax 藤井淳平、Tp 佐々木克典、Bs 斎藤柊真、Ds 高本佳範）を明記。ジャズを「こよなく愛する」→「愛する」、「ジャズナンバー」→「ナンバー」など提供文の表現に合わせて更新
- 上記いずれも meta description / OGP / Twitter Card / PROFILE 本文を一括反映

## 2026-04-25

### 変更（アクセスマップ）

- ACCESS の各拠点カードと地図のピンを連動：
  - カードクリック → 該当ピンの吹き出しを開きつつ flyTo でスムーズ移動
  - キーボード（Enter / Space）操作にも対応
  - ピンの吹き出しが開いている間は、対応する拠点カードがゴールドで強調
- カードに番号バッジ（01/02/03）を追加。地図ピンとの対応が一目でわかるように
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
