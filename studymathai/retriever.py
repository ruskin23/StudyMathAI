# retriever.py

import chromadb
from sentence_transformers import SentenceTransformer
from studymathai.db import DatabaseManager
from studymathai.models import GeneratedSlide
import json


class SlideRetriever:
    def __init__(self, db: DatabaseManager, persist_dir: str = "./chroma_index"):
        self.db = db
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_collection(name="slides")

    def query(self, question: str, top_k: int = 3):
        # Embed the query
        query_embedding = self.embedding_model.encode(question)

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "distances"]
        )

        if not results["metadatas"]:
            print("❌ No matches found.")
            return []

        hits = []
        for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
            content_id = meta["content_id"]
            heading_title = meta.get("heading_title", "")
            score = 1 - dist  # Higher is better
            hits.append((content_id, heading_title, score))

        return hits

    def get_slide_deck(self, content_id: int):
        deck = self.db.get_slides_for_segment(content_id)
        if not deck:
            return None

        try:
            return json.loads(deck.slides_json)
        except Exception as e:
            print(f"❌ Failed to parse slides for content_id {content_id}: {e}")
            return None
