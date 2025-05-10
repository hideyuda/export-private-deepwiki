#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI interface for deepwiki-to-md.
"""

import argparse
import asyncio
import sys

from src.usecase.chat_page_usecase import ConvertChatPageToMarkdownUsecase
from src.gateway.web_adapter import WebAdapter
from src.gateway.html_adapter import HtmlAdapter
from src.gateway.markdown_adapter import MarkdownAdapter
from src.gateway.file_adapter import FileAdapter
from src.repository.web_repository import WebRepository
from src.repository.html_repository import HtmlRepository
from src.repository.markdown_repository import MarkdownRepository
from src.repository.file_repository import FileRepository


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DeepWiki chat content to Markdown converter."
    )
    parser.add_argument("url", help="The URL of the DeepWiki search page to process.")
    parser.add_argument("output_file", help="The path to the output Markdown file.")
    return parser.parse_args()


async def run_cli():
    """Run the CLI application."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Initialize adapters
        web_adapter = WebAdapter()
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
        await usecase.execute(args.url, args.output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def main():
    """Main entry point for the CLI application."""
    return asyncio.run(run_cli())


if __name__ == "__main__":
    sys.exit(main())
