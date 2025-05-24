
# api/routes/books.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
from studymathai.processor import PageTextExtractor, BookContentExtractor, BookProcessor
from studymathai.generator import SlideGenerator
from studymathai.db import DatabaseManager
from studymathai.utils import TextCleaner
from studymathai.processor import PageAwareChapterSegmentor

router = APIRouter()

data_dir = os.getenv("PDF_DIRECTORY", "./uploads")
os.makedirs(data_dir, exist_ok=True)

class ProcessResponse(BaseModel):
    message: str
    book_id: int
    title: str

@router.post("/process", response_model=ProcessResponse)
def process_pdf(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        filepath = os.path.join(data_dir, file.filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        db = DatabaseManager()
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
