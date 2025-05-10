#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML repository for parsing HTML content and creating domain entities.
"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from src.domain.entities import (
    ChatBlockContent,
    CodeReference,
    CodeReferenceCollection,
    ProcessedAnswer,
    MermaidDiagram,
)
from src.gateway.html_adapter import HtmlAdapter


class HtmlRepository:
    """
    Repository for HTML operations, using HtmlAdapter.
    """

    def __init__(self, html_adapter: HtmlAdapter):
        """
        Initialize the HtmlRepository with an HtmlAdapter.

        Args:
            html_adapter: The HtmlAdapter to use for HTML operations.
        """
        self.html_adapter = html_adapter

    def extract_chat_blocks(
        self,
        html_content: str,
        output_dir: str,
        chat_block_indices: Optional[List[int]] = None,
    ) -> List[ChatBlockContent]:
        """
        Extracts chat blocks from HTML content and creates ChatBlockContent entities.

        Args:
            html_content: The HTML content to parse.
            output_dir: Directory where output files (e.g., SVGs) will be saved.
            chat_block_indices: Indices of chat blocks to parse. If None, all blocks are parsed.

        Returns:
            A list of ChatBlockContent objects.
        """
        # Extract chat block snippets
        snippets = self.html_adapter.extract_chat_block_snippets(html_content)

        # If specific indices were requested, filter the snippets
        if chat_block_indices is not None:
            filtered_snippets = [
                (i, s) for i, s in enumerate(snippets) if i in chat_block_indices
            ]
        else:
            filtered_snippets = enumerate(snippets)

        # Parse each snippet into a ChatBlockContent object
        chat_blocks = []
        for i, snippet in filtered_snippets:
            chat_block = self.parse_chat_block(snippet, output_dir, i)
            if chat_block:
                chat_blocks.append(chat_block)

        return chat_blocks

    def parse_chat_block(
        self, html_snippet: str, output_dir: str, chat_block_index: int
    ) -> ChatBlockContent:
        """
        Parses a single chat block HTML into a ChatBlockContent entity.

        Args:
            html_snippet: The HTML snippet for a chat block.
            output_dir: Directory where output files will be saved.
            chat_block_index: The index of this chat block.

        Returns:
            A ChatBlockContent object.
        """
        # Parse HTML snippet
        block_soup = self.html_adapter.parse_html(html_snippet)

        # Extract query
        query = self.html_adapter.extract_query_from_block(block_soup)

        # Extract answer area
        answer_area = self.html_adapter.extract_answer_area(block_soup)

        # Extract code references
        code_references = self._create_code_references(block_soup)

        # Process answer if available
        processed_answer = None
        if answer_area:
            processed_answer = self._process_answer_area(
                answer_area, output_dir, chat_block_index
            )

        # Create and return ChatBlockContent
        return ChatBlockContent(
            query=query,
            processed_answer=processed_answer,
            code_references=code_references,
        )

    def _create_code_references(
        self, block_soup: BeautifulSoup
    ) -> CodeReferenceCollection:
        """
        Creates CodeReference entities from a chat block.

        Args:
            block_soup: The BeautifulSoup object for a chat block.

        Returns:
            A CodeReferenceCollection object.
        """
        collection = CodeReferenceCollection()
        ref_data_list = self.html_adapter.extract_code_references(block_soup)

        for ref_data in ref_data_list:
            code_ref = CodeReference(
                repo_name=ref_data["repo_name"],
                file_name=ref_data["file_name"],
                github_url=ref_data["github_url"],
            )
            collection.add(code_ref)

        return collection

    def _process_answer_area(
        self, answer_area: BeautifulSoup, output_dir: str, chat_block_index: int
    ) -> ProcessedAnswer:
        """
        Processes the answer area, extracting and saving Mermaid diagrams.

        Args:
            answer_area: The BeautifulSoup object for the answer area.
            output_dir: Directory where diagram files will be saved.
            chat_block_index: The index of the chat block.

        Returns:
            A ProcessedAnswer object.
        """
        # Copy the answer area to avoid modifying the original
        answer_area_copy = BeautifulSoup(str(answer_area), "html.parser")

        # Extract Mermaid diagrams
        diagrams = self.html_adapter.extract_mermaid_diagrams(answer_area_copy)

        # Process each diagram
        placeholder_map = {}
        for diagram_data in diagrams:
            svg_tag = diagram_data["svg_tag"]
            pre_tag = diagram_data["pre_tag"]
            diagram_index = diagram_data["index"]

            # Create MermaidDiagram entity
            diagram = MermaidDiagram(
                original_id=svg_tag.get("id", ""),
                svg_content=svg_tag,
                chat_block_index=chat_block_index,
                diagram_index=diagram_index,
            )

            # Save the diagram and get the file path
            relative_svg_path = diagram.prepare_and_save(output_dir)

            # Create a placeholder for this diagram
            placeholder = self.html_adapter.create_placeholder(
                chat_block_index, diagram_index
            )

            # Add the placeholder and corresponding markdown link to the map
            if relative_svg_path:
                placeholder_map[placeholder] = (
                    f"![Mermaid Diagram]({relative_svg_path})"
                )
            else:
                placeholder_map[placeholder] = ""

            # Replace the SVG with a placeholder in the HTML
            self.html_adapter.replace_svg_with_placeholder(pre_tag, placeholder)

        # Clean up the HTML
        self.html_adapter.unwrap_nested_pre_tags(answer_area_copy)
        self.html_adapter.remove_empty_pre_tags(answer_area_copy)

        # Create and return ProcessedAnswer
        return ProcessedAnswer(
            html_content_with_placeholders=str(answer_area_copy),
            placeholder_to_markdown_link_map=placeholder_map,
        )
