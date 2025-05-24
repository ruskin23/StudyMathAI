# 📚 StudyMathAI

<div align="center">
  <img src="StudyMath.ai.png" alt="Logo">
  <p>Transform dense math textbooks into interactive, searchable slide decks powered by AI</p>
</div>

StudyMathAI is an intelligent educational tool that converts PDF textbooks into structured, study-ready presentations with semantic search capabilities. Built with OpenAI's GPT models and vector databases, it makes complex mathematical content more accessible and engaging for students.

## ✨ Features

- **🤖 Interactive Chatbot**: Natural language conversation interface with automatic knowledge base integration
- **🔍 Intelligent PDF Processing**: Automatically extracts and structures content using Table of Contents
- **📖 Chapter Segmentation**: Breaks down chapters into digestible sections based on headings
- **🤖 AI-Powered Slide Generation**: Creates clean, markdown-formatted slides with proper mathematical notation
- **🔎 Semantic Search**: Find relevant content using natural language queries
- **💾 Vector Database Integration**: ChromaDB-powered similarity search across all slides
- **📊 Structured Data Storage**: SQLite database with normalized schema for efficient data management

## 🏗️ Architecture

```
PDF Input → Text Extraction → Chapter Segmentation → AI Slide Generation → Vector Indexing → Semantic Search
```

### Processing Pipeline

1. **PDF Ingestion**: Extract raw text and table of contents
2. **Content Structuring**: Parse chapters and create hierarchical sections
3. **AI Enhancement**: Generate study-optimized slides using GPT
4. **Vector Indexing**: Create searchable embeddings with ChromaDB
5. **Query Interface**: Natural language search across all content

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
   ```

### Usage

#### 1. Process a Textbook

```bash
python -m studymathai.main --file "textbook.pdf" --data_dir "/path/to/pdf/directory"
```

This command will:
- Extract text from the PDF
- Parse the table of contents
- Segment chapters into sections
- Generate AI-powered slides for each section

#### 2. Index Slides for Search

```bash
python -m studymathai.indexer
```

Creates vector embeddings and populates the ChromaDB collection for semantic search.

#### 3. Interactive Chat Interface

Use the AI-powered chatbot to ask questions about your textbook content:

```python
from studymathai.chatbot import ChatBot

# Initialize the chatbot
bot = ChatBot()

# Ask questions naturally
response = bot.get_response("What are vector spaces and how do they work?")
print(response)

# The chatbot automatically searches your knowledge base
response = bot.get_response("Explain linear independence with examples")
print(response)
```

#### 4. Direct Search (Advanced)

For programmatic access to the search functionality:

```python
from studymathai.db import DatabaseManager
from studymathai.retriever import SlideRetriever

db = DatabaseManager()
retriever = SlideRetriever(db)

# Search for relevant content
results = retriever.query("What are vector spaces?", top_k=3)

for result in results:
    slides = retriever.get_slide_deck(result["content_id"])
    print(f"📝 {result['heading_title']} (Score: {result['score']:.3f})")
```

## 📁 Project Structure

```
studymathai/
├── __init__.py
├── chatbot.py        # Interactive AI tutoring chatbot
├── db.py              # Database operations and models
├── generator.py       # AI slide generation with OpenAI
├── indexer.py         # Vector indexing with ChromaDB
├── main.py           # Main processing pipeline
├── models.py         # SQLAlchemy ORM models
├── processor.py      # PDF processing and content extraction
├── retriever.py      # Semantic search interface
└── utils.py          # Text cleaning utilities
```

## 🗄️ Database Schema

The application uses a normalized SQLite schema:

- **`Book`**: Stores PDF metadata and file information
- **`PageText`**: Raw text content for each PDF page
- **`BookContent`**: Chapter-level content and page ranges
- **`ChapterContent`**: Section-level segments with headings
- **`GeneratedSlide`**: AI-generated slide decks in JSON format
- **`TableOfContents`**: Hierarchical TOC structure

## 💬 Interactive Chatbot

The built-in AI chatbot provides a natural conversation interface for studying your textbook content. It automatically searches your knowledge base and provides contextual answers.

### Features

- **🔍 Automatic Knowledge Base Search**: Uses function calling to query relevant slides
- **💾 Conversation History**: Maintains chat history in `chat_history.json`
- **🎯 Context-Aware Responses**: Integrates textbook content into conversational answers
- **🛠️ Tool Integration**: Seamlessly combines search results with GPT responses

### Example Conversation

```python
from studymathai.chatbot import ChatBot

bot = ChatBot()

# Natural language questions
print(bot.get_response("What is a vector space?"))
print(bot.get_response("Can you give me examples of linear transformations?"))
print(bot.get_response("How do I prove linear independence?"))
```

The chatbot will automatically:
1. Analyze your question
2. Search the vector database for relevant slides
3. Combine multiple sources if needed
4. Provide a comprehensive, contextual answer

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPEN_API_KEY` | OpenAI API key | Required |
| `MODEL_NAME` | OpenAI model to use | `gpt-4o-mini` |
| `SQLITE_DB_NAME` | SQLite database file | `studymathai.db` |
| `CHROMA_DIRECTORY` | ChromaDB storage path | `./chroma_index` |
| `EMBEDDING_MODEL_NAME` | Sentence transformer model | `all-MiniLM-L6-v2` |

### Slide Generation

The AI generates slides with:
- Proper markdown formatting
- Mathematical expressions in LaTeX (`$...$` for inline, `$$...$$` for blocks)
- Structured bullet points
- Clear, concise explanations
- Self-contained study materials

## 📊 Dependencies

### Core Dependencies
- **OpenAI** (≥1.82.0): GPT-powered slide generation
- **ChromaDB** (≥1.0.10): Vector database for semantic search
- **PyMuPDF** (≥1.26.0): PDF text extraction
- **SQLAlchemy** (≥2.0.41): Database ORM
- **sentence-transformers** (≥4.1.0): Text embeddings

### Development Dependencies
- **Jupyter**: Interactive development and testing
- **pypdf2**: Additional PDF processing utilities

## 🎯 Use Cases

- **Students**: Convert dense textbooks into digestible study materials and get instant answers to questions
- **Educators**: Create structured presentations from academic content and provide AI tutoring support
- **Researchers**: Quickly search and reference specific concepts across large texts
- **Self-learners**: Transform complex mathematical texts into accessible formats

## 🔮 Roadmap

- [ ] Enhanced chatbot with math problem solving
- [ ] Web interface with live markdown rendering
- [ ] Quiz generation from slide content
- [ ] Cross-reference detection between sections
- [ ] Export capabilities (PDF, PowerPoint, etc.)
- [ ] Multi-language support
- [ ] Integration with popular learning management systems

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing powerful language models
- ChromaDB team for the excellent vector database
- The sentence-transformers community for embedding models
- PyMuPDF developers for PDF processing capabilities

---

**Built with ❤️ by [Ruskin Patel](mailto:ruskin.patel23@gmail.com)**

*StudyMathAI - Making mathematics education more accessible, one slide at a time.*
