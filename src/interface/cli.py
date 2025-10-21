#!/usr/bin/env python3
# ruff: noqa: T201, D401, D400

"""CLI interface for deepwiki-to-md."""

import argparse
import asyncio
import sys
from pathlib import Path

from src.usecase.chat_page_usecase import ConvertChatPageToMarkdownUsecase
from src.usecase.wiki_site_usecase import ConvertWikiSiteToMarkdownUsecase
from src.gateway.web_adapter import WebAdapter
from src.gateway.html_adapter import HtmlAdapter
from src.gateway.markdown_adapter import MarkdownAdapter
from src.gateway.file_adapter import FileAdapter
from src.repository.web_repository import WebRepository
from src.repository.html_repository import HtmlRepository
from src.repository.markdown_repository import MarkdownRepository
from src.repository.file_repository import FileRepository


def _add_auth_options(subparser: argparse.ArgumentParser) -> None:
    """Add authentication/browser options to a subparser."""
    subparser.add_argument(
        "--auth",
        action="store_true",
        help=(
            "Use a persistent browser context (reuse cookies) to access private pages."
        ),
    )
    subparser.add_argument(
        "--user-data-dir",
        dest="user_data_dir",
        default=None,
        help=(
            "Path to a browser user data directory to reuse login state (e.g., your "
            "Chrome profile)."
        ),
    )
    subparser.add_argument(
        "--browser-channel",
        dest="browser_channel",
        choices=["chrome", "chromium", "msedge"],
        default=None,
        help="Browser channel to use. Use 'chrome' to leverage your system Chrome.",
    )
    subparser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode (visible window) instead of headless.",
    )
    subparser.add_argument(
        "--browser-arg",
        dest="browser_args",
        action="append",
        default=None,
        help="Extra argument to pass to the browser (can be specified multiple times).",
    )
    subparser.add_argument(
        "--manual-login",
        action="store_true",
        help=(
            "Pause and wait for manual login confirmation (press Enter in the terminal) "
            "when using --auth and --headed."
        ),
    )
    subparser.add_argument(
        "--wait-selector",
        dest="wait_selector",
        default=None,
        help=(
            "CSS selector to wait for after navigation (e.g., a content container) to "
            "ensure the page has fully loaded."
        ),
    )
    subparser.add_argument(
        "--wait-timeout-ms",
        dest="wait_timeout_ms",
        type=int,
        default=300000,
        help="Timeout in milliseconds for --wait-selector (default: 300000).",
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DeepWiki content to Markdown converter.",
    )

    # サブコマンドを設定
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # chatコマンド - チャットページをMarkdownに変換
    chat_parser = subparsers.add_parser("chat", help="Convert chat page to Markdown")
    chat_parser.add_argument("url", help="URL of the chat page")
    chat_parser.add_argument(
        "-o",
        "--output",
        help="Output directory path (default: current directory)",
        default=str(Path.cwd()),
    )

    # wikiコマンド - WikiサイトをMarkdownに変換
    wiki_parser = subparsers.add_parser("wiki", help="Convert wiki site to Markdown")
    wiki_parser.add_argument("url", help="URL of the wiki site")
    wiki_parser.add_argument(
        "-o",
        "--output",
        help="Output directory path (default: current directory)",
        default=str(Path.cwd()),
    )

    # Add shared auth/browser options to both subcommands
    _add_auth_options(chat_parser)
    _add_auth_options(wiki_parser)

    # コマンドが指定されていない場合のデフォルトヘルプ
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


async def execute_chat_command(
    url: str,
    output_dir: str,
    args: argparse.Namespace,
) -> None:
    """chatコマンドを実行する."""
    # Initialize adapters
    web_adapter = WebAdapter(
        use_persistent_context=args.auth,
        user_data_dir=args.user_data_dir,
        browser_channel=args.browser_channel,
        headless=not args.headed,
        browser_args=args.browser_args or [],
        manual_login=args.manual_login,
        wait_selector=args.wait_selector,
        wait_timeout_ms=args.wait_timeout_ms,
    )
    html_adapter = HtmlAdapter()
    markdown_adapter = MarkdownAdapter()
    file_adapter = FileAdapter()

    # Initialize repositories
    web_repository = WebRepository(web_adapter)
    html_repository = HtmlRepository(html_adapter)
    markdown_repository = MarkdownRepository(markdown_adapter)
    file_repository = FileRepository(file_adapter)

    # Initialize usecase
    usecase = ConvertChatPageToMarkdownUsecase(
        web_repository,
        html_repository,
        markdown_repository,
        file_repository,
    )

    # Execute the usecase
    await usecase.execute(url, output_dir)


async def execute_wiki_command(
    url: str,
    output_dir: str,
    args: argparse.Namespace,
) -> None:
    """wikiコマンドを実行する."""
    # Initialize adapters
    web_adapter = WebAdapter(
        use_persistent_context=args.auth,
        user_data_dir=args.user_data_dir,
        browser_channel=args.browser_channel,
        headless=not args.headed,
        browser_args=args.browser_args or [],
        manual_login=args.manual_login,
        wait_selector=args.wait_selector,
        wait_timeout_ms=args.wait_timeout_ms,
    )
    html_adapter = HtmlAdapter()
    markdown_adapter = MarkdownAdapter()
    file_adapter = FileAdapter()

    # Initialize repositories
    web_repository = WebRepository(web_adapter)
    html_repository = HtmlRepository(html_adapter)
    markdown_repository = MarkdownRepository(markdown_adapter)
    file_repository = FileRepository(file_adapter)

    # Initialize usecase
    usecase = ConvertWikiSiteToMarkdownUsecase(
        web_repository,
        html_repository,
        markdown_repository,
        file_repository,
    )

    # Execute the usecase
    await usecase.execute(url, output_dir)


async def run_cli() -> int:
    """Run the CLI application."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # コマンドに応じて処理を分岐
        if args.command == "chat":
            await execute_chat_command(args.url, args.output, args)
        elif args.command == "wiki":
            await execute_wiki_command(args.url, args.output, args)
        else:
            print("Error: Unknown command. Use 'chat' or 'wiki'.")
            return 1
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def main() -> int:
    """Run the CLI application."""
    return asyncio.run(run_cli())


if __name__ == "__main__":
    sys.exit(main())
