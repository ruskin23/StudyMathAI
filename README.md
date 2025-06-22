# StudyMathAI

<div align="center">
  <img src="StudyMath.ai.png" alt="StudyMathAI Logo">
</div>

Transform PDF textbooks into structured, searchable content with AI-powered slides and interactive chat capabilities.

## Overview

StudyMathAI processes PDF textbooks by:
1. Extracting and structuring content using table of contents
2. Breaking chapters into digestible segments
3. Generating AI-powered study slides
4. Creating searchable vector embeddings
5. Providing a REST API for chat and content retrieval

## Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key

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

### Books

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/books/process` | Upload and process a PDF |
| GET | `/books/` | List all processed books |
| GET | `/books/{book_id}` | Get book details |
| GET | `/books/{book_id}/toc` | Get table of contents |
| GET | `/books/{book_id}/chapters` | Get all chapters |
| GET | `/books/{book_id}/segments` | Get chapter segments |
| GET | `/books/{book_id}/slides` | Get generated slides |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/query` | Send a chat message |
| GET | `/chat/history/{session_id}` | Get chat history |

## Usage Examples

### Process a PDF

```bash
curl -X POST "http://localhost:8000/books/process" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@textbook.pdf"
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

# Process PDF
with open("textbook.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/books/process",
        files={"file": f}
    )
    book_id = response.json()["book_id"]

# Chat
chat_response = requests.post(
    "http://localhost:8000/chat/query",
    json={
        "session_id": "my_session",
        "query": "Explain linear independence"
    }
)
print(chat_response.json()["response"])

# Get slides
slides = requests.get(f"http://localhost:8000/books/{book_id}/slides")
```

## Project Structure

```
studymathai/
├── api/                   # REST API
│   ├── main.py           # FastAPI app
│   └── routes/           # API endpoints
│       ├── books.py      # Book management
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

## Database Schema

- **Book**: PDF metadata and file information
- **PageText**: Raw text content per page
- **BookContent**: Chapter-level content
- **ChapterContent**: Section segments
- **GeneratedSlide**: AI-generated slides
- **TableOfContents**: Document structure

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPEN_API_KEY` | OpenAI API key | Required |
| `MODEL_NAME` | OpenAI model | `gpt-4o-mini` |
| `SQLITE_DB_NAME` | Database file | `studymathai.db` |
| `CHROMA_DIRECTORY` | Vector storage | `./chroma_index` |
| `EMBEDDING_MODEL_NAME` | Embedding model | `all-MiniLM-L6-v2` |
| `PDF_DIRECTORY` | Upload directory | `./uploads` |

## Dependencies

- **FastAPI**: REST API framework
- **OpenAI**: AI slide generation
- **ChromaDB**: Vector database
- **PyMuPDF**: PDF processing
- **SQLAlchemy**: Database ORM
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
