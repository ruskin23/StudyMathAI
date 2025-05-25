# 📚 StudyMathAI

<div align="center">
  <img src="StudyMath.ai.png" alt="Logo">
  <p>Transform dense math textbooks into interactive, searchable slide decks powered by AI</p>
</div>

StudyMathAI is an intelligent educational tool that converts PDF textbooks into structured, study-ready presentations with semantic search capabilities. Built with OpenAI's GPT models and vector databases, it makes complex mathematical content more accessible and engaging for students. Now featuring a complete REST API for seamless integration with web applications!

## ✨ Features

- **🌐 REST API**: Complete FastAPI-powered backend for web applications and integrations
- **🤖 Interactive Chatbot**: Natural language conversation interface with automatic knowledge base integration
- **🔍 Intelligent PDF Processing**: Automatically extracts and structures content using Table of Contents
- **📖 Chapter Segmentation**: Breaks down chapters into digestible sections based on headings
- **🤖 AI-Powered Slide Generation**: Creates clean, markdown-formatted slides with proper mathematical notation
- **🔎 Semantic Search**: Find relevant content using natural language queries
- **💾 Vector Database Integration**: ChromaDB-powered similarity search across all slides
- **📊 Structured Data Storage**: SQLite database with normalized schema for efficient data management

## 🏗️ Architecture

```
PDF Input → Text Extraction → Chapter Segmentation → AI Slide Generation → Vector Indexing → REST API → Frontend/Integration
```

### Processing Pipeline

1. **PDF Ingestion**: Extract raw text and table of contents
2. **Content Structuring**: Parse chapters and create hierarchical sections
3. **AI Enhancement**: Generate study-optimized slides using GPT
4. **Vector Indexing**: Create searchable embeddings with ChromaDB
5. **API Layer**: RESTful endpoints for all functionality
6. **Query Interface**: Natural language search and chat via API

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- Poetry (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/studymathai.git
   cd studymathai
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```
   
   Or with pip:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPEN_API_KEY=your_openai_api_key_here
   MODEL_NAME=gpt-4o-mini
   SQLITE_DB_NAME=studymathai.db
   CHROMA_DIRECTORY=./chroma_index
   EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
   PDF_DIRECTORY=./uploads
   ```

## 🌐 API Usage

### Starting the API Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### API Endpoints

#### 📚 Book Management

- **Upload & Process PDF**: `POST /books/process`
  ```bash
  curl -X POST "http://localhost:8000/books/process" \
       -H "Content-Type: multipart/form-data" \
       -F "file=@textbook.pdf"
  ```

- **List Books**: `GET /books/`
- **Get Book Details**: `GET /books/{book_id}`
- **Get Table of Contents**: `GET /books/{book_id}/toc`
- **Get Chapters**: `GET /books/{book_id}/chapters`
- **Get Segments**: `GET /books/{book_id}/segments`
- **Get Generated Slides**: `GET /books/{book_id}/slides`

#### 💬 Chat Interface

- **Chat Query**: `POST /chat/query`
  ```bash
  curl -X POST "http://localhost:8000/chat/query" \
       -H "Content-Type: application/json" \
       -d '{
         "session_id": "user123",
         "query": "What are vector spaces and how do they work?"
       }'
  ```

- **Get Chat History**: `GET /chat/history/{session_id}`

#### 🔍 Search

- **Search Slides**: `POST /search/query` (when implemented)

#### ⚙️ Pipeline

- **Index Slides**: `POST /pipeline/index` (when implemented)

### Example API Integration

```python
import requests

# Upload and process a PDF
with open("textbook.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/books/process",
        files={"file": f}
    )
    result = response.json()
    book_id = result["book_id"]

# Chat with the processed content
chat_response = requests.post(
    "http://localhost:8000/chat/query",
    json={
        "session_id": "my_session",
        "query": "Explain linear independence with examples"
    }
)
print(chat_response.json()["response"])

# Get all slides for the book
slides = requests.get(f"http://localhost:8000/books/{book_id}/slides")
print(slides.json())
```

## 🖥️ Command Line Usage

You can still use StudyMathAI via command line for direct processing:

#### 1. Process a Textbook

```bash
python -m studymathai.main --file "textbook.pdf" --data_dir "/path/to/pdf/directory"
```

#### 2. Index Slides for Search

```bash
python -m studymathai.indexer
```

#### 3. Interactive Chat Interface (CLI)

```python
from studymathai.chatbot import ChatBot

# Initialize the chatbot
bot = ChatBot()

# Ask questions naturally
response = bot.get_response("What are vector spaces and how do they work?")
print(response)
```

## 📁 Project Structure

```
studymathai/
├── api/                   # FastAPI REST API layer
│   ├── __init__.py
│   ├── main.py           # FastAPI application setup
│   └── routes/           # API route handlers
│       ├── books.py      # Book management endpoints
│       ├── chat.py       # Chat interface endpoints
│       ├── search.py     # Search endpoints
│       └── pipeline.py   # Processing pipeline endpoints
├── studymathai/          # Core library
│   ├── __init__.py
│   ├── chatbot.py        # Interactive AI tutoring chatbot
│   ├── db.py             # Database operations and models
│   ├── generator.py      # AI slide generation with OpenAI
│   ├── indexer.py        # Vector indexing with ChromaDB
│   ├── main.py           # CLI processing pipeline
│   ├── models.py         # SQLAlchemy ORM models
│   ├── processor.py      # PDF processing and content extraction
│   ├── retriever.py      # Semantic search interface
│   └── utils.py          # Text cleaning utilities
```

## 🗄️ Database Schema

The application uses a normalized SQLite schema:

- **`Book`**: Stores PDF metadata and file information
- **`PageText`**: Raw text content for each PDF page
- **`BookContent`**: Chapter-level content and page ranges
- **`ChapterContent`**: Section-level segments with headings
- **`GeneratedSlide`**: AI-generated slide decks in JSON format
- **`TableOfContents`**: Hierarchical TOC structure

## 💬 Interactive Features

### API-Powered Chatbot

The REST API provides a scalable chat interface that maintains session-based conversations:

```json
{
  "session_id": "user123",
  "query": "How do I prove linear independence?"
}
```

**Response:**
```json
{
  "response": "To prove linear independence, you need to show that the only solution to c₁v₁ + c₂v₂ + ... + cₙvₙ = 0 is when all coefficients c₁, c₂, ..., cₙ are zero...",
  "retrieved_slides": [
    {
      "segment_id": 15,
      "heading": "Linear Independence",
      "slides": [...]
    }
  ]
}
```

### Features

- **🔍 Automatic Knowledge Base Search**: Uses function calling to query relevant slides
- **💾 Session-Based History**: Maintains separate chat histories per session
- **🎯 Context-Aware Responses**: Integrates textbook content into conversational answers
- **🛠️ Tool Integration**: Seamlessly combines search results with GPT responses
- **🌐 Scalable API**: Handle multiple concurrent users and sessions

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPEN_API_KEY` | OpenAI API key | Required |
| `MODEL_NAME` | OpenAI model to use | `gpt-4o-mini` |
| `SQLITE_DB_NAME` | SQLite database file | `studymathai.db` |
| `CHROMA_DIRECTORY` | ChromaDB storage path | `./chroma_index` |
| `EMBEDDING_MODEL_NAME` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `PDF_DIRECTORY` | Upload directory for PDFs | `./uploads` |

### API Configuration

The FastAPI server includes:
- **CORS middleware** for cross-origin requests
- **Automatic documentation** at `/docs` and `/redoc`
- **Health check endpoint** at `/health`
- **File upload handling** with configurable storage directory

## 📊 Dependencies

### Core Dependencies
- **FastAPI** (≥0.68.0): Modern REST API framework
- **uvicorn** (≥0.15.0): ASGI server for FastAPI
- **OpenAI** (≥1.82.0): GPT-powered slide generation
- **ChromaDB** (≥1.0.10): Vector database for semantic search
- **PyMuPDF** (≥1.26.0): PDF text extraction
- **SQLAlchemy** (≥2.0.41): Database ORM
- **sentence-transformers** (≥4.1.0): Text embeddings

### Development Dependencies
- **Jupyter**: Interactive development and testing
- **pypdf2**: Additional PDF processing utilities

## 🎯 Use Cases

### For Developers
- **Web Applications**: Integrate StudyMathAI into learning management systems
- **Mobile Apps**: Use the REST API for mobile study applications
- **Microservices**: Deploy as a containerized service in larger architectures
- **Batch Processing**: Process multiple textbooks via API automation

### For End Users
- **Students**: Convert dense textbooks into digestible study materials and get instant answers
- **Educators**: Create structured presentations from academic content and provide AI tutoring
- **Researchers**: Quickly search and reference specific concepts across large texts
- **Self-learners**: Transform complex mathematical texts into accessible formats

## 🐳 Deployment

### Docker Deployment (Recommended)

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Deployment

```bash
# Using Gunicorn for production
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔮 Roadmap

- [x] REST API with FastAPI
- [x] Session-based chat interface
- [x] File upload and processing endpoints
- [ ] Enhanced search endpoints with filtering
- [ ] Batch processing endpoints
- [ ] WebSocket support for real-time chat
- [ ] Authentication and user management
- [ ] Rate limiting and API quotas
- [ ] Docker containerization
- [ ] Web interface with live markdown rendering
- [ ] Cross-reference detection between sections
- [ ] Export capabilities (PDF, PowerPoint, etc.)

## 🤝 Contributing

Contributions are welcome! Whether you're interested in the core processing pipeline or the API layer, there are many ways to contribute.

### Areas for Contribution
- API endpoint enhancements
- Frontend integrations
- Database optimizations
- Additional file format support
- Performance improvements

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing powerful language models
- FastAPI team for the excellent web framework
- ChromaDB team for the excellent vector database
- The sentence-transformers community for embedding models
- PyMuPDF developers for PDF processing capabilities

---

**Built with ❤️ by [Ruskin Patel](mailto:ruskin.patel23@gmail.com)**

*StudyMathAI - Making mathematics education more accessible, one API call at a time.*
