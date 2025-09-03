from __future__ import annotations

from sqlalchemy.orm import Session

from studymathai.data_models import Chapter
from studymathai.database.models import Book, BookChapter


class ChaptersRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_book(self, book_id: int) -> list[BookChapter]:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        return book.chapter_entries

    def create_many(self, book_id: int, entries: list[Chapter]) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")

        # Idempotent insert: prefetch existing titles
        existing = {
            ch.chapter_title
            for ch in self.session.query(BookChapter).filter_by(book_id=book_id).all()
        }

        created = 0
        for entry in entries:
            if entry.title in existing:
                continue
            chapter = BookChapter(
                chapter_title=entry.title,
                start_page=entry.start_page,
                end_page=entry.end_page,
                book=book,
            )
            self.session.add(chapter)
            created += 1
        return created

    def delete_for_book(self, book_id: int) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        count = len(book.chapter_entries)
        book.chapter_entries.clear()
        return count
