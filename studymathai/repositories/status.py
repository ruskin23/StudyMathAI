from __future__ import annotations

from sqlalchemy.orm import Session

from studymathai.database.models import ProcessingStatus


class ProcessingStatusRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_for_book(self, book_id: int) -> ProcessingStatus | None:
        return self.session.query(ProcessingStatus).filter_by(book_id=book_id).first()

    def ensure_for_book(self, book_id: int) -> ProcessingStatus:
        status = self.get_for_book(book_id)
        if status:
            return status
        status = ProcessingStatus(book_id=book_id)
        self.session.add(status)
        self.session.flush()
        return status
