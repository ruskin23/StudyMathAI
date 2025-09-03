from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from studymathai.database.models import Book


def _compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file's contents."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class BooksRepository:
    """Repository encapsulating all Book CRUD operations.

    Pattern example for other entities (chapters, segments, slides).
    """

    def __init__(self, session: Session):
        self.session = session

    # Reads
    def list(self) -> list[Book]:
        return self.session.query(Book).all()

    def ids(self) -> list[int]:
        rows = self.session.query(Book.id).distinct().all()
        return [row[0] for row in rows if row[0] is not None]

    def get(self, book_id: int) -> Book:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            raise ValueError(f"No book found with id: {book_id}")
        return book

    def get_by_filepath(self, filepath: str) -> Book:
        book_hash = _compute_file_hash(filepath)
        book = self.session.query(Book).filter_by(book_hash=book_hash).first()
        if not book:
            raise ValueError(f"No book found with file path: {filepath}")
        return book

    # Writes
    def register_from_file(self, filepath: str) -> Book:
        """Idempotently register a book based on file contents hash.

        Returns the existing book if already registered.
        """
        book_hash = _compute_file_hash(filepath)
        existing = self.session.query(Book).filter_by(book_hash=book_hash).first()
        if existing:
            return existing

        title = filepath.split("/")[-1]
        book = Book(title=title, book_hash=book_hash, file_path=filepath)
        self.session.add(book)
        self.session.flush()  # populate id
        return book

    def update_title(self, book_id: int, new_title: str) -> Book:
        if not new_title or not new_title.strip():
            raise ValueError("New title cannot be empty or None")
        book = self.get(book_id)
        book.title = new_title.strip()
        return book

    def delete(self, book_id: int) -> int | None:
        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            return None
        bid = book.id
        self.session.delete(book)
        return bid

    def delete_by_filepath(self, filepath: str) -> int | None:
        book_hash = _compute_file_hash(filepath)
        book = self.session.query(Book).filter_by(book_hash=book_hash).first()
        if not book:
            return None
        bid = book.id
        self.session.delete(book)
        return bid


# Optional functional facade for convenience
def list_books(session: Session) -> list[Book]:
    return BooksRepository(session).list()


def get_book_by_id(session: Session, book_id: int) -> Book:
    return BooksRepository(session).get(book_id)


def register_book_from_file(session: Session, filepath: str) -> Book:
    return BooksRepository(session).register_from_file(filepath)


def remove_book_by_id(session: Session, book_id: int) -> int | None:
    return BooksRepository(session).delete(book_id)
