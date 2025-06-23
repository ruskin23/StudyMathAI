# api/routes/content.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from typing import List
from studymathai.db import DatabaseConnection
from studymathai.models import Book, BookContent, ChapterContent, TableOfContents, GeneratedSlide

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

class Slide(BaseModel):
    title: str
    bullets: List[str]

class SlideDeck(BaseModel):
    segment_id: int
    heading: str
    slides: List[Slide]

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

@router.get("/{book_id}/slides", response_model=List[SlideDeck])
def get_slides(book_id: int):
    """Get slides for a book."""
    with db.get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        segments = session.query(ChapterContent).filter_by(book_id=book.id).all()
        
    result = []
    for segment in segments:
        with db.get_session() as session:
            slide_obj = session.query(GeneratedSlide).filter_by(content_id=segment.id).first()
            
        if slide_obj:
            try:
                parsed = json.loads(slide_obj.slides_json)
                result.append(SlideDeck(
                    segment_id=segment.id,
                    heading=parsed.get("heading", segment.heading_title),
                    slides=[Slide(**s) for s in parsed.get("slides", [])]
                ))
            except Exception:
                continue
    return result

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

@router.get("/{book_id}/segments/{segment_id}/slides", response_model=SlideDeck)
def get_segment_slides(book_id: int, segment_id: int):
    """Get slides for a specific segment."""
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
            
        slide_obj = session.query(GeneratedSlide).filter_by(content_id=segment_id).first()
        
    if not slide_obj:
        raise HTTPException(status_code=404, detail="Slides not found for this segment")
    
    try:
        parsed = json.loads(slide_obj.slides_json)
        return SlideDeck(
            segment_id=segment_id,
            heading=parsed.get("heading", segment.heading_title),
            slides=[Slide(**s) for s in parsed.get("slides", [])]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing slides: {str(e)}") 