from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import get_db_session
from studymathai.repositories import (
    BooksRepository,
    ChaptersRepository,
    PagesRepository,
    ProcessingStatusRepository,
    SegmentsRepository,
    SlidesRepository,
    TOCRepository,
)

router = APIRouter()


class TOCResponse(BaseModel):
    id: int
    book_id: int
    level: int
    title: str
    page_number: int

    model_config = {"from_attributes": True}


class ChapterResponse(BaseModel):
    id: int
    book_id: int
    chapter_title: str
    start_page: int
    end_page: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PageResponse(BaseModel):
    id: int
    book_id: int
    chapter_id: int | None = None
    page_number: int
    page_text: str

    model_config = {"from_attributes": True}


class SegmentResponse(BaseModel):
    id: int
    book_id: int
    chapter_id: int
    heading_level: int
    heading_title: str
    heading_text: str | None = None

    model_config = {"from_attributes": True}


class SlideResponse(BaseModel):
    id: int
    book_id: int
    segment_id: int
    title: str
    bullets: list[str]

    model_config = {"from_attributes": True}


class ProcessingStatusResponse(BaseModel):
    book_id: int
    content_extracted: bool
    pages_extracted: bool
    chapters_segmented: bool
    slides_generated: bool
    slides_indexed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("/metadata/toc/{book_id}", response_model=list[TOCResponse])
def get_toc_metadata(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        # Ensure book exists and list TOC via repository
        BooksRepository(session).get(book_id)
        tocs = TOCRepository(session).list_for_book(book_id)
        return [TOCResponse.model_validate(toc) for toc in tocs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.get("/metadata/chapters/{book_id}", response_model=list[ChapterResponse])
def get_chapters_metadata(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        # Ensure book exists and list chapters via repository
        BooksRepository(session).get(book_id)
        chapters = ChaptersRepository(session).list_for_book(book_id)
        return [ChapterResponse.model_validate(ch) for ch in chapters]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.get("/pages/{book_id}", response_model=list[PageResponse])
def list_pages(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        BooksRepository(session).get(book_id)
        pages = PagesRepository(session).list_for_book(book_id)
        return [PageResponse.model_validate(p) for p in pages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.get("/segments/{book_id}", response_model=list[SegmentResponse])
def list_segments(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        BooksRepository(session).get(book_id)
        segments = SegmentsRepository(session).list_for_book(book_id)
        return [SegmentResponse.model_validate(s) for s in segments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.get("/slides/by-book/{book_id}", response_model=list[SlideResponse])
def list_slides_by_book(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        BooksRepository(session).get(book_id)
        slides = SlidesRepository(session).list_for_book(book_id)
        return [SlideResponse.model_validate(s) for s in slides]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.get("/slides/by-segment/{segment_id}", response_model=list[SlideResponse])
def list_slides_by_segment(
    segment_id: int, session: Session = Depends(get_db_session)
):  # noqa: B008
    try:
        slides = SlidesRepository(session).list_for_segment_id(segment_id)
        return [SlideResponse.model_validate(s) for s in slides]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e


@router.get("/status/{book_id}", response_model=ProcessingStatusResponse)
def get_processing_status(book_id: int, session: Session = Depends(get_db_session)):  # noqa: B008
    try:
        BooksRepository(session).get(book_id)
        status = ProcessingStatusRepository(session).ensure_for_book(book_id)
        return ProcessingStatusResponse.model_validate(status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}") from e
