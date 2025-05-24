
# StudyMathAI

StudyMathAI is a Python application that processes math textbooks (in PDF format), extracts structured content using the table of contents, generates GPT-powered slide decks, and stores them in a vector database for semantic search.

This project is modular and designed for developers who want to work with structured textbook content and LLMs for study tools or AI-driven retrieval systems.

## Features

- Extracts chapters and headings from PDF textbooks
- Segments chapter content by TOC-based headings
- Generates slide decks using OpenAI's GPT API
- Stores slides in a local SQLite database
- Embeds individual slides using SentenceTransformers
- Uses ChromaDB for vector-based semantic search
- Retrieves the most relevant SlideDecks based on a question

## Tech Stack

- Python 3.12
- Poetry for dependency management
- SQLAlchemy (SQLite)
- SentenceTransformers (`all-MiniLM-L6-v2`)
- ChromaDB
- PyMuPDF (`fitz`)
- OpenAI API (GPT-4)

## Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/StudyMathAI.git
cd StudyMathAI
```

2. Install dependencies with Poetry

```bash
poetry install
```

3. Set up environment variables

Create a `.env` file in the root directory:

```
ENV=dev
OPEN_API_KEY=your-openai-key
MODEL_NAME=gpt-4
```

4. Run the processing pipeline

This will process the input PDF, extract chapters, headings, and generate slides.

```bash
poetry run python -m studymathai.main
```

5. Index the generated slides into ChromaDB

```bash
poetry run python dev_scripts/run_indexer.py
```

## Directory Structure

```
StudyMathAI/
├── studymathai/             # Source code (modules)
├── tests/                   # (Optional) unit tests
├── dev_scripts/             # Local dev scripts (ignored by git)
├── .gitignore
├── pyproject.toml
├── poetry.lock
├── README.md
```

## Excluded from Version Control

The following are ignored via `.gitignore`:

* `*.db` files (SQLite)
* ChromaDB vector store
* Notebooks, raw outputs, JSONs, text dumps
* Dev scripts and cache files

## Notes

* All slide generation is based on heading-level content (`ChapterContent`).
* SlideDecks are stored as JSON blobs and validated via Pydantic.
* Each slide is embedded separately and can be semantically searched.
* Query results return all slides associated with the matched heading.

## License

MIT License

