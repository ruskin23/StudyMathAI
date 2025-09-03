from __future__ import annotations

from sqlalchemy.orm import Session

from studymathai.data_models import HeadingContent
from studymathai.database.models import Book, BookChapter, ChapterSegment


class SegmentsRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_all(self) -> list[ChapterSegment]:
        return self.session.query(ChapterSegment).all()

    def list_for_book(self, book_id: int) -> list[ChapterSegment]:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        return book.segment_entries

    def list_for_chapter(self, book_id: int, chapter_id: int) -> list[ChapterSegment]:
        chapter = self.session.query(BookChapter).filter_by(id=chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter with ID {chapter_id} not found")
        if chapter.book_id != book_id:
            raise ValueError(f"Chapter {chapter_id} does not belong to book {book_id}")
        return chapter.segments

    def create_many(self, book_id: int, chapter_id: int, entries: list[HeadingContent]) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")

        chapter = self.session.query(BookChapter).filter_by(id=chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter with ID {chapter_id} not found")
        if chapter.book_id != book_id:
            raise ValueError(f"Chapter {chapter_id} does not belong to book {book_id}")

        # Idempotent insert: prefetch existing titles for chapter
        existing_titles = {
            s.heading_title
            for s in self.session.query(ChapterSegment).filter_by(chapter_id=chapter_id).all()
        }

        created = 0
        for entry in entries:
            if entry.heading.title in existing_titles:
                continue
            segment = ChapterSegment(
                heading_level=entry.heading.level,
                heading_title=entry.heading.title,
                heading_text=entry.text,
                book=book,
                chapter=chapter,
            )
            self.session.add(segment)
            created += 1
        return created

    def delete_for_book(self, book_id: int) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        count = len(book.segment_entries)
        book.segment_entries.clear()
        return count

    def delete_for_chapter(self, book_id: int, chapter_id: int) -> int:
        chapter = self.session.query(BookChapter).filter_by(id=chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter with ID {chapter_id} not found")
        if chapter.book_id != book_id:
            raise ValueError(f"Chapter {chapter_id} does not belong to book {book_id}")
        count = len(chapter.segments)
        chapter.segments.clear()
        return count
