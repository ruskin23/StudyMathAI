"""
Processing modules for StudyMathAI.

This package contains modules for processing PDF documents:
- extraction: Extract text, TOC, and chapters from PDFs
- segmentation: Segment chapters into meaningful sections
- generation: Generate slides from text content
"""

from .extraction import (
    clean_title,
    extract_chapters,
    extract_headings,
    extract_page_texts,
    extract_toc,
)
from .generation import generate_slides
from .segmentation import build_heading_map, build_line_map, segment_chapter

__all__ = [
    "extract_page_texts",
    "extract_toc",
    "extract_chapters",
    "extract_headings",
    "clean_title",
    "segment_chapter",
    "build_line_map",
    "build_heading_map",
    "generate_slides",
]
