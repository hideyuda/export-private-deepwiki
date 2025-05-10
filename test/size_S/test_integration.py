#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple integration test for deepwiki-to-md refactored code.
Tests that the core dependencies and modules can be imported successfully.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gateway.web_adapter import WebAdapter
from src.gateway.html_adapter import HtmlAdapter
from src.gateway.markdown_adapter import MarkdownAdapter
from src.gateway.file_adapter import FileAdapter
from src.repository.web_repository import WebRepository
from src.repository.html_repository import HtmlRepository
from src.repository.markdown_repository import MarkdownRepository
from src.repository.file_repository import FileRepository
from src.usecase.chat_page_usecase import ConvertChatPageToMarkdownUsecase


async def test_structures():
    """Test that the core structures can be created."""
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
        web_repository, html_repository, markdown_repository, file_repository
    )

    # Check all components have been created
    print("\nTesting component initialization:")
    components = [
        web_adapter,
        html_adapter,
        markdown_adapter,
        file_adapter,
        web_repository,
        html_repository,
        markdown_repository,
        file_repository,
        usecase,
    ]

    all_created = all(component is not None for component in components)

    if all_created:
        print("✅ All components initialized successfully.")
        return True
    else:
        failed_components = [
            type(component).__name__ for component in components if component is None
        ]
        print(f"❌ Failed to initialize components: {', '.join(failed_components)}")
        return False


def main():
    """Main function."""
    print("===== Testing deepwiki-to-md Refactored Code =====")

    success = asyncio.run(test_structures())

    if success:
        print(
            "\n✅ Integration test passed! The refactored code structure is working correctly."
        )
        return 0
    else:
        print(
            "\n❌ Integration test failed! Check the structure of the refactored code."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
