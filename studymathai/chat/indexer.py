import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from studymathai.database import DatabaseConnection
from studymathai.logging_config import get_logger
from studymathai.repositories import SegmentsRepository

load_dotenv()
logger = get_logger(__name__)


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
            logger.info("Created new collection: slides")

    def index_all_slides(self, book_id: int = None):
        """
        1. Grab all heading-slides combination for a particular book id. Call it slide_decks
        2. for each slide deck, get the content (segment) id to get the heading details.
        """

        with self.db.get_session() as session:
            seg_repo = SegmentsRepository(session)
            segments = (
                seg_repo.list_for_book(book_id) if book_id is not None else seg_repo.list_all()
            )
            logger.info(f"Found {len(segments)} segments to index")

            for segment in segments:
                content_id = segment.id
                heading_title = segment.heading_title or ""

                slides = segment.slides
                if not slides:
                    continue

                slide_texts = []
                slide_ids = []
                slide_metas = []

                for i, slide in enumerate(slides):
                    title = slide.title or ""
                    bullets = slide.bullets or []
                    slide_text = f"{title}\n" + "\n".join(bullets)
                    slide_texts.append(slide_text)
                    slide_ids.append(f"{content_id}_slide_{i}")
                    slide_metas.append(
                        {
                            "content_id": content_id,
                            "slide_index": i,
                            "heading_title": heading_title,
                            "slide_title": title,
                        }
                    )

                try:
                    embeddings = self.embedding_model.encode(slide_texts)
                    self.collection.add(
                        embeddings=embeddings.tolist(),
                        documents=slide_texts,
                        metadatas=slide_metas,
                        ids=slide_ids,
                    )
                    logger.info(f"Indexed {len(slides)} slides for content_id {content_id}")
                except Exception as e:
                    logger.error(f"Failed to index content_id {content_id}: {e}")

        logger.info("Indexing complete")
