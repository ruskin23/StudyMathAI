# vector_indexer.py

import json
import chromadb
from sentence_transformers import SentenceTransformer
from studymathai.db import DatabaseManager
from studymathai.models import GeneratedSlide, ChapterContent


class SlideVectorIndexer:
    def __init__(self, db: DatabaseManager, persist_dir: str = "./chroma_index"):
        self.db = db
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name="slides")

    def flatten_slide(self, slide):
        return f"{slide['title']}. " + " ".join(slide["bullets"])

    def index_all_slides(self, book_id: int = None):
        session = self.db.Session()
        query = session.query(GeneratedSlide)

        if book_id is not None:
            query = query.filter(GeneratedSlide.book_id == book_id)

        slide_decks = query.all()
        print(f"📚 Found {len(slide_decks)} slide decks to index")

        for deck in slide_decks:
            content_id = deck.content_id
            try:
                chapter = session.query(ChapterContent).get(content_id)
                deck_data = json.loads(deck.slides_json)
                slides = deck_data.get("slides", [])
                heading_title = deck_data.get("heading", chapter.heading_title if chapter else "Unknown")
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
                            "chapter_id": chapter.chapter_id if chapter else None,
                            "book_id": deck.book_id
                        }]
                    )
                except Exception as e:
                    print(f"❌ Error indexing slide {content_id}_{i}: {e}")

        print("✅ Vector index complete.")
