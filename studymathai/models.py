from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    book_hash = Column(String, unique=True, nullable=False)
    file_path = Column(Text)
    title = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contents = relationship("BookContent", back_populates="book")
    chapters = relationship("ChapterContent", back_populates="book")
    toc_entries = relationship("TableOfContents", back_populates="book")
    pages = relationship("PageText", back_populates="book")


class BookContent(Base):
    __tablename__ = 'book_content'
    __table_args__ = (
        UniqueConstraint('book_id', 'chapter_title', name='uq_book_chapter'),
    )

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    chapter_title = Column(Text, nullable=False)
    chapter_text = Column(Text)
    start_page = Column(Integer)
    end_page = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    book = relationship("Book", back_populates="contents")
    chapter_segments = relationship("ChapterContent", back_populates="chapter")
    toc_entries = relationship("TableOfContents", back_populates="chapter")


class TableOfContents(Base):
    __tablename__ = 'table_of_contents'
    __table_args__ = (
        UniqueConstraint('book_id', 'level', 'title', 'page_number', name='uq_toc_entry'),
    )

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    chapter_id = Column(Integer, ForeignKey('book_content.id'), nullable=True)
    level = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey('table_of_contents.id'), nullable=True)

    book = relationship("Book", back_populates="toc_entries")
    chapter = relationship("BookContent", back_populates="toc_entries")
    parent = relationship("TableOfContents", remote_side=[id], backref="children")


class ChapterContent(Base):
    __tablename__ = 'chapter_content'
    __table_args__ = (
        UniqueConstraint('chapter_id', 'heading_title', name='uq_chapter_heading'),
    )

    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey('book_content.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    heading_level = Column(Integer, nullable=False)
    heading_title = Column(Text, nullable=False)
    content_text = Column(Text)
    parent_id = Column(Integer, ForeignKey('chapter_content.id'))

    chapter = relationship("BookContent", back_populates="chapter_segments")
    book = relationship("Book", back_populates="chapters")
    parent = relationship("ChapterContent", remote_side=[id], backref="subsections")
    slides = relationship("GeneratedSlide", back_populates="content")


class GeneratedSlide(Base):
    __tablename__ = 'generated_slides'
    __table_args__ = (
        UniqueConstraint('content_id', name='uq_unique_slide_per_segment'),
    )

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('chapter_content.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)  # ← NEW
    slides_json = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    model_info = Column(Text)

    content = relationship("ChapterContent", back_populates="slides")


class PageText(Base):
    __tablename__ = 'page_text'
    __table_args__ = (
        UniqueConstraint('book_id', 'page_number', name='uq_book_page'),
    )

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    page_number = Column(Integer, nullable=False)
    page_text = Column(Text, nullable=False)

    book = relationship("Book", back_populates="pages")
