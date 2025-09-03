import os
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import get_db_session
from studymathai.repositories.books import BooksRepository

router = APIRouter()


class UploadResponse(BaseModel):
    message: str
    book_id: int
    title: str
    file_path: str
    created_at: datetime


class BookMetadata(BaseModel):
    id: int
    title: str
    file_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/upload", response_model=UploadResponse)
def upload_book(
    file: UploadFile = File(...), session: Session = Depends(get_db_session)  # noqa: B008
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        data_dir = os.getenv("PDF_DIRECTORY", "./uploads")
        os.makedirs(data_dir, exist_ok=True)

        filepath = os.path.join(data_dir, file.filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        repo = BooksRepository(session)
        book = repo.register_from_file(filepath)
        book_obj = BookMetadata.model_validate(book)

        return UploadResponse(
            message="Book uploaded and registered successfully",
            book_id=book_obj.id,
            title=book_obj.title,
            file_path=book_obj.file_path,
            created_at=book_obj.created_at,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}") from e


@router.get("/", response_model=list[BookMetadata])
def list_books(session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        books = BooksRepository(session).list()
        return [BookMetadata.model_validate(book) for book in books]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.get("/{book_id}", response_model=BookMetadata)
def get_book(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        book = BooksRepository(session).get(book_id)
        return BookMetadata.model_validate(book)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.delete("/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        BooksRepository(session).delete(book_id)
        return {"message": f"Book {book_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e
