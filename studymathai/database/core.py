import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from studymathai.database.models import Base


class DatabaseConnection:
    def __init__(self, db_name: str = None):
        self.db_name = db_name or os.getenv("SQLITE_DB_NAME", "studymathai.db")

        if self.db_name == ":memory:":
            self.engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(
                f"sqlite:///{self.db_name}", connect_args={"check_same_thread": False}
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
