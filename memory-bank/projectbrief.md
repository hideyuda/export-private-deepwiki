# プロジェクト概要 - deepwiki-to-md

## 目的

deepwiki-to-mdは、DeepWikiのコンテンツ（リポジトリのWikiやチャットログ）をMarkdown形式でローカルに保存するためのCLIツールです。このプロジェクトにより、ユーザーはDeepWiki上の価値ある情報を簡単にエクスポートし、ローカル環境で管理・活用できるようになります。

## 主要目標

1. DeepWikiのチャットログをMarkdown形式で取得可能にする
2. DeepWikiのWikiコンテンツをMarkdown形式で取得可能にする
3. Mermaid図などの特殊要素を適切に保存・変換する
4. シンプルなCLIインターフェースを提供する
5. Dockerによる環境差異の吸収と簡単なセットアップを実現する

## 技術スコープ

- Python 3.12ベースの実装
- Playwright を使用したWebブラウザの自動操作
- BeautifulSoup4 によるHTML解析
- markdownify によるHTML→Markdown変換
- クリーンアーキテクチャに基づいた設計

## 提供形態

1. **Dockerイメージ (`suwash/deepwiki-to-md:latest`)**:
   - ツール本体（Pythonスクリプト、Playwright、必要なブラウザドライバ、その他依存ライブラリ）
   - Docker Hubで公開

2. **ラッパースクリプト (`deepwiki-to-md`)**:
   - ユーザーが直接ダウンロードして利用するシェルスクリプト
   - Dockerコマンドの実行を抽象化
   - GitHub Pagesやリリースページで配布

## コマンドライン仕様

基本的なコマンド構文:
```bash
./deepwiki-to-md <サブコマンド> <URL>
```

例:
- **リポジトリWikiの取得**: `./deepwiki-to-md repo https://deepwiki.com/yourgroup/yourrepo`
- **チャットログの取得**: `./deepwiki-to-md chat https://deepwiki.com/search/yourchatid`

## 開発ロードマップ

1. ~~開発環境のDevcontainer化~~ (完了)
2. `deepwiki-to-md chat`のPoCスクリプトをリファクタリング
3. `deepwiki-to-md wiki`の実装
4. 本番用Dockerイメージの作成と公開
5. ドキュメント整備

## 品質基準

- 利用者にとって簡単な操作性
- 出力されるMarkdownの高い可読性
- DeepWikiコンテンツの正確な変換
- 拡張性と保守性の高いコード設計
- 適切なテストカバレッジ
