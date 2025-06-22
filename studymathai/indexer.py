# vector_indexer.py

import json
import chromadb
from sentence_transformers import SentenceTransformer
from studymathai.db import DatabaseManager
from studymathai.models import GeneratedSlide, ChapterContent

import os
from dotenv import load_dotenv

load_dotenv()

class SlideVectorIndexer:
    def __init__(self, db: DatabaseManager):
        self.db = db

        chroma_dir = os.getenv("CHROMA_DIRECTORY", "./chroma_index")
        embedding_model = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

        self.embedding_model = SentenceTransformer(embedding_model)
        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.client.get_or_create_collection(name="slides")

    def flatten_slide(self, slide):
        return f"{slide['title']}. " + " ".join(slide["bullets"])

    def index_all_slides(self, book_id: int = None):
        """
        1. Grab all heading-slides combination for a particular book id. Call it slide_decks
        2. for each slide deck, get the content (segment) id to get the heading details.
        """
        
        with self.db.connection.get_session() as session:
            query = session.query(GeneratedSlide)

            if book_id is not None:
                query = query.filter(GeneratedSlide.book_id == book_id)

            slide_decks = query.all()
            print(f"📚 Found {len(slide_decks)} slide decks to index")

            for deck in slide_decks:
                content_id = deck.content_id
                try:
                    # content_id refers to ChapterContent.id (primary key)
                    heading = session.query(ChapterContent).filter_by(id=content_id).first()
                    deck_data = json.loads(deck.slides_json)
                    slides = deck_data.get("slides", [])
                    heading_title = deck_data.get("heading", heading.heading_title if heading else "Unknown")
                except Exception as e:
                    print(f"⚠️  Skipping content_id {content_id}: {e}")
                    continue

                for i, slide in enumerate(slides):
                    try:
                        flat_text = self.flatten_slide(slide)
                        embedding = self.embedding_model.encode(flat_text)

                        self.collection.add(
                            documents=[flat_text],
                            embeddings=[embedding],
                            ids=[f"{content_id}_{i}"],
                            metadatas=[{
                                "slide_index": i,
                                "content_id": content_id,
                                "heading_title": heading_title,
                                "chapter_id": heading.chapter_id if heading else None,
                                "book_id": deck.book_id
                            }]
                        )
                    except Exception as e:
                        print(f"❌ Error indexing slide {content_id}_{i}: {e}")

        print("✅ Vector index complete.")