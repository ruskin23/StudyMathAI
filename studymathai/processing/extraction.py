import re

import fitz  # PyMuPDF

from studymathai.data_models import Chapter, Heading, Text, TOCEntry
from studymathai.logging_config import get_logger

logger = get_logger(__name__)


def clean_title(text: str) -> str:
    """Cleans the text by removing unwanted characters.
    This method removes:
    - Unicode surrogate pairs (e.g., emojis)
    - Control characters (e.g., newlines, tabs)
    """
    return re.sub(r"[\uD800-\uDFFF\u0000-\u001F]+", "", text).strip()


def extract_toc(doc: fitz.Document) -> list[TOCEntry]:
    """Returns the Table of Contents as a list of TOCEntry models."""
    raw_toc = doc.get_toc(simple=True)
    cleaned_toc = [
        TOCEntry(level=level, title=clean_title(title), page=page) for level, title, page in raw_toc
    ]
    logger.debug(f"TOC entries: {cleaned_toc}")
    return cleaned_toc


def extract_headings(toc: list[TOCEntry]) -> list[Heading]:
    """
    Extracts headings from the Table of Contents.
    Returns a list of Heading objects.
    """
    headings = []
    for entry in toc:
        headings.append(Heading(title=entry.title, level=entry.level, page_number=entry.page))
    logger.debug(f"Extracted {len(headings)} headings from TOC.")
    return headings


def extract_page_texts(doc: fitz.Document) -> list[Text]:
    """
    Extracts text from all pages of a PDF document.
    Returns a list of Text objects containing page numbers and text content.
    """
    texts: list[Text] = []
    for page_num in range(doc.page_count):
        page: fitz.Page = doc.load_page(page_num)
        if not page:
            logger.warning(f"Page {page_num} could not be loaded.")
            text = ""
        else:
            text = page.get_text()
            if not text.strip():
                logger.warning(f"Page {page_num} has no extractable text.")

        texts.append(Text(page_number=page_num, page_text=text))
    logger.info(f"Extracted {len(texts)} pages of text from the PDF.")
    return texts


def filter_relevant_chapters(toc: list[TOCEntry]) -> list[tuple[str, int]]:
    """
    Filters the Table of Contents to keep only relevant chapters.
    Returns a list of tuples containing (title, page).
    This method ensures that:
    - Level-1 entries are kept only if they are followed by a level-2 entry
    - Trailing level-1 entries not followed by a level-2 entry are removed.
    """
    valid = []

    # First pass: keep level-1 only if followed by level-2
    for i, entry in enumerate(toc):
        if entry.level == 1 and (i + 1 < len(toc) and toc[i + 1].level == 2):
            valid.append((entry.title, entry.page))

    for title, page in valid:
        logger.debug(f"Valid chapter: {title} (Page {page})")

    # Second pass: remove trailing L1s not followed by L2
    while valid:
        last_title, last_page = valid[-1]
        idx = next(
            (
                i
                for i, e in reversed(list(enumerate(toc)))
                if e.title == last_title and e.page == last_page
            ),
            None,
        )
        if idx is None or idx + 1 >= len(toc) or toc[idx + 1].level != 2:
            valid.pop()
        else:
            break

    return valid


def extract_chapters(toc_entries: list[TOCEntry], doc: fitz.Document) -> list[Chapter]:
    """
    Extracts chapter page ranges from the Table of Contents.
    Returns a list of ChapterRange objects.
    """
    filtered = filter_relevant_chapters(toc_entries)
    logger.debug(f"Filtered TOC entries: {filtered}")
    chapters = []
    for i, (title, start_page) in enumerate(filtered):
        start = start_page - 1
        end = filtered[i + 1][1] - 1 if i + 1 < len(filtered) else doc.page_count - 1
        chapters.append(Chapter(title=title, start_page=start, end_page=end))
    logger.debug(f"Chapter page ranges: {chapters}")
    return chapters
