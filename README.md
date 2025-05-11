# deepwiki-to-md

DeepWikiのコンテンツ（リポジトリのWikiやチャットログ）をMarkdown形式でローカルに保存するためのCLIツールです。

## 機能

- **チャットログの取得**: DeepWikiのチャットページをMarkdownファイルとして保存
- **Wikiサイトの取得**: DeepWikiのWiki全体をMarkdownファイルとして保存
- **Mermaid図の抽出**: チャットやWiki内のMermaid図をSVGファイルとして保存
- **整形されたMarkdown出力**: 読みやすく整形されたMarkdownコンテンツの生成

## インストール

### 方法1: ラッパースクリプトを使用する（推奨）

```bash
# ラッパースクリプトをダウンロード
curl -O https://github.com/suwash/deepwiki-to-md/releases/latest/download/deepwiki-to-md

# 実行権限を付与
chmod +x deepwiki-to-md

# 必要に応じてPATHの通ったディレクトリに移動
sudo mv deepwiki-to-md /usr/local/bin/
```

### 方法2: Dockerを直接使用する

```bash
# Dockerイメージを使用
docker run --rm -v "$(pwd):/output" suwash/deepwiki-to-md:latest chat <URL>
```

## 使用方法

### 基本的な使い方

```bash
# チャットページを取得
./deepwiki-to-md chat https://deepwiki.com/search/your-chat-id

# Wikiサイトを取得
./deepwiki-to-md wiki https://deepwiki.com/organization/repository

# 出力先ディレクトリを指定
./deepwiki-to-md chat https://deepwiki.com/search/your-chat-id -o ./output
```

### サブコマンド

- `chat <URL>`: DeepWikiのチャットページをMarkdownに変換
- `wiki <URL>`: DeepWikiのWikiページ（サイト全体）をMarkdownに変換

### オプション

- `-o, --output <ディレクトリ>`: 出力先ディレクトリを指定（デフォルト: カレントディレクトリ）
- `-h, --help`: ヘルプメッセージを表示

## 出力形式

### chatコマンド

```
output/
└── search/
    └── your-chat-id/
        ├── chat.md         # チャット履歴コンテンツ
        └── images/         # Mermaid図のSVGファイル
            ├── 0__diagram_0.svg
            ├── 0__diagram_1.svg
            └── ...
```

### wikiコマンド

```
output/
└── wiki/
    └── organization/
        └── repository/
            ├── 1-page-title.md  # ページコンテンツ
            ├── 2-page-title.md
            ├── ...
            ├── index.md         # 目次ページ
            └── images/          # Mermaid図のSVGファイル
                ├── 1-page-title_diagram_0.svg
                ├── 1-page-title_diagram_1.svg
                └── ...
```

## 開発者向け情報

### 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/suwash/deepwiki-to-md.git
cd deepwiki-to-md
code .
# dev containerを開く

# テストの実行
./test/size_L/test_chat.sh
./test/size_L/test_wiki.sh
```

### imageの公開

```bash
./scripts/buildpack.sh
```

### アーキテクチャ

deepwiki-to-mdはクリーンアーキテクチャを採用し、以下の層構造で実装されています：

- **ドメイン層**: ビジネスロジックとエンティティ
- **ユースケース層**: アプリケーション固有のビジネスロジック
- **リポジトリ層**: ドメインオブジェクトと外部データの変換
- **ゲートウェイ層**: 外部ライブラリとの通信を抽象化
- **インターフェース層**: ユーザーとの対話

## ライセンス

MIT License
