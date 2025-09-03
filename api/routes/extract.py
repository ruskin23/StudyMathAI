from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import get_db_session
from studymathai.repositories import BooksRepository
from studymathai.services.extraction import (
    extract_and_save_metadata,
    extract_and_save_pages,
    segment_and_save,
)

router = APIRouter()


class MetadataResponse(BaseModel):
    id: int
    message: str


class PageTextResponse(BaseModel):
    id: int
    num_pages: int
    message: str


@router.post("/metadata/{book_id}", response_model=MetadataResponse)
def extract_metadata(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        book = BooksRepository(session).get(book_id)
        ch_created, toc_created = extract_and_save_metadata(session, book.id)

        return MetadataResponse(id=book.id, message="Successfully extracted metadata")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed error: {str(e)}",
        ) from e


@router.post("/pages/{book_id}", response_model=PageTextResponse)
def extract_page_text(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        book = BooksRepository(session).get(book_id)
        pages_created = extract_and_save_pages(session, book.id)

        return PageTextResponse(
            id=book.id, num_pages=pages_created, message="Successfully extracted text from pages"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed error: {str(e)}",
        ) from e


@router.post("/segments/{book_id}", response_model=PageTextResponse)
def extract_chapter_segments(
    book_id: int, session: Session = Depends(get_db_session)
):  # noqa: B008
    try:
        book = BooksRepository(session).get(book_id)
        created_total = segment_and_save(session, book.id)

        return PageTextResponse(
            id=book.id,
            num_pages=created_total,
            message="Successfully segmented chapters and saved segments",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed error: {str(e)}",
        ) from e
