"""
AI Assistant modules for StudyMathAI.

This package contains AI-powered learning features:
- chatbot: Q&A chatbot for interacting with textbook content
- indexer: Vector indexing for semantic search
- retriever: Retrieval system for finding relevant content
"""

from .chatbot import ChatContextManager, Chatbot
from .indexer import SlideVectorIndexer
from .retriever import SlideRetriever

__all__ = [
    "ChatContextManager",
    "Chatbot",
    "SlideVectorIndexer",
    "SlideRetriever",
]
