## 開発環境

### Devcontainer設定

- Python 3.12ベースの開発環境
- `.devcontainer/Dockerfile`: 開発コンテナのビルド定義
  - Python 3.12
  - Playwrightとブラウザ（Chromium）
  - システム依存関係（libwebkit2gtk-4.0-dev, build-essential, curl）

- `.devcontainer/devcontainer.json`: VSCodeとの連携設定
  - remoteUserとして`root`を使用
  - GitHub CLI機能を追加
  - VSCode拡張機能：Python, Pylance, Ruff
  - フォーマット設定：Ruffを使用したコード自動整形

### 依存関係管理

- `requirements.txt`: 本番環境の依存関係
  - playwright>=1.40.0
  - beautifulsoup4>=4.12.2
  - markdownify>=0.11.6

- `requirements.dev.txt`: 開発環境の追加依存関係
  - rye>=0.15.0
  - ruff>=0.1.5
  - pytest>=7.4.3

### 開発ツール

- rye: Python環境管理
- ruff: リンター・フォーマッター
- pytest: テストフレームワーク
