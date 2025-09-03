from .core import DatabaseConnection
from .models import (
    Base,
    Book,
    BookChapter,
    ChapterSegment,
    PageText,
    ProcessingStatus,
    SegmentSlides,
    TableOfContents,
)
from .transform import (
    convert_chapter_entry,
    convert_text,
    convert_toc_entry,
)

__all__ = [
    "DatabaseConnection",
    "Base",
    "Book",
    "BookChapter",
    "ChapterSegment",
    "SegmentSlides",
    "TableOfContents",
    "PageText",
    "ProcessingStatus",
    # Transform helpers
    "convert_text",
    "convert_chapter_entry",
    "convert_toc_entry",
]
