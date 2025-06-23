# StudyMathAI API Structure

This document describes the restructured API design for better organization and maintainability.

## Overview

The API has been reorganized into four main modules:

1. **Books** (`/books`) - Book management and file upload
2. **Processing** (`/processing`) - Step-by-step processing pipeline
3. **Content** (`/content`) - Content retrieval and querying
4. **Chat** (`/chat`) - Chat functionality (existing)

## API Endpoints

### Books Module (`/books`)
Handles book management and file uploads.

#### `POST /books/upload`
Upload and register a new PDF book.
- **Input**: PDF file via multipart form data
- **Output**: Book metadata with ID and file path
- **Purpose**: Register a book for processing

#### `GET /books/`
List all books in the system.
- **Output**: Array of book metadata

#### `GET /books/{book_id}`
Get detailed information about a specific book.
- **Output**: Book details including creation timestamp

#### `PUT /books/{book_id}`
Update book metadata (e.g., title).
- **Input**: Updated metadata
- **Output**: Updated book details

#### `DELETE /books/{book_id}`
Delete a book and all associated data.
- **Output**: Confirmation message

### Processing Module (`/processing`)
Handles the step-by-step processing pipeline.

#### `POST /processing/extract-pages/{book_id}`
Extract page-level text from a book.
- **Input**: Book ID
- **Output**: Number of pages extracted
- **Prerequisites**: Book must be uploaded

#### `POST /processing/extract-content/{book_id}`
Extract chapters and table of contents.
- **Input**: Book ID
- **Output**: Number of chapters and TOC entries extracted
- **Prerequisites**: Pages must be extracted

#### `POST /processing/segment-chapters/{book_id}`
Segment chapters into heading-text blocks.
- **Input**: Book ID
- **Output**: Number of segments created
- **Prerequisites**: Content must be extracted

#### `POST /processing/generate-slides/{book_id}`
Generate slides for all segments in a book.
- **Input**: Book ID
- **Output**: Number of slides generated
- **Prerequisites**: Chapters must be segmented

#### `POST /processing/process-complete/{book_id}`
Run the complete processing pipeline in sequence.
- **Input**: Book ID
- **Output**: Completion status
- **Purpose**: Legacy endpoint for full pipeline processing

### Content Module (`/content`)
Handles content retrieval and querying.

#### `GET /content/{book_id}/toc`
Get table of contents for a book.
- **Output**: Array of TOC entries with page numbers and hierarchy

#### `GET /content/{book_id}/chapters`
Get chapters for a book.
- **Output**: Array of chapter information with page ranges

#### `GET /content/{book_id}/segments`
Get all segments for a book.
- **Output**: Array of segment information with content text

#### `GET /content/{book_id}/slides`
Get all slide decks for a book.
- **Output**: Array of slide decks with titles and bullet points

#### `GET /content/{book_id}/segments/{segment_id}`
Get detailed information about a specific segment.
- **Output**: Segment details including full content text

#### `GET /content/{book_id}/segments/{segment_id}/slides`
Get slides for a specific segment.
- **Output**: Slide deck for the specified segment

## Processing Workflow

The typical workflow for processing a book:

1. **Upload**: `POST /books/upload` - Upload PDF file
2. **Extract Pages**: `POST /processing/extract-pages/{book_id}` - Extract page text
3. **Extract Content**: `POST /processing/extract-content/{book_id}` - Extract chapters and TOC
4. **Segment Chapters**: `POST /processing/segment-chapters/{book_id}` - Create segments
5. **Generate Slides**: `POST /processing/generate-slides/{book_id}` - Create slide presentations

## Benefits of This Structure

### Modularity
- Each module has a clear responsibility
- Processing steps can be run independently
- Easy to test and debug individual components

### Scalability
- New processing steps can be added easily
- Content retrieval is separated from processing
- Better separation of concerns

### Maintainability
- Code is organized by functionality
- Easier to locate and modify specific features
- Clear API boundaries

### Flexibility
- Users can run partial processing pipelines
- Individual steps can be re-run if needed
- Better error handling and recovery

## Error Handling

Each endpoint includes proper error handling:
- **404**: Resource not found (book, segment, etc.)
- **400**: Invalid input or missing prerequisites
- **500**: Processing errors with detailed messages

## Response Models

All endpoints use structured response models with:
- Clear field names and types
- Consistent error message format
- Appropriate HTTP status codes 