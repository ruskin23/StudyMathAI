# vector_indexer.py

import os
import json
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

from studymathai.db import DatabaseConnection
from studymathai.models import GeneratedSlide, ChapterContent

import os
from dotenv import load_dotenv

load_dotenv()

class SlideVectorIndexer:
    def __init__(self, db: DatabaseConnection, persist_dir: str = "./chroma_index"):
        self.db = db
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=persist_dir)

        try:
            self.collection = self.client.get_collection(name="slides")
        except ValueError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(name="slides")
            print("📚 Created new collection: slides")

    def index_all_slides(self, book_id: int = None):
        """
        1. Grab all heading-slides combination for a particular book id. Call it slide_decks
        2. for each slide deck, get the content (segment) id to get the heading details.
        """
        
        with self.db.get_session() as session:
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

                if not slides:
                    print(f"⚠️  No slides found for content_id {content_id}")
                    continue

                slide_texts = []
                slide_ids = []
                slide_metas = []

                for i, slide in enumerate(slides):
                    title = slide.get("title", "")
                    bullets = slide.get("bullets", [])
                    slide_text = f"{title}\n" + "\n".join(bullets)
                    slide_texts.append(slide_text)
                    slide_ids.append(f"{content_id}_slide_{i}")
                    slide_metas.append({
                        "content_id": content_id,
                        "slide_index": i,
                        "heading_title": heading_title,
                        "slide_title": title
                    })

                try:
                    # Generate embeddings
                    embeddings = self.embedding_model.encode(slide_texts)
                    
                    # Add to collection
                    self.collection.add(
                        embeddings=embeddings.tolist(),
                        documents=slide_texts,
                        metadatas=slide_metas,
                        ids=slide_ids
                    )
                    print(f"✅ Indexed {len(slides)} slides for content_id {content_id}")
                except Exception as e:
                    print(f"❌ Failed to index content_id {content_id}: {e}")

        print("✅ Indexing complete!")