"""Knowledge base service for indexing and retrieval."""

from .indexer import SlideVectorIndexer
from .retriever import SlideRetriever

__all__ = [
    "SlideVectorIndexer",
    "SlideRetriever",
]
