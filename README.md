# StudyMathAI

<div align="center">
  <img src="StudyMath.ai.png" alt="StudyMathAI Logo">
</div>

Transform PDF textbooks into structured, searchable content with a clean REST API.

## Overview

StudyMathAI processes PDF textbooks by:
1. **PDF Processing**: Extract text, TOC/chapters, and heading-based segments
2. **REST API**: Manage uploads and retrieve content (books/TOC/chapters/pages/segments/slides)

**Key Architecture**: The PDF processing pipeline is independent and runs on PDF + NLP tooling. No auth by default. CORS enabled for development.

## Quick Start

### Prerequisites
- Python 3.12+

### Installation

```bash
git clone https://github.com/yourusername/studymathai.git
cd studymathai
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Environment Setup

Create a `.env` file (optional):
```env
SQLITE_DB_NAME=studymathai.db
PDF_DIRECTORY=./uploads
```

### Start the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation: `http://localhost:8000/docs`

## API Endpoints

### 📚 Books (`/books`)
- POST `/books/upload` — Upload and register a PDF (multipart field `file`)
- GET `/books/` — List all books
- GET `/books/{book_id}` — Get book details
- DELETE `/books/{book_id}` — Delete a book and associated data

### 🔄 Extract (`/extract`)
- POST `/extract/metadata/{book_id}` — Extract TOC and chapters
- POST `/extract/pages/{book_id}` — Extract page text
- POST `/extract/segments/{book_id}` — Segment into heading-text sections

### 📖 Content (`/content`)
- GET `/content/metadata/toc/{book_id}` — Table of contents
- GET `/content/metadata/chapters/{book_id}` — Chapters
- GET `/content/pages/{book_id}` — Page text
- GET `/content/segments/{book_id}` — Segments
- GET `/content/slides/by-book/{book_id}` — Slides for the book
- GET `/content/slides/by-segment/{segment_id}` — Slides for a segment
- GET `/content/status/{book_id}` — Processing status flags

## Usage Examples

### Basic PDF Processing

```bash
# 1. Upload PDF
curl -X POST "http://localhost:8000/books/upload" \
     -F "file=@textbook.pdf"

# 2. Extract metadata (TOC + chapters)
curl -X POST "http://localhost:8000/extract/metadata/1"

# 3. Extract pages (plain text per page)
curl -X POST "http://localhost:8000/extract/pages/1"

# 4. Segment content (heading → text)
curl -X POST "http://localhost:8000/extract/segments/1"

# 5. Get segments
curl -X GET "http://localhost:8000/content/segments/1"
```

### Python Integration

```python
import requests

# Upload and process PDF
with open("textbook.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/books/upload",
        files={"file": f}
    )
    book_id = response.json()["book_id"]

# Extract content
requests.post(f"http://localhost:8000/extract/metadata/{book_id}")
requests.post(f"http://localhost:8000/extract/pages/{book_id}")
requests.post(f"http://localhost:8000/extract/segments/{book_id}")

# Get heading-text segments
segments = requests.get(f"http://localhost:8000/content/segments/{book_id}")
print(f"Found {len(segments.json())} segments")
```

## Project Structure

```
api/
├── main.py                  # FastAPI app (CORS + routers)
├── utils.py                 # DB session dependency
└── routes/
    ├── books.py            # Upload/list/get/delete books
    ├── extract.py          # Extract metadata/pages/segments
    └── content.py          # TOC/chapters/pages/segments/slides/status

studymathai/
├── database/
│   ├── core.py             # DB engine/session factory
│   └── models.py           # SQLAlchemy models
├── repositories/           # CRUD/data access
│   ├── books.py, pages.py, chapters.py, toc.py,
│   ├── segments.py, slides.py, status.py
├── services/extraction.py  # Orchestration for pipeline steps
├── processing/             # PDF/segmentation logic (fitz + sbert)
│   ├── extraction.py       # TOC/pages parsing
│   └── segmentation.py     # Heading-based segmentation
├── data_models.py          # Pydantic models for processing
└── logging_config.py       # Logger helper
```

## Processing Workflow

### PDF Processing Workflow
```
Upload PDF → Extract Metadata → Extract Pages → Segment → Retrieve Content
```

## Database Schema

- **Book**: PDF metadata and file information
- **PageText**: Raw text content per page
- **BookChapter**: Chapter-level content
- **ChapterSegment**: Section segments with heading-text pairs
- **TableOfContents**: Document structure
- **SegmentSlide**: AI-generated slides (optional)

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SQLITE_DB_NAME` | SQLite database filename | `studymathai.db` |
| `PDF_DIRECTORY` | Directory for uploaded PDFs | `./uploads` |

Notes

- The segmentation step loads a sentence-transformers model (`all-MiniLM-L6-v2`) on first run, which may download weights if not cached.
- Endpoints return structured JSON with `{ "detail": "..." }` on errors.
| `SQLITE_DB_NAME` | Database file | `studymathai.db` | All features |
| `CHROMA_DIRECTORY` | Vector storage | `./chroma_index` | Chat/search |
| `EMBEDDING_MODEL_NAME` | Embedding model | `all-MiniLM-L6-v2` | Chat/search |
| `PDF_DIRECTORY` | Upload directory | `./uploads` | All features |

## Dependencies

**Core Dependencies (PDF Processing):**
- **FastAPI**: REST API framework
- **PyMuPDF**: PDF processing
- **SQLAlchemy**: Database ORM

**AI Dependencies (Optional):**
- **OpenAI**: AI slide generation
- **ChromaDB**: Vector database
- **sentence-transformers**: Text embeddings

## Command Line Usage

```bash
# Process a PDF directly
python -m studymathai.main --file "textbook.pdf"

# Index slides for search
python -m studymathai.indexer
```

## Deployment

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production

```bash
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
