from __future__ import annotations

from sqlalchemy.orm import Session

from studymathai.data_models import Text
from studymathai.database.models import Book, BookChapter, PageText


class PagesRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_book(self, book_id: int) -> list[PageText]:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        return book.pages

    def _find_chapter_for_page(self, chapters: list[BookChapter], page: int) -> BookChapter | None:
        for ch in chapters:
            if (
                ch.start_page is not None
                and ch.end_page is not None
                and ch.start_page <= page <= ch.end_page
            ):
                return ch
        return None

    def create_many_auto_link(self, book_id: int, entries: list[Text]) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")

        chapters = (
            self.session.query(BookChapter)
            .filter_by(book_id=book_id)
            .order_by(BookChapter.start_page)
            .all()
        )

        # Idempotent insert: prefetch existing page_numbers
        existing_pages = {
            p.page_number for p in self.session.query(PageText).filter_by(book_id=book_id).all()
        }

        created = 0
        for entry in entries:
            if entry.page_number in existing_pages:
                continue
            chapter = self._find_chapter_for_page(chapters, entry.page_number)
            text = PageText(
                page_number=entry.page_number,
                page_text=entry.page_text,
                book=book,
                chapter=chapter,
            )
            self.session.add(text)
            created += 1
        return created

    def delete_for_book(self, book_id: int) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        count = len(book.pages)
        book.pages.clear()
        return count
