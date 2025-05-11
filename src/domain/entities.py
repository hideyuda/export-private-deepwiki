#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Domain entities for the deepwiki-to-md application.
These represent the core business objects in the system.
"""

import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from bs4 import Tag

from src.domain.constants import (
    VISIBLE_TEXT_COLOR,
    GENERIC_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    FOREIGN_OBJECT_TEXT_STYLE,
)


@dataclass
class MermaidDiagram:
    """
    Represents a Mermaid SVG diagram to be processed and saved.
    """

    original_id: str
    svg_content: Tag  # BeautifulSoup Tag object for the SVG (should be a copy)
    chat_block_index: int
    diagram_index: int

    def _sanitize_filename(self, filename: str) -> str:
        sanitized = re.sub(r"[^\w\.-]", "_", filename)
        return sanitized[:100]

    def prepare_and_save(self, md_file_output_dir: str) -> Optional[str]:
        """
        Prepares the SVG content and saves it to a file
        within an 'images' subdirectory of the md_file_output_dir.
        Returns the relative path to the saved SVG file for Markdown, or None on error.
        """
        svg_tag = self.svg_content

        # 0. Normalize 'foreignobject' to 'foreignObject' (SVG standard)
        for fo_lower in svg_tag.find_all("foreignobject", recursive=True):
            fo_lower.name = "foreignObject"

        # 1. Clear potentially problematic root <svg> attributes
        for attr in ["width", "height", "style"]:
            if svg_tag.has_attr(attr):
                del svg_tag[attr]

        # 2. Handle viewBox and set root <svg> width for responsiveness
        viewbox_str = svg_tag.get("viewBox")
        if not viewbox_str:
            viewbox_str = svg_tag.get("viewbox")  # Check for lowercase 'viewbox'
            if viewbox_str:
                svg_tag["viewBox"] = viewbox_str
                if svg_tag.has_attr("viewbox"):
                    del svg_tag["viewbox"]

        if viewbox_str:
            parts = viewbox_str.split()
            if len(parts) == 4:
                svg_tag["width"] = "100%"  # Make SVG responsive to container width
                # Height is implicitly handled by viewBox and preserveAspectRatio
            else:
                print(
                    f"Warning: Malformed viewBox '{viewbox_str}' for SVG {self.original_id}. Using width='100%' as fallback."
                )
                svg_tag["width"] = "100%"
        else:
            print(
                f"CRITICAL WARNING: SVG {self.original_id} lacks a viewBox attribute. Setting width='100%' but scaling may be unpredictable."
            )
            svg_tag["width"] = "100%"

        svg_tag["preserveAspectRatio"] = "xMidYMid meet"

        # 3. Forcefully style text elements for visibility
        # Apply to native SVG <text> and <tspan> elements
        for text_element in svg_tag.find_all(["text", "tspan"], recursive=True):
            text_element["fill"] = VISIBLE_TEXT_COLOR
            text_element["font-family"] = GENERIC_FONT_FAMILY
            text_element["font-size"] = DEFAULT_FONT_SIZE
            if text_element.has_attr("style"):  # Remove conflicting inline styles
                del text_element["style"]

        # Apply to HTML content within <foreignObject>
        for foreign_object in svg_tag.find_all("foreignObject", recursive=True):
            # Ensure foreignObject itself can be rendered (has dimensions)
            if (
                not foreign_object.has_attr("width")
                or foreign_object.get("width", "0").replace("px", "").strip() == "0"
            ):
                foreign_object["width"] = "100%"
            if (
                not foreign_object.has_attr("height")
                or foreign_object.get("height", "0").replace("px", "").strip() == "0"
            ):
                foreign_object["height"] = "1000"

            for element in foreign_object.find_all(
                ["div", "span", "p", "font", "b", "i", "strong", "em", "label"],
                recursive=True,
            ):
                element["style"] = FOREIGN_OBJECT_TEXT_STYLE

        # --- File Saving Logic ---
        images_subdir_name = "images"
        images_dir_path = os.path.join(md_file_output_dir, images_subdir_name)
        os.makedirs(images_dir_path, exist_ok=True)

        # filename_base_id = (
        #     self.original_id
        #     if self.original_id
        #     else f"mermaid_diagram_{self.chat_block_index}_{self.diagram_index}"
        # )
        filename_base_id = (
            f"mermaid_diagram_{self.chat_block_index}_{self.diagram_index}"
        )
        base_filename = self._sanitize_filename(filename_base_id)
        svg_filename = f"{base_filename}.svg"
        svg_filepath = os.path.join(images_dir_path, svg_filename)

        try:
            if not isinstance(svg_tag, Tag):
                print(
                    f"Error: svg_tag for {self.original_id} is not a valid Tag object. Type: {type(svg_tag)}"
                )
                return None
            svg_string_to_write = svg_tag.prettify()
            with open(svg_filepath, "w", encoding="utf-8") as f_svg:
                f_svg.write(svg_string_to_write)

            relative_svg_path = os.path.join(images_subdir_name, svg_filename)
            return relative_svg_path.replace("\\", "/")
        except AttributeError as ae:
            print(
                f"AttributeError during prettify for SVG {self.original_id}. SVG content: {str(svg_tag)[:200]}. Error: {ae}"
            )
            return None
        except IOError as e:
            print(f"Error saving SVG file {svg_filepath}: {e}")
            return None


@dataclass
class CodeReference:
    """
    Represents a reference to a code file.
    """

    repo_name: Optional[str]
    file_name: str
    github_url: str

    def to_markdown(self) -> str:
        display_name = (
            f"{self.repo_name}/{self.file_name}" if self.repo_name else self.file_name
        )
        return f"- [{display_name}]({self.github_url})"


@dataclass
class CodeReferenceCollection:
    """
    A first-class collection for CodeReference objects.
    """

    references: List[CodeReference] = field(default_factory=list)

    def add(self, reference: CodeReference):
        self.references.append(reference)

    def to_markdown(self) -> str:
        if not self.references:
            return ""
        md_list = [ref.to_markdown() for ref in self.references]
        return "\n## Code References\n" + "\n".join(md_list) + "\n"


@dataclass
class ProcessedAnswer:
    """
    Represents the answer content after processing Mermaid diagrams.
    """

    html_content_with_placeholders: (
        str  # HTML string where SVGs are replaced by placeholders
    )
    placeholder_to_markdown_link_map: Dict[
        str, str
    ]  # Maps placeholders to final Markdown image links

    def to_markdown(self, markdown_converter) -> str:
        """
        Converts the processed HTML to Markdown and inserts diagram links.
        """
        markdown_text = markdown_converter.convert_html_to_markdown(
            self.html_content_with_placeholders
        )
        for placeholder, md_link in self.placeholder_to_markdown_link_map.items():
            if placeholder in markdown_text:
                markdown_text = markdown_text.replace(placeholder, md_link)
            else:
                print(
                    f"Warning: Placeholder '{placeholder}' not found in markdownified answer for replacement."
                )
        return markdown_text


@dataclass
class ChatBlockContent:
    """
    Represents the extracted content of a single chat block.
    """

    query: Optional[str]
    processed_answer: Optional[ProcessedAnswer]
    code_references: CodeReferenceCollection

    def to_markdown(self, markdown_converter) -> str:
        parts = []
        if self.query:
            parts.append(f"# Query\n\n> {self.query}\n")
        if self.processed_answer:
            # Remove the hardcoded "### Answer" heading.
            # The heading will come from the HTML content (e.g., <h1>Answer</h1>)
            # and be converted by markdownify.
            parts.append(f"\n{self.processed_answer.to_markdown(markdown_converter)}\n")

        code_refs_md = self.code_references.to_markdown()
        if code_refs_md:
            parts.append(code_refs_md)
        return "\n".join(filter(None, parts))


@dataclass
class ChatLog:
    """
    Represents a collection of chat blocks from a page.
    """

    chat_blocks: List[ChatBlockContent] = field(default_factory=list)

    def add_chat_block(self, chat_block: ChatBlockContent):
        self.chat_blocks.append(chat_block)

    def to_markdown(self, markdown_converter) -> str:
        if not self.chat_blocks:
            return ""

        markdown_docs = [
            block.to_markdown(markdown_converter) for block in self.chat_blocks if block
        ]
        return "\n\n---\n\n".join(filter(None, markdown_docs))
