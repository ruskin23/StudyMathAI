from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)

    book_hash = Column(String, unique=True, nullable=False)
    file_path = Column(Text)
    title = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    chapter_entries = relationship(
        "BookChapter", back_populates="book", cascade="all, delete-orphan"
    )
    segment_entries = relationship(
        "ChapterSegment", back_populates="book", cascade="all, delete-orphan"
    )
    toc_entries = relationship(
        "TableOfContents", back_populates="book", cascade="all, delete-orphan"
    )
    pages = relationship("PageText", back_populates="book", cascade="all, delete-orphan")
    processing_status = relationship(
        "ProcessingStatus",
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan",
    )


class BookChapter(Base):
    __tablename__ = "book_chapter"
    __table_args__ = (UniqueConstraint("book_id", "chapter_title", name="uq_book_chapter"),)

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    chapter_title = Column(Text, nullable=False)
    start_page = Column(Integer)
    end_page = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    book = relationship("Book", back_populates="chapter_entries")
    pages = relationship("PageText", back_populates="chapter", cascade="all, delete-orphan")
    toc_entries = relationship(
        "TableOfContents", back_populates="chapter", cascade="all, delete-orphan"
    )
    segments = relationship(
        "ChapterSegment", back_populates="chapter", cascade="all, delete-orphan"
    )


class PageText(Base):
    __tablename__ = "page_text"
    __table_args__ = (UniqueConstraint("book_id", "page_number", name="uq_book_page"),)

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("book_chapter.id"), nullable=True)  # Now nullable

    page_number = Column(Integer, nullable=False)
    page_text = Column(Text, nullable=False)

    book = relationship("Book", back_populates="pages")
    chapter = relationship("BookChapter", back_populates="pages")


class TableOfContents(Base):
    __tablename__ = "table_of_contents"
    __table_args__ = (
        UniqueConstraint("book_id", "level", "title", "page_number", name="uq_toc_entry"),
    )

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("book_chapter.id"), nullable=False)

    level = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=False)

    book = relationship("Book", back_populates="toc_entries")
    chapter = relationship("BookChapter", back_populates="toc_entries")


class ChapterSegment(Base):
    __tablename__ = "chapter_segment"
    __table_args__ = (UniqueConstraint("chapter_id", "heading_title", name="uq_chapter_heading"),)

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("book_chapter.id"), nullable=False)

    heading_level = Column(Integer, nullable=False)
    heading_title = Column(Text, nullable=False)
    heading_text = Column(Text)

    chapter = relationship("BookChapter", back_populates="segments")
    book = relationship("Book", back_populates="segment_entries")
    slides = relationship("SegmentSlides", back_populates="segment", cascade="all, delete-orphan")


class SegmentSlides(Base):
    __tablename__ = "segment_slide"
    __table_args__ = (UniqueConstraint("segment_id", "title", name="uq_slide_segment_title"),)

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("chapter_segment.id"), nullable=False)

    title = Column(Text, nullable=False)
    bullets = Column(JSON, nullable=False)

    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    segment = relationship("ChapterSegment", back_populates="slides")
    book = relationship("Book")  # Optional, but clearer


class ProcessingStatus(Base):
    __tablename__ = "processing_status"
    __table_args__ = (UniqueConstraint("book_id", name="uq_processing_status_book"),)

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    content_extracted = Column(Boolean, default=False, nullable=False)
    pages_extracted = Column(Boolean, default=False, nullable=False)
    chapters_segmented = Column(Boolean, default=False, nullable=False)
    slides_generated = Column(Boolean, default=False, nullable=False)
    slides_indexed = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    book = relationship("Book", back_populates="processing_status")
