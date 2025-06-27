# api/routes/deletion.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from studymathai.db import DatabaseConnection
from studymathai.models import Book, BookContent, ChapterContent, GeneratedSlide, TableOfContents, PageText, ProcessingStatus

router = APIRouter()
db = DatabaseConnection()

# ──────────────── Response Models ────────────────

class DeletionResponse(BaseModel):
    message: str
    book_id: int
    records_deleted: int
    success: bool

class CompleteDeletionResponse(BaseModel):
    message: str
    book_id: int
    success: bool
    tables_cleared: dict

# ──────────────── Deletion Endpoints ────────────────

@router.delete("/book-content/{book_id}", response_model=DeletionResponse)
def delete_book_content(book_id: int):
    """Delete all BookContent (chapters) for a specific book."""
    try:
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete all BookContent for this book
            deleted_count = session.query(BookContent).filter_by(book_id=book_id).delete()
            
        return DeletionResponse(
            message=f"Successfully deleted {deleted_count} book content records",
            book_id=book_id,
            records_deleted=deleted_count,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Book content deletion failed: {str(e)}")


@router.delete("/chapter-content/{book_id}", response_model=DeletionResponse)
def delete_chapter_content(book_id: int):
    """Delete all ChapterContent (segments) for a specific book."""
    try:
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete all ChapterContent for this book
            deleted_count = session.query(ChapterContent).filter_by(book_id=book_id).delete()
            
        return DeletionResponse(
            message=f"Successfully deleted {deleted_count} chapter content records",
            book_id=book_id,
            records_deleted=deleted_count,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chapter content deletion failed: {str(e)}")


@router.delete("/generated-slides/{book_id}", response_model=DeletionResponse)
def delete_generated_slides(book_id: int):
    """Delete all GeneratedSlides for a specific book."""
    try:
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete all GeneratedSlides for this book
            deleted_count = session.query(GeneratedSlide).filter_by(book_id=book_id).delete()
            
        return DeletionResponse(
            message=f"Successfully deleted {deleted_count} generated slide records",
            book_id=book_id,
            records_deleted=deleted_count,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generated slides deletion failed: {str(e)}")


@router.delete("/table-of-contents/{book_id}", response_model=DeletionResponse)
def delete_table_of_contents(book_id: int):
    """Delete all TableOfContents entries for a specific book."""
    try:
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete all TableOfContents for this book
            deleted_count = session.query(TableOfContents).filter_by(book_id=book_id).delete()
            
        return DeletionResponse(
            message=f"Successfully deleted {deleted_count} table of contents records",
            book_id=book_id,
            records_deleted=deleted_count,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Table of contents deletion failed: {str(e)}")


@router.delete("/page-text/{book_id}", response_model=DeletionResponse)
def delete_page_text(book_id: int):
    """Delete all PageText entries for a specific book."""
    try:
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete all PageText for this book
            deleted_count = session.query(PageText).filter_by(book_id=book_id).delete()
            
        return DeletionResponse(
            message=f"Successfully deleted {deleted_count} page text records",
            book_id=book_id,
            records_deleted=deleted_count,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Page text deletion failed: {str(e)}")


@router.delete("/processing-status/{book_id}", response_model=DeletionResponse)
def delete_processing_status(book_id: int):
    """Delete ProcessingStatus for a specific book."""
    try:
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete ProcessingStatus for this book
            deleted_count = session.query(ProcessingStatus).filter_by(book_id=book_id).delete()
            
        return DeletionResponse(
            message=f"Successfully deleted {deleted_count} processing status records",
            book_id=book_id,
            records_deleted=deleted_count,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing status deletion failed: {str(e)}")


@router.delete("/all-data/{book_id}", response_model=CompleteDeletionResponse)
def delete_all_book_data(book_id: int):
    """Delete all data across all tables for a specific book (except the book record itself)."""
    try:
        tables_cleared = {}
        
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete from all tables
            tables_cleared['generated_slides'] = session.query(GeneratedSlide).filter_by(book_id=book_id).delete()
            tables_cleared['chapter_content'] = session.query(ChapterContent).filter_by(book_id=book_id).delete()
            tables_cleared['book_content'] = session.query(BookContent).filter_by(book_id=book_id).delete()
            tables_cleared['table_of_contents'] = session.query(TableOfContents).filter_by(book_id=book_id).delete()
            tables_cleared['page_text'] = session.query(PageText).filter_by(book_id=book_id).delete()
            tables_cleared['processing_status'] = session.query(ProcessingStatus).filter_by(book_id=book_id).delete()
            
        total_deleted = sum(tables_cleared.values())
        
        return CompleteDeletionResponse(
            message=f"Successfully deleted all data for book {book_id}. Total records deleted: {total_deleted}",
            book_id=book_id,
            success=True,
            tables_cleared=tables_cleared
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete data deletion failed: {str(e)}")


@router.delete("/complete/{book_id}", response_model=CompleteDeletionResponse)
def delete_book_completely(book_id: int):
    """Delete the book and all its associated data from all tables."""
    try:
        tables_cleared = {}
        
        with db.get_session() as session:
            # Verify book exists
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete from all related tables first
            tables_cleared['generated_slides'] = session.query(GeneratedSlide).filter_by(book_id=book_id).delete()
            tables_cleared['chapter_content'] = session.query(ChapterContent).filter_by(book_id=book_id).delete()
            tables_cleared['book_content'] = session.query(BookContent).filter_by(book_id=book_id).delete()
            tables_cleared['table_of_contents'] = session.query(TableOfContents).filter_by(book_id=book_id).delete()
            tables_cleared['page_text'] = session.query(PageText).filter_by(book_id=book_id).delete()
            tables_cleared['processing_status'] = session.query(ProcessingStatus).filter_by(book_id=book_id).delete()
            
            # Finally delete the book itself
            tables_cleared['books'] = session.query(Book).filter_by(id=book_id).delete()
            
        total_deleted = sum(tables_cleared.values())
        
        return CompleteDeletionResponse(
            message=f"Successfully deleted book {book_id} and all associated data. Total records deleted: {total_deleted}",
            book_id=book_id,
            success=True,
            tables_cleared=tables_cleared
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete book deletion failed: {str(e)}") 