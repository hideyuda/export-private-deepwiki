#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown repository for converting entities to markdown using the MarkdownAdapter.
"""

from src.domain.entities import ProcessedAnswer, ChatLog
from src.gateway.markdown_adapter import MarkdownAdapter


class MarkdownRepository:
    """
    Repository for markdown operations, using MarkdownAdapter.
    """

    def __init__(self, markdown_adapter: MarkdownAdapter):
        """
        Initialize the MarkdownRepository with a MarkdownAdapter.

        Args:
            markdown_adapter: The MarkdownAdapter to use for markdown conversions.
        """
        self.markdown_adapter = markdown_adapter

    def convert_processed_answer_to_markdown(
        self, processed_answer: ProcessedAnswer
    ) -> str:
        """
        Converts a ProcessedAnswer entity to markdown.

        Args:
            processed_answer: The ProcessedAnswer entity to convert.

        Returns:
            The markdown representation of the processed answer.
        """
        return processed_answer.to_markdown(self.markdown_adapter)

    def convert_chat_log_to_markdown(self, chat_log: ChatLog) -> str:
        """
        Converts a ChatLog entity to markdown.

        Args:
            chat_log: The ChatLog entity to convert.

        Returns:
            The markdown representation of the chat log.
        """
        return chat_log.to_markdown(self.markdown_adapter)
