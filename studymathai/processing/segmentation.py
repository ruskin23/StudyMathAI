import numpy as np
from sentence_transformers import SentenceTransformer, util

from studymathai.data_models import Heading, HeadingContent, Line, Text
from studymathai.logging_config import get_logger

logger = get_logger(__name__)

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def filter_lines_by_page(lines: list[Line], page_number: int) -> list[Line]:
    """
    Filters the line map to only include lines from the specified page number.
    """
    return [line for line in lines if line.page_number == page_number]


def get_similarity_score(heading: str, line_texts: list[str]) -> list[float]:
    """
    Computes similarity scores between a heading and a list of line texts.
    Returns a list of similarity scores.
    """
    if not line_texts:
        return []

    heading_embedding = EMBED_MODEL.encode([heading])[0]
    line_embeddings = EMBED_MODEL.encode(line_texts)
    scores = util.cos_sim(heading_embedding, line_embeddings)[0].cpu().numpy()
    return scores.tolist()


def get_similar_line(heading: Heading, lines: list[Line]) -> tuple[Line | None, float]:
    """
    Finds the most similar line to the heading in the line map.
    Returns the Line entry and its similarity score.
    """
    page_lines = filter_lines_by_page(lines, heading.page_number)
    if not page_lines:
        return None, 0.0

    line_texts = [line.text for line in page_lines]
    scores = get_similarity_score(heading.title, line_texts)

    if not scores:
        return None, 0.0

    best_idx = int(np.argmax(scores))
    return page_lines[best_idx], scores[best_idx]


def build_line_map(page_texts: list[Text]) -> list[Line]:
    """
    Builds a line map from the page texts.
    Each entry in the line map contains the page number and the line number.
    """
    line_map = []
    for text in page_texts:
        lines = text.page_text.splitlines()
        for i, line in enumerate(lines):
            if line.strip():
                line_map.append(
                    Line(page_number=text.page_number, line_number=i, text=line.strip())
                )

    logger.info(f"Built line map with {len(line_map)} entries from {len(page_texts)} pages")
    return line_map


def build_heading_map(headings: list[Heading], lines: list[Line]) -> list[tuple[Heading, Line]]:
    """
    Maps headings to their corresponding lines in the text based on similarity.
    Returns a list of tuples containing the heading and the corresponding Line entry.
    """
    heading_map = []
    for heading in headings:
        line_entry, score = get_similar_line(heading, lines)
        if line_entry and score > 0.3:  # Only keep matches with reasonable similarity
            heading_map.append((heading, line_entry))
            logger.info(
                "Matched heading '%s' to line '%s' with score %.4f",
                heading.title,
                line_entry.text,
                score,
            )
        else:
            logger.warning(
                "No good match found for heading '%s' on page %s",
                heading.title,
                heading.page_number,
            )
    return heading_map


def segment_chapter(headings: list[Heading], page_texts: list[Text]) -> list[HeadingContent]:
    """
    Segments a chapter by matching headings to lines in the text
    and extracting content between headings.
    Returns a list of HeadingContent objects.
    """
    if not headings:
        logger.warning("No headings provided for segmentation.")
        return []

    lines = build_line_map(page_texts)
    heading_matches = build_heading_map(headings, lines)

    if not heading_matches:
        logger.warning("No headings matched to lines in the chapter.")
        return []

    # Sort headings by page number and line number
    heading_matches.sort(key=lambda x: (x[1].page_number, x[1].line_number))

    segments = []

    for i, (heading, heading_line) in enumerate(heading_matches):
        # Find the next heading to determine the end boundary
        if i + 1 < len(heading_matches):
            next_heading_line = heading_matches[i + 1][1]
            # Extract text between current heading and next heading
            section_lines = [
                line
                for line in lines
                if (
                    (line.page_number > heading_line.page_number)
                    or (
                        line.page_number == heading_line.page_number
                        and line.line_number > heading_line.line_number
                    )
                )
                and (
                    (line.page_number < next_heading_line.page_number)
                    or (
                        line.page_number == next_heading_line.page_number
                        and line.line_number < next_heading_line.line_number
                    )
                )
            ]
        else:
            # This is the last heading, extract until the end
            section_lines = [
                line
                for line in lines
                if (
                    (line.page_number > heading_line.page_number)
                    or (
                        line.page_number == heading_line.page_number
                        and line.line_number > heading_line.line_number
                    )
                )
            ]

        heading_text = "\n".join(line.text for line in section_lines)

        if heading_text.strip():  # Only add if there's content
            segments.append(HeadingContent(heading=heading, text=heading_text.strip()))
            logger.info(f"Segmented {len(section_lines)} lines for heading '{heading.title}'")

    logger.info(f"Segmented {len(segments)} headings in the chapter.")
    return segments
