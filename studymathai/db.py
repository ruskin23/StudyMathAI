# Updated studymathai/db.py with session safety

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from .models import Base, Book, BookContent, ChapterContent, GeneratedSlide, TableOfContents, PageText
import json
from typing import List, Optional

class DatabaseManager:
    def __init__(self):
        db_name = os.getenv("SQLITE_DB_NAME", "studymathai.db")
        self.engine = create_engine(
            f"sqlite:///{db_name}",
            connect_args={"check_same_thread": False},
            pool_size=10,
            max_overflow=20,
            pool_timeout=30
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_book(self, book_hash: str, file_path: str, title: str) -> Book:
        with self.Session() as session:
            book = Book(book_hash=book_hash, file_path=file_path, title=title)
            session.add(book)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                book = session.query(Book).filter_by(book_hash=book_hash).first()
            return book

    def get_book_by_hash(self, book_hash: str) -> Optional[Book]:
        with self.Session() as session:
            return session.query(Book).filter_by(book_hash=book_hash).first()

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        with self.Session() as session:
            return session.query(Book).filter_by(id=book_id).first()

    def get_books(self) -> List[Book]:
        with self.Session() as session:
            return session.query(Book).all()

    def add_page_text(self, book_id: int, page_number: int, page_text: str) -> PageText:
        with self.Session() as session:
            page = PageText(
                book_id=book_id,
                page_number=page_number,
                page_text=page_text
            )
            session.add(page)
            try:
                session.commit()
                return page
            except IntegrityError:
                session.rollback()
                return session.query(PageText).filter_by(book_id=book_id, page_number=page_number).first()

    def get_pages_by_book(self, book_id: int) -> list:
        with self.Session() as session:
            return session.query(PageText).filter_by(book_id=book_id).all()

    def add_chapter(self, book_id: int, title: str, text: str, start: int, end: int) -> Optional[BookContent]:
        with self.Session() as session:
            chapter = BookContent(
                book_id=book_id,
                chapter_title=title,
                chapter_text=text,
                start_page=start,
                end_page=end
            )
            session.add(chapter)
            try:
                session.commit()
                session.refresh(chapter)
                return chapter
            except IntegrityError:
                session.rollback()
                return session.query(BookContent).filter_by(book_id=book_id, chapter_title=title).first()

    def get_chapters_by_book(self, book_id: int) -> List[BookContent]:
        with self.Session() as session:
            return session.query(BookContent).filter_by(book_id=book_id).all()

    def add_chapter_segment(self, chapter_id: int, book_id: int, level: int, title: str, text: str, parent_id: Optional[int] = None) -> Optional[ChapterContent]:
        with self.Session() as session:
            segment = ChapterContent(
                chapter_id=chapter_id,
                book_id=book_id,
                heading_level=level,
                heading_title=title,
                content_text=text,
                parent_id=parent_id
            )
            session.add(segment)
            try:
                session.commit()
                return segment
            except IntegrityError:
                session.rollback()
                return session.query(ChapterContent).filter_by(chapter_id=chapter_id, heading_title=title).first()

    def get_segments_by_chapter(self, chapter_id: int) -> List[ChapterContent]:
        with self.Session() as session:
            return session.query(ChapterContent).filter_by(chapter_id=chapter_id).all()

    def get_segments_by_book(self, book_id: int):
        with self.Session() as session:
            return session.query(ChapterContent).filter_by(book_id=book_id).all()

    def add_generated_slide(self, content_id: int, book_id: int, slide_data: dict, model_info: str = "") -> Optional[GeneratedSlide]:
        with self.Session() as session:
            slide = GeneratedSlide(
                content_id=content_id,
                book_id=book_id,
                slides_json=json.dumps(slide_data),
                model_info=model_info
            )
            session.add(slide)
            try:
                session.commit()
                return slide
            except IntegrityError:
                session.rollback()
                return session.query(GeneratedSlide).filter_by(content_id=content_id).first()

    def get_slides_for_segment(self, content_id: int) -> Optional[GeneratedSlide]:
        with self.Session() as session:
            return session.query(GeneratedSlide).filter_by(content_id=content_id).first()

    def add_toc_entry(self, book_id: int, level: int, title: str, page_number: int, chapter_id: Optional[int] = None, parent_id: Optional[int] = None):
        with self.Session() as session:
            toc_entry = TableOfContents(
                book_id=book_id,
                chapter_id=chapter_id,
                level=level,
                title=title,
                page_number=page_number,
                parent_id=parent_id
            )
            session.add(toc_entry)
            try:
                session.commit()
                return toc_entry
            except IntegrityError:
                session.rollback()
                return session.query(TableOfContents).filter_by(
                    book_id=book_id,
                    level=level,
                    title=title,
                    page_number=page_number
                ).first()
                
    def get_toc_for_book(self, book_id: int):
        with self.Session() as session:
            return session.query(TableOfContents).filter_by(book_id=book_id).all()

    def get_toc_for_chapter(self, chapter_id: int) -> List[TableOfContents]:
        with self.Session() as session:
            return session.query(TableOfContents).filter(
                TableOfContents.chapter_id == chapter_id,
                TableOfContents.level > 1
            ).all()
