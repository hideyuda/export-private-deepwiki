## 完了

- ✅ devcontainer化 (2025/5/10完了)
  - PoC時の依存を含める
    - python 3.12
    - playwright
  - `.devcontainer/Dockerfile`と`.devcontainer/devcontainer.json`を作成
  - `project.toml`を整備

- ✅ `deepwiki-to-md chat`のPoCスクリプトをファイル分割 & リファクタリング (2025/5/10完了)
  - クリーンアーキテクチャに基づいた構造へ移行
  - モジュール分割と責務の明確化
  - テスト環境の構築
  - 全ての機能を維持したままのリファクタリング完了

## ToDo

- `deepwiki-to-md wiki`を実装
- コンテナ化
- container image公開
- ドキュメント整備
