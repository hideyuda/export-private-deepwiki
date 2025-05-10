#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usecase for converting a chat page to markdown.
"""

import os
from src.domain.entities import ChatLog
from src.repository.web_repository import WebRepository
from src.repository.html_repository import HtmlRepository
from src.repository.markdown_repository import MarkdownRepository
from src.repository.file_repository import FileRepository


class ConvertChatPageToMarkdownUsecase:
    """
    Usecase for converting a web page's chat content to a Markdown document.
    """

    def __init__(
        self,
        web_repository: WebRepository,
        html_repository: HtmlRepository,
        markdown_repository: MarkdownRepository,
        file_repository: FileRepository,
    ):
        """
        Initialize the usecase with repositories.

        Args:
            web_repository: For fetching web content.
            html_repository: For parsing HTML content.
            markdown_repository: For converting to markdown.
            file_repository: For file operations.
        """
        self.web_repository = web_repository
        self.html_repository = html_repository
        self.markdown_repository = markdown_repository
        self.file_repository = file_repository

    async def execute(self, url: str, output_md_filepath: str) -> None:
        """
        Executes the usecase to convert a chat page to markdown.

        Args:
            url: The URL of the chat page.
            output_md_filepath: The path to save the markdown file.
        """
        print("Starting the HTML to Markdown conversion process...")
        print(f"Target URL: {url}")
        print(f"Output Markdown File: {output_md_filepath}")

        # Ensure output directory exists
        output_md_dir = self.file_repository.ensure_output_directory(output_md_filepath)
        print(
            f"SVG files will be saved in an 'images' subdirectory within: {output_md_dir}"
        )

        # Fetch page content
        page_html = await self.web_repository.fetch_content(url)
        if not page_html:
            print("Failed to retrieve page content. Exiting.")
            return

        print("Page content retrieved, parsing HTML...")

        # Extract chat blocks
        chat_blocks = self.html_repository.extract_chat_blocks(page_html, output_md_dir)

        if not chat_blocks:
            print("No chat blocks found. Exiting.")
            return

        print(f"Found {len(chat_blocks)} chat block(s). Processing...")

        # Create chat log
        chat_log = ChatLog()
        for block in chat_blocks:
            chat_log.add_chat_block(block)

        # Convert to markdown
        final_markdown = self.markdown_repository.convert_chat_log_to_markdown(chat_log)

        if not final_markdown.strip():
            print(
                "No content was extracted to Markdown. The output file will be empty or not created."
            )
            return

        # Save markdown to file
        self.file_repository.save_markdown(final_markdown, output_md_filepath)
