
# api/routes/books.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import json
import shutil
from typing import List
from studymathai.processor import PageTextExtractor, BookContentExtractor, BookProcessor
from studymathai.generator import SlideGenerator
from studymathai.db import DatabaseManager
from studymathai.utils import TextCleaner
from studymathai.processor import PageAwareChapterSegmentor

router = APIRouter()
db = DatabaseManager()

data_dir = os.getenv("PDF_DIRECTORY", "./uploads")
os.makedirs(data_dir, exist_ok=True)


# ──────────────── Response Models ────────────────

class ProcessResponse(BaseModel):
    message: str
    book_id: int
    title: str
    
    
class BookMetadata(BaseModel):
    id: int
    title: str
    file_path: str

class BookDetail(BookMetadata):
    created_at: str


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


# ──────────────── Endpoints ────────────────


@router.post("/process", response_model=ProcessResponse)
def process_pdf(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        filepath = os.path.join(data_dir, file.filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        text_cleaner = TextCleaner()

        # Run pipeline
        # === 2. Book context ===
        processor = BookProcessor(filepath, db)

        # === 3. Extract page-level text ===
        page_extractor = PageTextExtractor(processor)
        page_extractor.extract_and_store_pages()

        # === 4. Extract chapters and TOC entries ===
        content_extractor = BookContentExtractor(processor)
        content_extractor.extract_and_save()

        # === 5. Segment each chapter into heading-text blocks
        for chapter in db.get_chapters_by_book(processor.book.id):
            print(f"Segmenting chapter: {chapter.chapter_title}")
            segmentor = PageAwareChapterSegmentor(processor, chapter, text_cleaner)
            segmentor.segment_and_store()

        # === 6. Generate slides for segments
        slidegen = SlideGenerator(db)
        slidegen.process_book(processor.book.id)

        print("✅ All processing complete.")

        book_id = processor.book.id
        book_title = processor.book.title

        return {
            "message": "Book processed and slides generated.",
            "book_id": book_id,
            "title": book_title,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[BookMetadata])
def list_books():
    books = db.get_books()
    return [
        BookMetadata(id=b.id, title=b.title, file_path=b.file_path)
        for b in books
    ]


@router.get("/{book_id}", response_model=BookDetail)
def get_book(book_id: int):
    book = db.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookDetail(
        id=book.id,
        title=book.title,
        file_path=book.file_path,
        created_at=str(book.created_at)
    )

@router.get("/{book_id}/toc", response_model=List[TOCEntry])
def get_toc(book_id: int):
    book = db.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    entries = db.get_toc_for_book(book.id)
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
    book = db.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    chapters = db.get_chapters_by_book(book.id)
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
    book = db.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    segments = db.get_segments_by_book(book.id)
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
    book = db.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    segments = db.get_segments_by_book(book.id)
    result = []
    for segment in segments:
        slide_obj = db.get_slides_for_segment(segment.id)
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
