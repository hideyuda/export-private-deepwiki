# ActiveContext - deepwiki-to-md

## 現在の焦点

- 開発環境の整備（Devcontainer化）が完了
- `src/PoC__deepwiki-to-md_chat.py`のリファクタリングとモジュール分割が完了
- 現在の作業: `deepwiki-to-md wiki`機能の実装準備

## 実装済みアーキテクチャ (2025/5/10)

以下の層構造とディレクトリ構成で実装を進める:

```
src/
├── domain/
│   ├── __init__.py
│   ├── constants.py          # SVG処理などの定数
│   └── entities.py           # すべてのエンティティクラス
│
├── usecase/
│   ├── __init__.py
│   └── chat_page_usecase.py  # ChatPageToMarkdownUsecase
│
├── repository/
│   ├── __init__.py
│   ├── web_repository.py     # WebRepository
│   ├── html_repository.py    # HtmlRepository
│   ├── markdown_repository.py # MarkdownRepository
│   └── file_repository.py    # FileRepository
│
├── gateway/
│   ├── __init__.py
│   ├── web_adapter.py        # WebAdapter (Playwright使用)
│   ├── html_adapter.py       # HtmlAdapter (BeautifulSoup使用)
│   ├── markdown_adapter.py   # MarkdownAdapter (markdownify使用)
│   └── file_adapter.py       # FileAdapter (os操作)
│
└── interface/
    ├── __init__.py
    └── cli.py                # CLI処理と例外ハンドリング
```

### 各層の責務

- **ドメイン層**: ビジネスロジックとエンティティを含む（MermaidDiagram, ChatBlockContent等）
- **ユースケース層**: ドメインとリポジトリを利用する手順のみ実装
- **リポジトリ層**: 外部リソースとドメインオブジェクトの変換、ゲートウェイ層のアダプターを利用
- **ゲートウェイ層**: 外部システム（ライブラリ）との通信を担当するアダプター
- **インターフェース層**: CLIインターフェースと例外処理

### 設計上の決定事項

1. **Repository関数**:
   - 入力と出力はドメイン層の型を使用
   - 外部依存（アダプター）の結果をドメインオブジェクトに変換

2. **Usecase**:
   - ドメイン層とRepositoryを組み合わせる手順のみ実装
   - 複雑なビジネスロジックはドメイン層に移動

3. **例外処理**:
   - 基本的には`cli`レイヤーでのみ例外をキャッチ
   - アダプターでは必要に応じてリトライのために例外処理

4. **モジュール分割**:
   - 単一責任の原則に従い、各クラスが特定の役割に特化
   - 依存関係を明示的に管理し、循環依存を回避

## 最近の変更 (2025/5/10)

- Devcontainer環境の構築
  - `.devcontainer/Dockerfile` - Python 3.12とPlaywrightを含む開発環境
  - `.devcontainer/devcontainer.json` - VSCode設定
  - 依存関係管理の整備 - `requirements.txt`と`requirements.dev.txt`の分離

- `src/PoC__deepwiki-to-md_chat.py`のリファクタリング完了
  - クリーンアーキテクチャに基づく設計と実装
  - モジュール分割と依存関係の整理
  - テスト・検証環境の整備:
    - `src/test_integration.py` - アーキテクチャの統合テスト
    - `src/test_deps.py` - 依存関係の検証

## 次のステップ

1. `deepwiki-to-md wiki`の実装
   - このモジュールは新規実装となるため、テスト駆動開発を適用
   - ドメインモデルの拡張
   - Wikiページのクローリング機能の実装
   - Wikiコンテンツの抽出機能
   - Markdown変換ロジック

2. 本番用Dockerコンテナの作成とイメージ公開

## 既存の設計上の決定事項

- 開発と本番で依存関係を明確に分離
- Playwrightを使用してDeepWikiコンテンツにアクセス
  - ブラウザ自動化によりSPAコンテンツも取得可能
- クリーンアーキテクチャの採用
  - ドメイン層、リポジトリ層、ゲートウェイ層、ユースケース層の分離
  - テスト容易性の向上

## 開発上の注意点

- VSCode DevContainerを使用して開発環境を統一
- コード品質維持のためRuffを使用したフォーマットとリンティング
- テスト駆動開発を推奨
