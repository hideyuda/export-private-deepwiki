# ベースイメージとしてPython 3.12を使用
FROM python:3.12-slim AS builder

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY pyproject.toml README.md .

# 依存関係をインストール（ビルド用）
RUN pip install --no-cache-dir .



# 本番イメージ
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
RUN apt-get update && \
  apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*
  # wget \
  # gnupg \

# Playwrightとブラウザをインストール
RUN pip install --no-cache-dir playwright && \
  playwright install --with-deps chromium

# ビルダーステージから依存関係をコピー
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリケーションコードをコピー
COPY src/ /app/src/
COPY bin/ /app/bin/
COPY pyproject.toml /app/

# 実行権限を付与
RUN chmod +x /app/bin/deepwiki-to-md

# 環境変数を設定
ENV PYTHONPATH=/app

# エントリーポイントを設定
ENTRYPOINT ["src/interface/cli.py"]

# デフォルトコマンド（ヘルプを表示）
CMD ["--help"]
