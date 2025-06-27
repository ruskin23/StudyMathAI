from sqlalchemy.orm import Session
from .models import ProcessingStatus
from .db import DatabaseConnection


class ProcessingStatusManager:
    """Utility class to manage ProcessingStatus flags for books."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def ensure_processing_status(self, book_id: int):
        """
        Ensure a ProcessingStatus record exists for the given book_id.
        Creates one with all flags False if it doesn't exist.
        """
        with self.db.get_session() as session:
            status = session.query(ProcessingStatus).filter_by(book_id=book_id).first()
            
            if not status:
                status = ProcessingStatus(
                    book_id=book_id,
                    content_extracted=False,
                    pages_extracted=False,
                    chapters_segmented=False,
                    slides_generated=False,
                    slides_indexed=False
                )
                session.add(status)
    
    def update_status_flag(self, book_id: int, flag_name: str, value: bool = True):
        """
        Update a specific flag in the ProcessingStatus for the given book_id.
        
        Args:
            book_id: The book ID
            flag_name: Name of the flag to update ('content_extracted', 'pages_extracted', etc.)
            value: Value to set (default True)
        """
        with self.db.get_session() as session:
            status = session.query(ProcessingStatus).filter_by(book_id=book_id).first()
            
            if not status:
                # Create status if it doesn't exist
                status = ProcessingStatus(book_id=book_id)
                session.add(status)
                session.flush()  # To get the ID
            
            # Set the flag
            if hasattr(status, flag_name):
                setattr(status, flag_name, value)
                session.commit()
            else:
                raise ValueError(f"Invalid flag name: {flag_name}")
    
    def set_pages_extracted(self, book_id: int):
        """Set pages_extracted flag to True for the given book."""
        self.update_status_flag(book_id, 'pages_extracted', True)
    
    def set_content_extracted(self, book_id: int):
        """Set content_extracted flag to True for the given book."""
        self.update_status_flag(book_id, 'content_extracted', True)
    
    def set_chapters_segmented(self, book_id: int):
        """Set chapters_segmented flag to True for the given book."""
        self.update_status_flag(book_id, 'chapters_segmented', True)
    
    def set_slides_generated(self, book_id: int):
        """Set slides_generated flag to True for the given book."""
        self.update_status_flag(book_id, 'slides_generated', True)
    
    def set_slides_indexed(self, book_id: int):
        """Set slides_indexed flag to True for the given book."""
        self.update_status_flag(book_id, 'slides_indexed', True)
    
    def get_processing_status(self, book_id: int) -> dict:
        """Get the current processing status for a book as a dictionary."""
        self.ensure_processing_status(book_id)
        
        with self.db.get_session() as session:
            status = session.query(ProcessingStatus).filter_by(book_id=book_id).first()
            
            if not status:
                # This should not happen after ensure_processing_status, but just in case
                return {
                    'book_id': book_id,
                    'content_extracted': False,
                    'pages_extracted': False,
                    'chapters_segmented': False,
                    'slides_generated': False,
                    'slides_indexed': False,
                    'created_at': None,
                    'updated_at': None
                }
            
            # Access all attributes while session is active and return as dict
            return {
                'book_id': status.book_id,
                'content_extracted': status.content_extracted,
                'pages_extracted': status.pages_extracted,
                'chapters_segmented': status.chapters_segmented,
                'slides_generated': status.slides_generated,
                'slides_indexed': status.slides_indexed,
                'created_at': status.created_at,
                'updated_at': status.updated_at
            } 