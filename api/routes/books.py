# api/routes/books.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
from typing import List, Optional
from studymathai.processor import BookProcessor
from studymathai.db import DatabaseConnection
from studymathai.models import Book

router = APIRouter()
db = DatabaseConnection()

data_dir = os.getenv("PDF_DIRECTORY", "./uploads")
os.makedirs(data_dir, exist_ok=True)

# ──────────────── Response Models ────────────────

class UploadResponse(BaseModel):
    message: str
    book_id: int
    title: str
    file_path: str

class BookMetadata(BaseModel):
    id: int
    title: str
    file_path: str

class BookDetail(BookMetadata):
    created_at: str

class BookUpdateRequest(BaseModel):
    title: Optional[str] = None

# ──────────────── Book Management Endpoints ────────────────

@router.post("/upload", response_model=UploadResponse)
def upload_book(file: UploadFile = File(...)):
    """Upload and register a new book."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file
        filepath = os.path.join(data_dir, file.filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Register book in database
        processor = BookProcessor(filepath, db)

        return UploadResponse(
            message="Book uploaded and registered successfully",
            book_id=processor.book_data['id'],
            title=processor.book_data['title'],
            file_path=processor.book_data['file_path']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=List[BookMetadata])
def list_books():
    """Get all books."""
    with db.get_session() as session:
        books = session.query(Book).all()
        return [
            BookMetadata(id=b.id, title=b.title, file_path=b.file_path)
            for b in books
        ]

@router.get("/{book_id}", response_model=BookDetail)
def get_book(book_id: int):
    """Get details of a specific book."""
    with db.get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return BookDetail(
            id=book.id,
            title=book.title,
            file_path=book.file_path,
            created_at=str(book.created_at)
        )

@router.delete("/{book_id}")
def delete_book(book_id: int):
    """Delete a book and its associated data."""
    try:
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Delete the physical file if it exists
            if os.path.exists(book.file_path):
                os.remove(book.file_path)
            
            # Delete from database (this should cascade to related tables)
            session.delete(book)
            
        return {"message": f"Book {book_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.put("/{book_id}", response_model=BookDetail)
def update_book(book_id: int, update_data: BookUpdateRequest):
    """Update book metadata."""
    try:
        with db.get_session() as session:
            book = session.query(Book).filter_by(id=book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            if update_data.title:
                book.title = update_data.title
            
            session.refresh(book)
            
            return BookDetail(
                id=book.id,
                title=book.title,
                file_path=book.file_path,
                created_at=str(book.created_at)
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")
