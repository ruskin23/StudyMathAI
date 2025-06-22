import os
import re
import fitz
from sqlalchemy.exc import IntegrityError
import numpy as np
from sentence_transformers import SentenceTransformer, util
    
from .db import DatabaseConnection
from .models import PageText, BookContent, ChapterContent, Book, TableOfContents
from .utils import TextCleaner
from studymathai.logging_config import get_logger
import hashlib
import json

logger = get_logger(__name__)


class BookProcessor:
    """
    Orchestrates registration and shared PDF context for extractors.
    """
    def __init__(self, filepath: str, db: DatabaseConnection):
        self.filepath = filepath
        self.db = db
        self.doc = fitz.open(filepath)
        self.book = self._register_book()

    def _compute_hash(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(self.filepath.encode('utf-8'))
        with open(self.filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _register_book(self):
        book_hash = self._compute_hash()
        title = self.doc.metadata.get("title") or os.path.splitext(os.path.basename(self.filepath))[0]
        
        with self.db.get_session() as session:
            # Check if book already exists
            existing = session.query(Book).filter_by(book_hash=book_hash).first()
            if existing:
                return existing
            
            # Create new book
            book = Book(book_hash=book_hash, file_path=self.filepath, title=title)
            session.add(book)
            try:
                session.commit()
                session.refresh(book)
                return book
            except IntegrityError:
                session.rollback()
                return session.query(Book).filter_by(book_hash=book_hash).first()


class PageTextExtractor:
    """
    Extracts page-by-page text content from PDF using the BookProcessor context.
    """
    def __init__(self, processor: BookProcessor):
        self.processor = processor
        self.db = processor.db
        self.book = processor.book
        self.doc = processor.doc

    def extract_and_store_pages(self):
        with self.db.get_session() as session:
            for page_num in range(self.doc.page_count):
                page = self.doc.load_page(page_num)
                text = page.get_text()
                
                # Check if page already exists
                existing = session.query(PageText).filter_by(
                    book_id=self.book.id, 
                    page_number=page_num
                ).first()
                
                if not existing:
                    page_text = PageText(
                        book_id=self.book.id,
                        page_number=page_num,
                        page_text=text
                    )
                    session.add(page_text)
        
        logger.info(f"✅ Extracted {self.doc.page_count} pages for book ID {self.book.id}")


class BookContentExtractor:
    """
    Extracts chapter-level content and TOC entries from a PDF using the BookProcessor context.
    Assumes the book has already been registered and PageText has been stored.
    """
    def __init__(self, processor: BookProcessor):
        self.processor = processor
        self.db = processor.db
        self.book = processor.book
        self.doc = processor.doc
        self.toc = self.doc.get_toc(simple=True)

    def _clean_title(self, title: str) -> str:
        return re.sub(r'[\uD800-\uDFFF\u0000-\u001F]+', '', title).strip()

    def _get_filtered_chapter_ranges(self):
        toc = self.toc
        filtered = []

        for i, (level, title, page) in enumerate(toc):
            if level != 1:
                continue
            next_level = toc[i + 1][0] if i + 1 < len(toc) else None
            if next_level == 2:
                filtered.append((self._clean_title(title), page))

        if filtered and "index" in filtered[-1][0].lower():
            filtered.pop()

        chapter_ranges = []
        for i, (title, start_page) in enumerate(filtered):
            start = start_page - 1
            end = filtered[i + 1][1] - 1 if i + 1 < len(filtered) else self.doc.page_count - 1
            chapter_ranges.append((title, start, end))

        return chapter_ranges

    def _extract_text(self, start: int, end: int) -> str:
        return "\n".join(self.doc.load_page(i).get_text() for i in range(start, end + 1))

    def _save_toc_to_db(self, chapter_ranges_with_objs):
        with self.db.get_session() as session:
            for level, title, page in self.toc:
                chapter_id = None
                if level > 1:
                    for _, start, end, chapter_obj in chapter_ranges_with_objs:
                        if start <= page - 1 <= end:
                            chapter_id = chapter_obj.id
                            break

                # Check if TOC entry already exists
                existing = session.query(TableOfContents).filter_by(
                    book_id=self.book.id,
                    level=level,
                    title=title,
                    page_number=page
                ).first()
                
                if not existing:
                    toc_entry = TableOfContents(
                        book_id=self.book.id,
                        chapter_id=chapter_id,
                        level=level,
                        title=title,
                        page_number=page,
                        parent_id=None  # You might want to implement parent_id logic
                    )
                    session.add(toc_entry)

    def extract_and_save(self):
        with self.db.get_session() as session:
            existing_titles = {c.chapter_title for c in session.query(BookContent).filter_by(book_id=self.book.id).all()}
        
        chapter_ranges_with_objs = []

        for title, start, end in self._get_filtered_chapter_ranges():
            if title in existing_titles:
                continue

            text = self._extract_text(start, end)
            
            with self.db.get_session() as session:
                chapter = BookContent(
                    book_id=self.book.id,
                    chapter_title=title,
                    chapter_text=text.strip(),
                    start_page=start,
                    end_page=end
                )
                session.add(chapter)
                try:
                    session.commit()
                    session.refresh(chapter)
                    chapter_ranges_with_objs.append((title, start, end, chapter))
                except IntegrityError:
                    session.rollback()
                    existing = session.query(BookContent).filter_by(
                        book_id=self.book.id, 
                        chapter_title=title
                    ).first()
                    if existing:
                        chapter_ranges_with_objs.append((title, start, end, existing))

        self._save_toc_to_db(chapter_ranges_with_objs)
        logger.info(f"✅ Extracted chapters and TOC for book ID {self.book.id}")



class PageAwareChapterSegmentor:
    """
    Segments chapters by matching TOC headings to actual text locations using page-level text and similarity.
    """
    EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

    def __init__(self, processor: BookProcessor, chapter: BookContent, text_cleaner: TextCleaner):
        self.processor = processor
        self.chapter = chapter
        self.db = processor.db
        self.book = processor.book
        self.text_cleaner = text_cleaner
        
        with self.db.get_session() as session:
            self.headings = session.query(TableOfContents).filter(
                TableOfContents.chapter_id == chapter.id,
                TableOfContents.level > 1
            ).all()
            
            pages = session.query(PageText).filter_by(book_id=chapter.book_id).all()
            self.page_texts = {p.page_number: p.page_text for p in pages}

    def _find_heading_line(self, heading_title: str, page_text: str):
        lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        lines_clean = [self.text_cleaner.clean(line) for line in lines]
        heading_clean = self.text_cleaner.clean(heading_title)

        line_embeddings = self.EMBED_MODEL.encode(lines_clean)
        heading_embedding = self.EMBED_MODEL.encode([heading_clean])[0]

        scores = util.cos_sim(heading_embedding, line_embeddings)[0].cpu().numpy()
        best_idx = int(np.argmax(scores))
        
        # Heuristic: Avoid header if another match is very close in score
        if best_idx == 0 and len(scores) > 1:
            sorted_indices = np.argsort(scores)[::-1]  # descending order
            second_best_idx = int(sorted_indices[1])
            if scores[second_best_idx] >= 0.9 * scores[best_idx]:
                best_idx = second_best_idx

        return lines, best_idx

    def segment_and_store(self):
        if not self.headings:
            logger.info(f"No TOC entries found for chapter {self.chapter.id}")
            return

        all_lines = []
        line_map = []
        for pg in range(self.chapter.start_page, self.chapter.end_page + 1):
            lines = [line.strip() for line in self.page_texts.get(pg, '').splitlines() if line.strip()]
            all_lines.extend(lines)
            line_map.extend([(pg, i) for i in range(len(lines))])

        heading_locs = []
        for heading in self.headings:
            page = heading.page_number - 1
            lines = [line.strip() for line in self.page_texts.get(page, '').splitlines() if line.strip()]
            if not lines:
                continue
            raw_lines, idx = self._find_heading_line(heading.title, "\n".join(lines))

            prior_lines = sum(len([line.strip() for line in self.page_texts.get(pn, '').splitlines() if line.strip()])
                              for pn in range(self.chapter.start_page, page))
            heading_locs.append((heading, prior_lines + idx))

        heading_locs.sort(key=lambda x: x[1])

        # Add main chapter segment
        first_idx = heading_locs[0][1] if heading_locs else len(all_lines)
        pre_text = "\n".join(all_lines[:first_idx])
        
        with self.db.get_session() as session:
            existing = session.query(ChapterContent).filter_by(
                chapter_id=self.chapter.id,
                heading_title=self.chapter.chapter_title
            ).first()
            
            if not existing:
                segment = ChapterContent(
                    chapter_id=self.chapter.id,
                    book_id=self.book.id,
                    heading_level=1,
                    heading_title=self.chapter.chapter_title,
                    content_text=pre_text.strip(),
                    parent_id=None
                )
                session.add(segment)

        # Add sub-segments
        for i, (heading, idx) in enumerate(heading_locs):
            start = idx
            end = heading_locs[i + 1][1] if i + 1 < len(heading_locs) else len(all_lines)
            segment_text = "\n".join(all_lines[start:end])

            with self.db.get_session() as session:
                existing = session.query(ChapterContent).filter_by(
                    chapter_id=self.chapter.id,
                    heading_title=heading.title
                ).first()
                
                if not existing:
                    segment = ChapterContent(
                        chapter_id=self.chapter.id,
                        book_id=self.book.id,
                        heading_level=heading.level,
                        heading_title=heading.title,
                        content_text=segment_text.strip(),
                        parent_id=heading.parent_id
                    )
                    session.add(segment)

        logger.info(f"✅ Segmented chapter {self.chapter.chapter_title} (ID: {self.chapter.id})")
