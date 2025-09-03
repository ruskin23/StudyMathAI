from __future__ import annotations

from sqlalchemy.orm import Session

from studymathai.data_models import SlideDeck
from studymathai.database.models import Book, ChapterSegment, SegmentSlides


class SlidesRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_book(self, book_id: int) -> list[SegmentSlides]:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        all_slides: list[SegmentSlides] = []
        for segment in book.segment_entries:
            all_slides.extend(segment.slides)
        return all_slides

    def list_for_segment(self, book_id: int, segment_id: int) -> list[SegmentSlides]:
        segment = self.session.query(ChapterSegment).filter_by(id=segment_id).first()
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
        if segment.book_id != book_id:
            raise ValueError(f"Segment {segment_id} does not belong to book {book_id}")
        return segment.slides

    def list_for_segment_id(self, segment_id: int) -> list[SegmentSlides]:
        segment = self.session.query(ChapterSegment).filter_by(id=segment_id).first()
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
        return segment.slides

    def create_many(self, book_id: int, segment_id: int, slide_deck: SlideDeck) -> int:
        segment = self.session.query(ChapterSegment).filter_by(id=segment_id).first()
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
        if segment.book_id != book_id:
            raise ValueError(f"Segment {segment_id} does not belong to book {book_id}")

        # Idempotent insert: prefetch existing titles for segment
        existing_titles = {
            s.title
            for s in self.session.query(SegmentSlides).filter_by(segment_id=segment_id).all()
        }

        created = 0
        for entry in slide_deck.slides:
            if entry.title in existing_titles:
                continue
            slide = SegmentSlides(
                title=entry.title,
                bullets=entry.bullets,
                segment=segment,
                book_id=book_id,
            )
            self.session.add(slide)
            created += 1
        return created

    def delete_for_book(self, book_id: int) -> int:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        total = 0
        for segment in book.segment_entries:
            total += len(segment.slides)
            segment.slides.clear()
        return total

    def delete_for_segment(self, book_id: int, segment_id: int) -> int:
        segment = self.session.query(ChapterSegment).filter_by(id=segment_id).first()
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
        if segment.book_id != book_id:
            raise ValueError(f"Segment {segment_id} does not belong to book {book_id}")
        count = len(segment.slides)
        segment.slides.clear()
        return count
