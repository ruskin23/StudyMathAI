from __future__ import annotations

from sqlalchemy.orm import Session

from studymathai.data_models import TOCEntry
from studymathai.database.models import Book, BookChapter, TableOfContents


class TOCRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_book(self, book_id: int) -> list[TableOfContents]:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        return book.toc_entries

    def _find_chapter_for_page(self, chapters: list[BookChapter], page: int) -> BookChapter | None:
        for ch in chapters:
            if (
                ch.start_page is not None
                and ch.end_page is not None
                and ch.start_page <= page <= ch.end_page
            ):
                return ch
        return None

    def create_many_with_chapter_link(self, book_id: int, entries: list[TOCEntry]) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")

        # Preload chapters for range lookup once
        chapters = (
            self.session.query(BookChapter)
            .filter_by(book_id=book_id)
            .order_by(BookChapter.start_page)
            .all()
        )

        # Idempotent insert: prefetch existing keys
        existing_keys = {
            (e.level, e.title, e.page_number)
            for e in self.session.query(TableOfContents).filter_by(book_id=book_id).all()
        }

        created = 0
        for entry in entries:
            chapter = self._find_chapter_for_page(chapters, entry.page)
            if not chapter:
                raise ValueError(
                    f"No chapter found covering page {entry.page} for book {book_id}. "
                    "Ensure chapters are saved before TOC entries."
                )

            if (entry.level, entry.title, entry.page) in existing_keys:
                continue
            toc = TableOfContents(
                level=entry.level,
                title=entry.title,
                page_number=entry.page,
                book=book,
                chapter=chapter,
            )
            self.session.add(toc)
            created += 1
        return created

    def delete_for_book(self, book_id: int) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        count = len(book.toc_entries)
        book.toc_entries.clear()
        return count
