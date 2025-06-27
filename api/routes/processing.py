# api/routes/processing.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from studymathai.processor import PageTextExtractor, BookContentExtractor, BookProcessor

from studymathai.db import DatabaseConnection
from studymathai.models import Book, BookContent, ChapterContent
from studymathai.utils import TextCleaner
from studymathai.processor import PageAwareChapterSegmentor
from studymathai.processing_status import ProcessingStatusManager

router = APIRouter()
db = DatabaseConnection()
status_manager = ProcessingStatusManager(db)

# ──────────────── Response Models ────────────────

class ProcessingStatusResponse(BaseModel):
    book_id: int
    content_extracted: bool
    pages_extracted: bool
    chapters_segmented: bool
    slides_generated: bool
    slides_indexed: bool
    created_at: str
    updated_at: str

class ProcessingResponse(BaseModel):
    message: str
    book_id: int
    success: bool

class PageExtractionResponse(ProcessingResponse):
    pages_extracted: int

class ContentExtractionResponse(ProcessingResponse):
    chapters_extracted: int
    toc_entries_extracted: int

class SegmentationResponse(ProcessingResponse):
    segments_created: int



# ──────────────── Processing Endpoints ────────────────

@router.post("/extract-pages/{book_id}", response_model=PageExtractionResponse)
def extract_pages(book_id: int):
    """Extract page-level text from a book."""
    try:
        # Get book file path
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            book_file_path = book.file_path

        # Initialize processor - it handles its own book registration/lookup
        processor = BookProcessor(book_file_path, db)

        # Extract page-level text
        page_extractor = PageTextExtractor(processor)
        page_count = page_extractor.extract_and_store_pages()

        # Set the pages_extracted flag to True
        status_manager.set_pages_extracted(book_id)

        return PageExtractionResponse(
            message=f"Successfully extracted {page_count} pages",
            book_id=book_id,
            success=True,
            pages_extracted=page_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Page extraction failed: {str(e)}")


@router.post("/extract-content/{book_id}", response_model=ContentExtractionResponse)
def extract_content(book_id: int):
    """Extract chapters and table of contents from a book."""
    try:
        # Get book file path
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            book_file_path = book.file_path

        # Initialize processor - it handles its own book registration/lookup
        processor = BookProcessor(book_file_path, db)

        # Extract chapters and TOC entries
        content_extractor = BookContentExtractor(processor)
        chapters_count, toc_count = content_extractor.extract_and_save()

        # Set the content_extracted flag to True
        status_manager.set_content_extracted(book_id)

        return ContentExtractionResponse(
            message=f"Successfully extracted {chapters_count} chapters and {toc_count} TOC entries",
            book_id=book_id,
            success=True,
            chapters_extracted=chapters_count,
            toc_entries_extracted=toc_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content extraction failed: {str(e)}")


@router.post("/segment-chapters/{book_id}", response_model=SegmentationResponse)
def segment_chapters(book_id: int):
    """Segment chapters into heading-text blocks."""
    try:
        # Get book file path and verify chapters exist
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            book_file_path = book.file_path
            
            chapters_count = session.query(BookContent).filter_by(book_id=book_id).count()
            if chapters_count == 0:
                raise HTTPException(status_code=400, detail="No chapters found. Run content extraction first.")

        # Initialize processor - it handles its own book registration/lookup
        processor = BookProcessor(book_file_path, db)
        text_cleaner = TextCleaner()

        # Process chapters within their own session contexts
        total_segments = 0
        with db.get_session() as session:
            chapters = session.query(BookContent).filter_by(book_id=book_id).all()
            for chapter in chapters:
                print(f"Segmenting chapter: {chapter.chapter_title}")
                segmentor = PageAwareChapterSegmentor(processor, chapter, text_cleaner)
                segments_count = segmentor.segment_and_store()
                total_segments += segments_count

        # Set the chapters_segmented flag to True
        status_manager.set_chapters_segmented(book_id)

        return SegmentationResponse(
            message=f"Successfully segmented {chapters_count} chapters into {total_segments} segments",
            book_id=book_id,
            success=True,
            segments_created=total_segments
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chapter segmentation failed: {str(e)}")


@router.post("/process-complete/{book_id}", response_model=ProcessingResponse)
def process_complete_pipeline(book_id: int):
    """Run the complete PDF processing pipeline for a book (excludes AI slide generation)."""
    try:
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")

        # Run PDF processing steps in sequence (no AI slide generation)
        extract_pages(book_id)
        extract_content(book_id)
        segment_chapters(book_id)

        return ProcessingResponse(
            message="Complete PDF processing pipeline executed successfully",
            book_id=book_id,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete pipeline processing failed: {str(e)}")


@router.get("/status/{book_id}", response_model=ProcessingStatusResponse)
def get_processing_status(book_id: int):
    """Get the current processing status for a book."""
    try:
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
        
        # Get or create processing status
        status_data = status_manager.get_processing_status(book_id)
        
        return ProcessingStatusResponse(
            book_id=book_id,
            content_extracted=status_data['content_extracted'],
            pages_extracted=status_data['pages_extracted'],
            chapters_segmented=status_data['chapters_segmented'],
            slides_generated=status_data['slides_generated'],
            slides_indexed=status_data['slides_indexed'],
            created_at=status_data['created_at'].isoformat() if status_data['created_at'] else None,
            updated_at=status_data['updated_at'].isoformat() if status_data['updated_at'] else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get processing status: {str(e)}") 