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

1. `deepwiki-to-md wiki`の実装 (現在の作業)
   - URLパターン: https://deepwiki.com/{organization}/{repository}
   - 出力構造:
     ```
     wiki/
     └── {organization}/
         └── {repository}/
             ├── 1-{page-name}.md
             ├── 2-{page-name}.md
             └── images/
                 ├── 1-{page-name}_diagram_1.svg
                 ├── 1-{page-name}_diagram_2.svg
                 └── 2-{page-name}_diagram_1.svg
     ```
   - 具体的な実装計画:
     1. ドメイン層の拡張
       - `WikiPage`クラス: ページタイトル、コンテンツ、URL、ページ番号、図表リスト
       - `WikiSite`クラス: 組織名、リポジトリ名、ページコレクション
     2. リポジトリ層とゲートウェイ層の拡張
       - ナビゲーション抽出機能
       - Wikiページコンテンツ抽出
       - Mermaid図の処理
     3. ユースケース層の実装
       - `ConvertWikiSiteToMarkdownUsecase`の新規作成
       - ページコレクション処理ロジック
     4. インターフェース層の拡張
       - `wiki`サブコマンドの追加

2. 本番用Dockerコンテナの作成とイメージ公開

## `deepwiki-to-md wiki`の詳細実装計画

### ドメイン層の拡張

```python
@dataclass
class WikiPage:
    title: str
    content: str
    url: str
    page_number: int  # ページ番号（出力ファイル名の接頭辞用）
    diagrams: List[MermaidDiagram]  # ページ内のMermaid図リスト
    
@dataclass
class WikiSite:
    organization: str  # URLから抽出する組織名（例: langchain-ai）
    repository: str    # URLから抽出するリポジトリ名（例: langchain）
    pages: List[WikiPage]  # Wikiサイト内の全ページ
    
    def add_page(self, page: WikiPage) -> None:
        self.pages.append(page)
    
    def get_output_directory(self, base_dir: str) -> str:
        # 出力ディレクトリパスの生成（例: wiki/langchain-ai/langchain/）
        return os.path.join(base_dir, "wiki", self.organization, self.repository)
```

### ユースケース層の実装

```python
# src/usecase/wiki_site_usecase.py
class ConvertWikiSiteToMarkdownUsecase:
    def __init__(
        self,
        web_repository: WebRepository,
        html_repository: HtmlRepository,
        markdown_repository: MarkdownRepository,
        file_repository: FileRepository,
    ):
        self.web_repository = web_repository
        self.html_repository = html_repository
        self.markdown_repository = markdown_repository
        self.file_repository = file_repository
        
    def execute(self, url: str, output_base_dir: str) -> None:
        # 1. WikiサイトのURLから組織名とリポジトリ名を抽出
        wiki_site = self._extract_site_info(url)
        
        # 2. メインページのHTMLを取得
        main_page_html = self.web_repository.fetch_content(url)
        
        # 3. ナビゲーションメニューからすべてのページリンクを抽出
        navigation_links = self.html_repository.extract_wiki_navigation(main_page_html)
        
        # 4. 出力ディレクトリ構造を作成
        output_dir = wiki_site.get_output_directory(output_base_dir)
        images_dir = os.path.join(output_dir, "images")
        self.file_repository.ensure_directory(output_dir)
        self.file_repository.ensure_directory(images_dir)
        
        # 5. 各ページを処理
        for page_num, page_link in enumerate(navigation_links, 1):
            page_url = page_link["url"]
            page_title = page_link["title"]
            
            # 5.1. ページコンテンツの取得
            page_html = self.web_repository.fetch_content(page_url)
            
            # 5.2. ページコンテンツの解析とMermaid図の抽出
            wiki_page = self.html_repository.extract_wiki_page(
                page_html, 
                title=page_title, 
                url=page_url,
                page_number=page_num
            )
            
            # 5.3. Markdownへの変換
            markdown_content = self.markdown_repository.convert_wiki_to_markdown(wiki_page)
            
            # 5.4. Markdownファイルの保存
            page_filename = f"{page_num}-{self._sanitize_filename(page_title)}.md"
            page_filepath = os.path.join(output_dir, page_filename)
            self.file_repository.save_markdown(markdown_content, page_filepath)
            
            # 5.5. Mermaid図の保存
            for diagram_idx, diagram in enumerate(wiki_page.diagrams, 1):
                diagram_filename = f"{page_num}-{self._sanitize_filename(page_title)}_diagram_{diagram_idx}.svg"
                diagram_filepath = os.path.join(images_dir, diagram_filename)
                self.file_repository.save_svg(diagram.svg_content, diagram_filepath)
                
                # Markdown内の図参照パスを更新
                relative_diagram_path = f"images/{diagram_filename}"
                markdown_content = markdown_content.replace(diagram.placeholder, f"![diagram]({relative_diagram_path})")
                
            # 更新したMarkdownを保存（図参照パス更新後）
            self.file_repository.save_markdown(markdown_content, page_filepath)
            
            # WikiSiteにページを追加
            wiki_site.add_page(wiki_page)
```

### リポジトリ層とゲートウェイ層の拡張

```python
# src/repository/html_repository.py (拡張)
def extract_wiki_navigation(self, html_content: str) -> List[Dict[str, str]]:
    """
    Wikiページのナビゲーションメニューからすべてのページリンクを抽出
    
    Returns:
        List[Dict[str, str]]: [{"title": "ページタイトル", "url": "ページURL"}, ...]
    """
    return self.html_adapter.extract_wiki_navigation(html_content)

def extract_wiki_page(self, html_content: str, title: str, url: str, page_number: int) -> WikiPage:
    """
    WikiページのHTML内容を解析し、WikiPageオブジェクトを作成
    
    Returns:
        WikiPage: 解析されたWikiページ
    """
    content_html = self.html_adapter.extract_wiki_content(html_content)
    diagrams = self.html_adapter.extract_mermaid_diagrams(html_content)
    
    return WikiPage(
        title=title,
        content=content_html,
        url=url,
        page_number=page_number,
        diagrams=diagrams
    )

# src/gateway/html_adapter.py (拡張)
def extract_wiki_navigation(self, html_content: str) -> List[Dict[str, str]]:
    """
    ナビゲーションメニューからページリンクを抽出
    
    Returns:
        List[Dict[str, str]]: ページリンク情報
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    navigation_links = []
    
    # ナビゲーションメニューの抽出 (実際のHTMLに合わせて調整)
    nav_container = soup.select_one('.wiki-navigation')
    if nav_container:
        links = nav_container.select('a')
        for i, link in enumerate(links, 1):
            href = link.get('href')
            # 相対パスの場合は絶対URLに変換
            if href and not href.startswith('http'):
                href = urljoin("https://deepwiki.com", href)
            
            navigation_links.append({
                "title": link.get_text().strip(),
                "url": href
            })
    
    return navigation_links
```

### インターフェース層の拡張

```python
# src/interface/cli.py の拡張
def execute_wiki_command(url: str, output_dir: str = None):
    """WikiページをMarkdownに変換するコマンド実行"""
    try:
        # 依存コンポーネント初期化
        file_adapter = FileAdapter()
        web_adapter = WebAdapter()
        html_adapter = HtmlAdapter()
        markdown_adapter = MarkdownAdapter()
        
        file_repository = FileRepository(file_adapter)
        web_repository = WebRepository(web_adapter)
        html_repository = HtmlRepository(html_adapter)
        markdown_repository = MarkdownRepository(markdown_adapter)
        
        # デフォルト出力ディレクトリ (カレントディレクトリ)
        if not output_dir:
            output_dir = os.getcwd()
        
        # ユースケース実行
        usecase = ConvertWikiSiteToMarkdownUsecase(
            web_repository,
            html_repository,
            markdown_repository,
            file_repository
        )
        
        wiki_site = usecase.execute(url, output_dir)
        
        # 結果出力
        print(f"Successfully converted Wiki from {url}")
        print(f"Output directory: {wiki_site.get_output_directory(output_dir)}")
        print(f"Total pages: {len(wiki_site.pages)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
```

### 実装優先順位

1. **スケルトンコード作成**:
   - ドメインクラス（`WikiPage`, `WikiSite`）の実装
   - リポジトリとアダプターの基本メソッド追加

2. **ナビゲーション抽出**:
   - DeepWikiのHTML構造の分析
   - ナビゲーションメニュー抽出の実装
   - URLとページタイトルの抽出

3. **ページコンテンツ処理**:
   - 個別ページのコンテンツ抽出
   - Mermaid図の検出と処理
   - 画像パスの相対化

4. **Markdown変換と保存**:
   - ページコンテンツのMarkdown変換
   - ディレクトリ構造の生成
   - ファイル命名規則の実装

5. **統合とテスト**:
   - 各コンポーネントの統合
   - 実際のDeepWikiページでのテスト

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
