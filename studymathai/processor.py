import os
import re
import fitz
from sqlalchemy.exc import IntegrityError
import numpy as np
from sentence_transformers import SentenceTransformer, util
    
from .db import DatabaseManager
from .models import PageText, BookContent, ChapterContent
from .utils import TextCleaner
from studymathai.logging_config import get_logger

logger = get_logger(__name__)


class BookProcessor:
    """
    Orchestrates registration and shared PDF context for extractors.
    """
    def __init__(self, filepath: str, db: DatabaseManager):
        self.filepath = filepath
        self.db = db
        self.doc = fitz.open(filepath)
        self.book = self._register_book()

    def _compute_hash(self) -> str:
        import hashlib
        hasher = hashlib.sha256()
        hasher.update(self.filepath.encode('utf-8'))
        with open(self.filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _register_book(self):
        book_hash = self._compute_hash()
        existing = self.db.get_book_by_hash(book_hash)
        title = self.doc.metadata.get("title") or os.path.splitext(os.path.basename(self.filepath))[0]
        return existing or self.db.add_book(book_hash, self.filepath, title)


class PageTextExtractor:
    """
    Extracts and stores page-level text for a given book using the BookProcessor context.
    """
    def __init__(self, processor: BookProcessor):
        self.processor = processor
        self.doc = processor.doc
        self.db = processor.db
        self.book = processor.book

    def extract_and_store_pages(self):
        for page_num in range(self.doc.page_count):
            text = self.doc.load_page(page_num).get_text()
            try:
                self.db.add_page_text(
                    book_id=self.book.id,
                    page_number=page_num,
                    page_text=text.strip()
                )
            except IntegrityError:
                continue
        logger.info(f"✅ Stored {self.doc.page_count} pages for book ID {self.book.id}")


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
        for level, title, page in self.toc:
            chapter_id = None
            if level > 1:
                for _, start, end, chapter_obj in chapter_ranges_with_objs:
                    if start <= page - 1 <= end:
                        chapter_id = chapter_obj.id
                        break

            self.db.add_toc_entry(
                book_id=self.book.id,
                level=level,
                title=title,
                page_number=page,
                chapter_id=chapter_id
            )

    def extract_and_save(self):
        existing_titles = {c.chapter_title for c in self.db.get_chapters_by_book(self.book.id)}
        chapter_ranges_with_objs = []

        for title, start, end in self._get_filtered_chapter_ranges():
            if title in existing_titles:
                continue

            text = self._extract_text(start, end)
            chapter = self.db.add_chapter(
                book_id=self.book.id,
                title=title,
                text=text.strip(),
                start=start,
                end=end
            )
            chapter_ranges_with_objs.append((title, start, end, chapter))

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
        self.headings = self.db.get_toc_for_chapter(chapter.id)
        self.page_texts = {p.page_number: p.page_text for p in self.db.get_pages_by_book(chapter.book_id)}

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

        first_idx = heading_locs[0][1] if heading_locs else len(all_lines)
        pre_text = "\n".join(all_lines[:first_idx])
        self.db.add_chapter_segment(
            chapter_id=self.chapter.id,
            book_id=self.book.id,
            level=1,
            title=self.chapter.chapter_title,
            text=pre_text.strip()
        )

        for i, (heading, idx) in enumerate(heading_locs):
            start = idx
            end = heading_locs[i + 1][1] if i + 1 < len(heading_locs) else len(all_lines)
            segment_text = "\n".join(all_lines[start:end])

            self.db.add_chapter_segment(
                chapter_id=self.chapter.id,
                book_id=self.book.id,
                level=heading.level,
                title=heading.title,
                text=segment_text.strip(),
                parent_id=heading.parent_id
            )

        logger.info(f"✅ Segmented chapter {self.chapter.chapter_title} (ID: {self.chapter.id})")
