# retriever.py

import chromadb
from sentence_transformers import SentenceTransformer
from studymathai.db import DatabaseConnection
from studymathai.models import GeneratedSlide
import json


class SlideRetriever:
    def __init__(self, db: DatabaseConnection, persist_dir: str = "./chroma_index"):
        self.db = db
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_collection(name="slides")

    def query(self, question: str, top_k: int = 3):
        query_embedding = self.embedding_model.encode(question)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 3,  # Fetch more to allow filtering by content_id
            include=["metadatas", "distances"]
        )

        if not results["metadatas"]:
            print("❌ No matches found.")
            return []

        seen_content_ids = set()
        hits = []

        for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
            content_id = meta["content_id"]
            if content_id in seen_content_ids:
                continue
            seen_content_ids.add(content_id)

            heading_title = meta.get("heading_title", "")
            score = 1 - dist
            hits.append({
                "content_id": content_id,
                "heading_title": heading_title,
                "score": score
            })

            if len(hits) >= top_k:
                break

        return hits

    def get_slide_deck(self, content_id: int):
        with self.db.get_session() as session:
            deck = session.query(GeneratedSlide).filter_by(content_id=content_id).first()
            
        if not deck:
            return None

        try:
            return json.loads(deck.slides_json)
        except Exception as e:
            print(f"❌ Failed to parse slides for content_id {content_id}: {e}")
            return None
