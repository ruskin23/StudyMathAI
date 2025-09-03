from __future__ import annotations

import fitz
from sqlalchemy.orm import Session

from studymathai.database.models import ProcessingStatus
from studymathai.processing import (
    extract_chapters,
    extract_headings,
    extract_page_texts,
    extract_toc,
    segment_chapter,
)
from studymathai.repositories import (
    BooksRepository,
    ChaptersRepository,
    PagesRepository,
    SegmentsRepository,
    TOCRepository,
)


def _ensure_status(session: Session, book_id: int) -> ProcessingStatus:
    status = session.query(ProcessingStatus).filter_by(book_id=book_id).first()
    if not status:
        status = ProcessingStatus(book_id=book_id)
        session.add(status)
        session.flush()
    return status


def extract_and_save_metadata(session: Session, book_id: int) -> tuple[int, int]:
    """Extract TOC and chapters and save idempotently. Returns (#chapters, #toc)."""
    book = BooksRepository(session).get(book_id)
    doc = fitz.open(book.file_path)

    toc_entries = extract_toc(doc)
    chapter_entries = extract_chapters(toc_entries, doc)

    ch_created = ChaptersRepository(session).create_many(book.id, chapter_entries)
    toc_created = TOCRepository(session).create_many_with_chapter_link(book.id, toc_entries)

    status = _ensure_status(session, book.id)
    status.content_extracted = True
    session.flush()

    return ch_created, toc_created


def extract_and_save_pages(session: Session, book_id: int) -> int:
    """Extract page texts and save idempotently. Returns #pages created."""
    book = BooksRepository(session).get(book_id)
    doc = fitz.open(book.file_path)
    texts = extract_page_texts(doc)

    created = PagesRepository(session).create_many_auto_link(book.id, texts)

    status = _ensure_status(session, book.id)
    status.pages_extracted = True
    session.flush()

    return created


def segment_and_save(session: Session, book_id: int) -> int:
    """Segment book by headings and save segments idempotently. Returns #segments created."""
    book = BooksRepository(session).get(book_id)
    pages = PagesRepository(session).list_for_book(book.id)
    tocs = TOCRepository(session).list_for_book(book.id)
    chapters = ChaptersRepository(session).list_for_book(book.id)

    headings = extract_headings(tocs)
    segments = segment_chapter(headings, pages)

    # bucket by chapter using page ranges
    def chapter_for_page(page: int):
        for ch in chapters:
            if (
                ch.start_page is not None
                and ch.end_page is not None
                and ch.start_page <= page <= ch.end_page
            ):
                return ch
        return None

    bucket = {}
    for seg in segments:
        ch = chapter_for_page(seg.heading.page_number)
        if not ch:
            continue
        bucket.setdefault(ch.id, []).append(seg)

    created_total = 0
    seg_repo = SegmentsRepository(session)
    for ch_id, segs in bucket.items():
        created_total += seg_repo.create_many(book.id, ch_id, segs)

    status = _ensure_status(session, book.id)
    status.chapters_segmented = True
    session.flush()

    return created_total
