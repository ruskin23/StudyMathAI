# StudyMathAI

<div align="center">
  <img src="StudyMath.ai.png" alt="StudyMathAI Logo">
</div>

Transform PDF textbooks into structured, searchable content with AI-powered slides and interactive chat capabilities.

## Overview

StudyMathAI processes PDF textbooks by:
1. **PDF Processing**: Extracting text, structure, and creating heading-text segments
2. **AI Enhancement**: Generating study slides and embeddings (optional)
3. **Interactive Features**: Chat interface with context-aware responses
4. **REST API**: Complete API for content management and retrieval

**Key Architecture**: PDF processing is completely independent from AI functionality, allowing you to process books without AI dependencies.

## Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key (only needed for AI features)

### Installation

```bash
git clone https://github.com/yourusername/studymathai.git
cd studymathai
pip install -e .
```

### Environment Setup

Create a `.env` file:
```env
OPEN_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini
SQLITE_DB_NAME=studymathai.db
CHROMA_DIRECTORY=./chroma_index
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
PDF_DIRECTORY=./uploads
```

### Start the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation: `http://localhost:8000/docs`

## API Endpoints

### 📚 Book Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/books/upload` | Upload a PDF book |
| GET | `/books/` | List all books |
| GET | `/books/{book_id}` | Get book details |
| PUT | `/books/{book_id}` | Update book metadata |
| DELETE | `/books/{book_id}` | Delete book and data |

### 🔄 PDF Processing (No AI Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/processing/extract-pages/{book_id}` | Extract page-level text |
| POST | `/processing/extract-content/{book_id}` | Extract chapters and TOC |
| POST | `/processing/segment-chapters/{book_id}` | Create heading-text segments |
| POST | `/processing/process-complete/{book_id}` | Run complete PDF pipeline |

### 📖 Content Retrieval

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/content/{book_id}/toc` | Get table of contents |
| GET | `/content/{book_id}/chapters` | Get all chapters |
| GET | `/content/{book_id}/segments` | Get heading-text segments |
| GET | `/content/{book_id}/segments/{segment_id}` | Get specific segment |

### 🤖 AI Slide Generation (Requires OpenAI API)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/slides/generate/{book_id}` | Generate AI slides for book |
| GET | `/slides/{book_id}/all` | Get all generated slides |
| GET | `/slides/{book_id}/segment/{segment_id}` | Get slides for specific segment |

### 💬 Chat Interface

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/query` | Send a chat message |
| GET | `/chat/history/{session_id}` | Get chat history |

## Usage Examples

### Basic PDF Processing (No AI)

```bash
# 1. Upload PDF
curl -X POST "http://localhost:8000/books/upload" \
     -F "file=@textbook.pdf"

# 2. Process PDF (extract text, chapters, segments)
curl -X POST "http://localhost:8000/processing/process-complete/1"

# 3. Get heading-text segments
curl -X GET "http://localhost:8000/content/1/segments"
```

### Full Pipeline with AI Features

```bash
# 1-3. Same as above...

# 4. Generate AI slides
curl -X POST "http://localhost:8000/slides/generate/1"

# 5. Get generated slides
curl -X GET "http://localhost:8000/slides/1/all"
```

### Chat with Content

```bash
curl -X POST "http://localhost:8000/chat/query" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "user123",
       "query": "What are vector spaces?"
     }'
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

# Process PDF content
requests.post(f"http://localhost:8000/processing/process-complete/{book_id}")

# Get heading-text segments
segments = requests.get(f"http://localhost:8000/content/{book_id}/segments")
print(f"Found {len(segments.json())} segments")

# Optional: Generate AI slides
requests.post(f"http://localhost:8000/slides/generate/{book_id}")
slides = requests.get(f"http://localhost:8000/slides/{book_id}/all")

# Chat with content
chat_response = requests.post(
    "http://localhost:8000/chat/query",
    json={
        "session_id": "my_session",
        "query": "Explain linear independence"
    }
)
print(chat_response.json()["response"])
```

## Project Structure

```
studymathai/
├── api/                   # REST API
│   ├── main.py           # FastAPI app
│   └── routes/           # API endpoints
│       ├── books.py      # Book management
│       ├── content.py    # Content retrieval
│       ├── processing.py # PDF processing pipeline
│       ├── slides.py     # AI slide generation
│       └── chat.py       # Chat interface
├── studymathai/          # Core library
│   ├── chatbot.py        # AI chatbot
│   ├── db.py             # Database operations
│   ├── generator.py      # Slide generation
│   ├── indexer.py        # Vector indexing
│   ├── models.py         # Database models
│   ├── processor.py      # PDF processing
│   └── retriever.py      # Search functionality
```

## Processing Workflow

### PDF-Only Workflow (No AI dependencies)
```
Upload PDF → Extract Pages → Extract Content → Segment Chapters → Retrieve Segments
```

### Full AI-Enhanced Workflow
```
PDF Processing → Generate Slides → Chat Interface
```

## Database Schema

- **Book**: PDF metadata and file information
- **PageText**: Raw text content per page
- **BookContent**: Chapter-level content
- **ChapterContent**: Section segments with heading-text pairs
- **TableOfContents**: Document structure
- **GeneratedSlide**: AI-generated slides (optional)

## Configuration

| Variable | Description | Default | Required For |
|----------|-------------|---------|--------------|
| `OPEN_API_KEY` | OpenAI API key | - | AI features only |
| `MODEL_NAME` | OpenAI model | `gpt-4o-mini` | AI features only |
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
