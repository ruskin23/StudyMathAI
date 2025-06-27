# api/routes/slides.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import json
from studymathai.generator import SlideGenerator
from studymathai.db import DatabaseConnection
from studymathai.models import Book, ChapterContent, GeneratedSlide

router = APIRouter()
db = DatabaseConnection()

# ──────────────── Response Models ────────────────

class Slide(BaseModel):
    title: str
    bullets: List[str]

class SlideDeck(BaseModel):
    segment_id: int
    heading: str
    slides: List[Slide]

class SlideGenerationResponse(BaseModel):
    message: str
    book_id: int
    success: bool
    slides_generated: int

# ──────────────── Slide Generation Endpoints ────────────────

@router.post("/generate/{book_id}", response_model=SlideGenerationResponse)
def generate_slides(book_id: int):
    """Generate slides for all segments in a book using AI."""
    try:
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            segments = session.query(ChapterContent).filter_by(book_id=book_id).all()
            if not segments:
                raise HTTPException(status_code=400, detail="No segments found. Run chapter segmentation first.")

        # Generate slides using AI
        slidegen = SlideGenerator(db)
        slides_count = slidegen.process_book(book_id)

        return SlideGenerationResponse(
            message=f"Successfully generated slides for {slides_count} segments",
            book_id=book_id,
            success=True,
            slides_generated=slides_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slide generation failed: {str(e)}")


# ──────────────── Slide Retrieval Endpoints ────────────────

@router.get("/{book_id}/all", response_model=List[SlideDeck])
def get_slides(book_id: int):
    """Get all slides for a book."""
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


@router.get("/{book_id}/segment/{segment_id}", response_model=SlideDeck)
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