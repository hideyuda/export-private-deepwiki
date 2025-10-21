# export-private-deepwiki

> **言語 / Languages:** [English](../README.md) | [日本語](README_ja.md)

## 1. 概要

`export-private-deepwiki`は、DeepWikiのコンテンツ（リポジトリのWikiやチャットログ）をMarkdown形式でローカルに保存するためのCLIツールです。
このプロジェクトにより、ユーザーはDeepWiki上の情報を簡単にエクスポートし、ローカル環境で管理・活用できます。

### 1.1. 目的

1.  DeepWikiのチャットログをMarkdown形式で取得できるようにします。
2.  DeepWikiのWikiコンテンツをMarkdown形式で取得できるようにします。
3.  Mermaidの図も適切に変換・保存して再利用できるようにします。

## Private DeepWiki（Devin上の非公開Wiki）への対応

これまで公開（public）のDeepWikiのみを対象としていましたが、ログインが必要な非公開ページについても、Playwrightの永続コンテキスト（persistent context）を使用して同様に取得できるモードを追加しました。

ポイント
- 既存のリクエストベースではなく、実ブラウザ（Chromium/Chrome）を起動して、ログイン済みセッション（Cookie/LocalStorage）を使ってページにアクセスします。
- 初回はヘッド付き（--headed）でブラウザを表示し、ログインを完了してください。以降は同じユーザーデータディレクトリ（--user-data-dir）を指定すれば、ログイン状態が維持されます。
- macOSの既存Chromeプロファイルを直接使うこともできますが、同時起動やプロファイル破損のリスクがあるため、専用ディレクトリを作成して使うことを推奨します。


### 使い方

前提
- macOS
- Python 3.12+
- Playwright パッケージ（当プロジェクトの依存に含まれます）

セットアップ例
1) 依存をインストール
   ```bash
   pip install -r requirements.lock
   ```

2) Playwrightのブラウザは、システムChromeを使うため必須ではありませんが、Chromiumを使う場合は `playwright install` が必要です。

#### 初回実行（手動ログインする場合）

以下のコマンドで認証モードを有効化し、手動ログインを行います。

```bash
python -m src.interface.cli wiki \
  "https://app.devin.ai/wiki/<your org>/<your repo>" \
  -o ./output \
  --auth \
  --headed \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile" \
  --manual-login \
  --wait-selector "#codebase-wiki-repo-page" \
  --wait-timeout-ms 300000
```

**実行手順:**
1. ブラウザが立ち上がったら以下の手順でログインを完了してください：
   - **GitHubログイン**: github.comにまだログインしていない場合は、認証情報を入力するかSSOを使用
   - **Devinログイン**: app.devin.aiにサインインし、GitHubアカウントまたは他の認証方法を使用
   - **重要**: プライベートリポジトリにアクセスするため、GitHubとDevinの両方にログインする必要があります。DevinはしばしばGitHub認証を要求します
2. 両方のサービスへのログイン完了後、ターミナルに戻って **Enter** を押すとスクレイピングが続行されます

**主要オプション:**
- `--auth`: 永続コンテキストを使用してログイン状態を維持
- `--headed`: ブラウザを表示（初回ログイン時に必要）
- `--manual-login`: 手動でログイン完了を確認してからスクレイピング開始
- `--browser-channel chrome`: システムのGoogle Chromeを使用
- `--user-data-dir`: ログイン状態を保存するディレクトリ（任意の新規ディレクトリ推奨）
- `--wait-selector`: 特定の要素が現れるまで待機（Devin用）
- `--wait-timeout-ms`: 待機タイムアウト（ミリ秒）

#### 2回目以降（ログイン済みプロファイルを再利用して自動化）

ログイン状態が保存されているため、以下のコマンドで自動実行できます。

```bash
python -m src.interface.cli wiki \
  "https://app.devin.ai/wiki/<your org>/<your repo>" \
  -o ./output \
  --auth \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile" \
  --wait-selector "#codebase-wiki-repo-page" \
  --wait-timeout-ms 180000
```

**注意:**
- `--headed` と `--manual-login` は不要（自動でヘッドレス実行）
- 待機時間を短縮（300秒→180秒）

#### macOSの既存Chromeプロファイルを使う場合（上級者向け）

```bash
python -m src.interface.cli wiki \
  "https://app.devin.ai/wiki/<your org>/<your repo>" \
  -o ./output \
  --auth \
  --browser-channel chrome \
  --user-data-dir "$HOME/Library/Application Support/Google/Chrome"
```

**注意:** 既存のChromeを同じプロファイルで同時起動すると競合や破損のリスクがあります。使用中のChromeを終了してから実行するか、専用のプロファイルディレクトリを使ってください。

#### チャットページにも同様に適用可能

**初回（手動ログイン）:**
```bash
python -m src.interface.cli chat \
  "<チャットページURL>" \
  -o ./output \
  --auth \
  --headed \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile" \
  --manual-login
```

**2回目以降（自動化）:**
```bash
python -m src.interface.cli chat \
  "<チャットページURL>" \
  -o ./output \
  --auth \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile"
```

#### トラブルシューティング

**`--browser-channel chrome` でエラーが出る場合:**
- システムにChromeがインストールされているか確認
- 代替案1: Playwrightのchromeチャンネルをインストール（任意）
- 代替案2: `--browser-channel chromium` を使用（`python -m playwright install chromium` が必要な場合あり）

**ログインの問題:**
- **GitHub認証が必要**: DevinのWikiであっても、リポジトリアクセス認証のためにまずGitHubにログインする必要がある場合があります
- **複数のログイン手順**: プライベートリポジトリの場合、以下の両方にログインしていることを確認してください：
  1. GitHub (github.com) - リポジトリアクセス権限のため
  2. Devin (app.devin.ai) - Devinプラットフォーム自体のため
- **セッションタイムアウト**: ログイン成功後にスクレイピングが失敗する場合、セッションが期限切れになっている可能性があります。`--manual-login` で再実行して認証を更新してください

**ナビゲーション抽出について:**
- サイドバーにナビゲーションが無いUIでも、`/wiki/{org}/{repo}/` 配下のリンクを本文からフォールバック抽出します
- 最初に開くURLはリポジトリのトップWiki（目次に相当）だと精度が上がります

### 既知の制限と今後の改善
- Wiki本文内の画像が認証下にありローカルに保存されない場合、Markdownでは外部URLのまま参照されます。将来的に、Playwrightのページコンテキストを用いた画像のダウンロードとローカル参照への書き換えを追加予定です。
- Devin上のDOM構造が変更された場合、セレクタの調整が必要になる可能性があります。

## 2. コマンドライン仕様

基本的なコマンド構文は以下です。
```bash
python -m src.interface.cli <サブコマンド> <URL> [-o <出力ベースディレクトリ>]
```

* `<サブコマンド>`: `wiki` または `chat` を指定します。
* `<URL>`: 対象のDeepWikiページのURLを指定します。
* `-o <出力ベースディレクトリ>` (オプション): Markdownファイルや画像が出力されるベースディレクトリを指定します。デフォルトは`./output`です。

**例:**

* **リポジトリWikiの取得**:
    ```bash
    python -m src.interface.cli wiki https://deepwiki.com/yourgroup/yourrepo
    ```
    出力先: `./output/wiki/yourgroup/yourrepo/`

* **チャットログの取得**:
    ```bash
    python -m src.interface.cli chat https://deepwiki.com/search/yourchatid
    ```
    出力先: `./output/chat/yourchatid/`

* **出力ベースディレクトリを指定してリポジトリWikiを取得**:
    ```bash
    python -m src.interface.cli wiki https://deepwiki.com/yourgroup/yourrepo -o /path/to/custom_output
    ```
    出力先: `/path/to/custom_output/wiki/yourgroup/yourrepo/`

**出力ディレクトリ構造のイメージ:**

```
output/  ※デフォルトの出力ディレクトリ
    wiki/
        yourgroup/
            yourrepo/
                1-overview.md
                2-details.md
                images/
                    diagram1.svg
    chat/
        yourchatid/
            chat.md
            images/
                diagram1.svg
```

## 3. 参考

このプロジェクトは[deepwiki-to-md](https://github.com/suwa-sh/deepwiki-to-md)を参考に、export-private-repositoryとして変更したものです。