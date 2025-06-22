import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from studymathai.models import Base, Book, BookContent, ChapterContent, GeneratedSlide, TableOfContents, PageText
import json
from typing import List, Optional
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self, db_name: str = None):
        self.db_name = db_name or os.getenv("SQLITE_DB_NAME", "studymathai.db")
        self.engine = create_engine(
            f"sqlite:///{self.db_name}",
            connect_args={"check_same_thread": False},
            pool_size=10,
            max_overflow=20,
            pool_timeout=30
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()