# api/routes/content.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from typing import List
from studymathai.db import DatabaseConnection
from studymathai.models import Book, BookContent, ChapterContent, TableOfContents

router = APIRouter()
db = DatabaseConnection()

# ──────────────── Response Models ────────────────

class TOCEntry(BaseModel):
    id: int
    level: int
    title: str
    page_number: int
    chapter_id: int | None

class ChapterInfo(BaseModel):
    id: int
    title: str
    start_page: int
    end_page: int

class SegmentInfo(BaseModel):
    id: int
    chapter_id: int
    title: str
    level: int
    content: str



# ──────────────── Content Retrieval Endpoints ────────────────

@router.get("/{book_id}/toc", response_model=List[TOCEntry])
def get_toc(book_id: int):
    """Get table of contents for a book."""
    with db.get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        entries = session.query(TableOfContents).filter_by(book_id=book.id).all()
        
    return [
        TOCEntry(
            id=e.id,
            level=e.level,
            title=e.title,
            page_number=e.page_number,
            chapter_id=e.chapter_id
        ) for e in entries
    ]

@router.get("/{book_id}/chapters", response_model=List[ChapterInfo])
def get_chapters(book_id: int):
    """Get chapters for a book."""
    with db.get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        chapters = session.query(BookContent).filter_by(book_id=book.id).all()
        
    return [
        ChapterInfo(
            id=c.id,
            title=c.chapter_title,
            start_page=c.start_page,
            end_page=c.end_page
        ) for c in chapters
    ]

@router.get("/{book_id}/segments", response_model=List[SegmentInfo])
def get_segments(book_id: int):
    """Get segments for a book."""
    with db.get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        segments = session.query(ChapterContent).filter_by(book_id=book.id).all()
        
    return [
        SegmentInfo(
            id=s.id,
            chapter_id=s.chapter_id,
            title=s.heading_title,
            level=s.heading_level,
            content=s.content_text
        ) for s in segments
    ]



@router.get("/{book_id}/segments/{segment_id}", response_model=SegmentInfo)
def get_segment_detail(book_id: int, segment_id: int):
    """Get detailed information about a specific segment."""
    with db.get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        segment = session.query(ChapterContent).filter_by(
            id=segment_id, 
            book_id=book_id
        ).first()
        
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        
    return SegmentInfo(
        id=segment.id,
        chapter_id=segment.chapter_id,
        title=segment.heading_title,
        level=segment.heading_level,
        content=segment.content_text
    )

 