# export-private-deepwiki

## 1. 概要

`deepwiki-to-md`は、DeepWikiのコンテンツ（リポジトリのWikiやチャットログ）をMarkdown形式でローカルに保存するためのCLIツールです。
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

注意（Dockerについて）
- 非公開ページの取得では、ホストのログイン済みブラウザ環境を使う必要があるため、Dockerイメージ経由ではなく「ローカル実行（Python）」での利用を推奨します（コンテナ内でChromeを起動してホストのプロファイルを共有するのは非推奨/非対応）。

### 使い方（ローカル実行）

前提
- macOS
- Python 3.12+
- Playwright パッケージ（当プロジェクトの依存に含まれます）

セットアップ例
1) 依存をインストール

     （任意の環境で）
     - pip等でインストールしてください。

2) Playwrightのブラウザは、システムChromeを使うため必須ではありませんが、Chromiumを使う場合は `playwright install` が必要です。

サンプル（Devin上の非公開Wiki）

以下のように、--auth オプションで認証モードを有効化します。初回は --headed を付けてログインを完了してください。

```
python -m src.interface.cli wiki \
    "https://app.devin.ai/wiki/sakuraaiinc/scoutbird-temp" \
    -o ./output \
    --auth \
    --headed \
    --browser-channel chrome \
    --user-data-dir "$HOME/.deepwiki-playwright-profile"
```

- --auth: 永続コンテキストを使用してログイン状態を維持
- --headed: ブラウザを表示（初回ログイン時に便利）
- --browser-channel chrome: システムのGoogle Chromeを使用
- --user-data-dir: ログイン状態を保存するディレクトリ（任意の新規ディレクトリ推奨）

ログイン完了後は --headed を外して自動実行できます。

```
python -m src.interface.cli wiki \
    "https://app.devin.ai/wiki/sakuraaiinc/scoutbird-temp" \
    -o ./output \
    --auth \
    --browser-channel chrome \
    --user-data-dir "$HOME/.deepwiki-playwright-profile"
```

macOSの既存Chromeプロファイルを使う場合（上級者向け）

```
python -m src.interface.cli wiki \
    "https://app.devin.ai/wiki/sakuraaiinc/scoutbird-temp" \
    -o ./output \
    --auth \
    --browser-channel chrome \
    --user-data-dir "$HOME/Library/Application Support/Google/Chrome"
```

注: 既存のChromeを同じプロファイルで同時起動すると競合や破損のリスクがあります。使用中のChromeを終了してから実行するか、専用のプロファイルディレクトリを使ってください。

### chatにも同様に適用可能

```
python -m src.interface.cli chat \
    "<チャットページURL>" \
    -o ./output \
    --auth \
    --browser-channel chrome \
    --user-data-dir "$HOME/.deepwiki-playwright-profile"
```

### 既知の制限と今後の改善
- Wiki本文内の画像が認証下にありローカルに保存されない場合、Markdownでは外部URLのまま参照されます。将来的に、Playwrightのページコンテキストを用いた画像のダウンロードとローカル参照への書き換えを追加予定です。
- Devin上のDOM構造が変更された場合、セレクタの調整が必要になる可能性があります。

## 2. Getting Started

### 2.1. インストール

1.  **前提条件**:
    * Dockerがインストールされていること
2.  **ラッパースクリプトのダウンロード**:
    * 任意のディレクトリに配置します。
        ```bash
        # 例: ~/my_deepwiki_exports に配置する場合
        mkdir -p ~/my_deepwiki_exports
        curl -Lo ~/my_deepwiki_exports/deepwiki-to-md https://raw.githubusercontent.com/suwa-sh/deepwiki-to-md/refs/heads/main/bin/deepwiki-to-md
        chmod +x ~/my_deepwiki_exports/deepwiki-to-md
        ```
3.  **ツールの実行**:
    * **リポジトリWikiの取得例**:
        ```bash
        ~/my_deepwiki_exports/deepwiki-to-md wiki https://deepwiki.com/yourgroup/yourrepo
        ```
    * **チャットログの取得例**:
        ```bash
        ~/my_deepwiki_exports/deepwiki-to-md chat https://deepwiki.com/search/yourchatid
        ```

### 2.1. 提供物

1.  **Dockerイメージ (suwash/deepwiki-to-md)**
    * ツール本体のPythonスクリプト、Playwright、必要なブラウザドライバ、その他依存ライブラリを全て含みます。
    * Docker Hubで公開しています。
      * [suwash/deepwiki-to-md](https://hub.docker.com/r/suwash/deepwiki-to-md)
2.  **ラッパースクリプト (`deepwiki-to-md`)**
    * ユーザーが直接ダウンロードして利用するシェルスクリプトです。
    * このスクリプトがDockerコマンドの実行を抽象化します。
    * GitHubで管理しています。
      * [bin/deepwiki-to-md](bin/deepwiki-to-md)

### 2.2. システム構成と動作フロー

以下の図は、`deepwiki-to-md`のシステム構成とユーザーがコマンドを実行した際の動作フローを示します。

```mermaid
graph TD
    User[ユーザー] -- 1.準備 --> HostFS[出力ディレクトリ]
    User[ユーザー] -- 2.実行 --> WrapperScript[ラッパースクリプト]
    WrapperScript -- 3.起動 --> DockerContainer[コンテナ]
    HostFS -.->|4.ボリュームマウント| ContainerFS
    DockerContainer -- 5.実行 --> PythonScript[Pythonスクリプト]
    PythonScript -- 7.変換 --> ContainerFS[出力ディレクトリ]
    PythonScript -- 6.コンテンツ取得 --> DeepWiki[DeepWiki]
    ContainerFS -.->|8.永続化| HostFS

    subgraph ホストマシン
        WrapperScript
        HostFS
    end

    subgraph Docker
        DockerContainer
        PythonScript
        ContainerFS
    end

```

**ディレクトリ構造のイメージ（ユーザーのホストマシン上）:**

```
任意のディレクトリ/  ※例: ~/my_deepwiki_exports/
    deepwiki-to-md      <-- ラッパースクリプト本体
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

## 3. コマンドライン仕様

基本的なコマンド構文は以下です。
```bash
./deepwiki-to-md <サブコマンド> <URL> [-o <出力ベースディレクトリ>]
```

* `<サブコマンド>`: `wiki` または `chat` を指定します。
* `<URL>`: 対象のDeepWikiページのURLを指定します。
* `-o <出力ベースディレクトリ>` (オプション): Markdownファイルや画像が出力されるベースディレクトリを指定します。デフォルトはラッパースクリプトを配置したディレクトリです。

**例:**

* **リポジトリWikiの取得**:
    ```bash
    ./deepwiki-to-md wiki https://deepwiki.com/yourgroup/yourrepo
    ```
    出力先: `./wiki/yourgroup/yourrepo/`

* **チャットログの取得**:
    ```bash
    ./deepwiki-to-md chat https://deepwiki.com/search/yourchatid
    ```
    出力先: `./chat/yourchatid/`

* **出力ベースディレクトリを指定してリポジトリWikiを取得**:
    ```bash
    ./deepwiki-to-md wiki https://deepwiki.com/yourgroup/yourrepo -o /path/to/custom_output
    ```
    出力先: `/path/to/custom_output/wiki/yourgroup/yourrepo/`
