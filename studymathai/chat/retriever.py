import chromadb
from sentence_transformers import SentenceTransformer

from studymathai.database import DatabaseConnection
from studymathai.logging_config import get_logger
from studymathai.repositories import SlidesRepository

logger = get_logger(__name__)


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
            include=["metadatas", "distances"],
        )

        if not results["metadatas"]:
            logger.info("No matches found in vector search")
            return []

        seen_content_ids = set()
        hits = []

        for meta, dist in zip(results["metadatas"][0], results["distances"][0], strict=False):
            content_id = meta["content_id"]
            if content_id in seen_content_ids:
                continue
            seen_content_ids.add(content_id)

            heading_title = meta.get("heading_title", "")
            score = 1 - dist
            hits.append({"content_id": content_id, "heading_title": heading_title, "score": score})

            if len(hits) >= top_k:
                break

        return hits

    def get_slide_deck(self, content_id: int):
        """Return a slide deck for a segment (content_id == segment_id).

        Format: {"heading": str, "slides": [{"title": str, "bullets": list[str]}]}
        """
        with self.db.get_session() as session:
            # Fetch slides and segment header
            repo_slides = SlidesRepository(session)
            slides = repo_slides.list_for_segment_id(content_id)
            # Build deck JSON-like structure
            heading_title = slides[0].segment.heading_title if slides else ""
            deck = {
                "heading": heading_title,
                "slides": [{"title": s.title, "bullets": s.bullets} for s in slides],
            }
            return deck
