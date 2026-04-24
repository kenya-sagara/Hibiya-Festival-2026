# 環境構築手順

静的サイトのため、ビルドや依存インストールは不要です。

## ローカルでの動作確認

HTMLを直接開いても動作しますが、`file://` スキームだとフォント読込や fetch 系APIが制限されることがあります。簡易HTTPサーバーを立てて確認してください。

### 方法 A：Python の組み込みサーバー

```bash
cd C:\Users\sag0903\project\Hibiya-Festival-2026
python -m http.server 8080
```

ブラウザで <http://localhost:8080> を開く。

### 方法 B：Node.js (`npx`)

```bash
cd C:\Users\sag0903\project\Hibiya-Festival-2026
npx --yes http-server -p 8080
```

### 方法 C：VS Code

拡張機能「Live Server」を導入し、`index.html` を右クリック →「Open with Live Server」。

## デプロイ

静的ファイル（`index.html` と `assets/` ディレクトリ）をそのままアップロードするだけで動作します。

- **Netlify / Vercel / Cloudflare Pages**：リポジトリを連携するだけで自動デプロイ（ビルドコマンド不要、出力ディレクトリはプロジェクトルート）。
- **AWS S3 + CloudFront**：`index.html` と `assets/` を同一バケットに配置し、静的Webサイトホスティングを有効化。
- **従来のレンタルサーバー**：FTP等で `index.html` と `assets/` を公開ディレクトリに配置。

> ⚠️ `_source/` ディレクトリは Excel 原本や写真のオリジナルを保管しています。**公開時は必ず除外**してください（`.gitignore` 等で管理）。

## ブラウザ対応

- モダンブラウザ（Chrome / Edge / Safari / Firefox の直近2メジャーバージョン）
- CSS custom properties / `aspect-ratio` / `:has()` 等のモダン機能を使用
- IE 非対応

## コンテンツ更新

### 一元管理

アーティスト情報は `data/artists.json` に集約されています。以下を編集：

- **出演者の追加・編集・写真差し替え**：`data/artists.json` の `artists[]` を編集し、写真ファイルを `assets/artists/` に配置
- **サイトURL（OGP/シェア用）**：`data/artists.json` の `site.url` を本番ドメインに変更
- **タイムテーブル**：`index.html` 内 `.timetable` リストを編集（現状は手動同期）
- **開催情報・会場情報**：`index.html` の `.hero__meta` / `.venues` / `.access` セクション
- **スタイルのトーン変更**：`assets/css/style.css` の `:root` 内 CSS 変数

### 専用ページの再生成（必須）

`data/artists.json` を編集した後は、必ず以下を実行して各アーティストの専用ページを再生成してください：

```bash
python scripts/build.py
```

`artists/<slug>.html` が全アーティスト分、上書き生成されます。  
サイトURLをコマンドラインから上書きしたい場合：

```bash
python scripts/build.py --site-url https://example.com
```
