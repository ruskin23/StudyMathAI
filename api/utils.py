from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from studymathai.database import DatabaseConnection


def get_db_connection(request: Request) -> DatabaseConnection:
    return request.app.state.db_connection


def get_db_session(
    db: DatabaseConnection = Depends(get_db_connection),  # noqa: B008
) -> Generator[Session, None, None]:
    with db.get_session() as session:
        yield session
