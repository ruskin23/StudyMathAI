import os
import json
from openai import OpenAI
from studymathai.db import DatabaseConnection
from studymathai.models import BookContent, ChapterContent, GeneratedSlide
from pydantic import BaseModel
from typing import List
from sqlalchemy.exc import IntegrityError

# --- Slide Model Schema ---

class Slide(BaseModel):
    title: str
    bullets: List[str]

class SlideDeck(BaseModel):
    heading: str
    slides: List[Slide]

# --- Slide Generator Class ---

class SlideGenerator:
    """
    Uses GPT to generate slides for each chapter segment (heading-text block).
    Stores output in the GeneratedSlide table.
    """

    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.model=os.getenv("MODEL_NAME")
        self.client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

    def generate_slides(self, text: str, heading: str) -> SlideDeck:
        example = {
            "heading": "Vectors in $\\mathbb{F}^n$",
            "slides": [
                {
                    "title": "What is a List?",
                    "bullets": [
                        "A *list* of length $n$ is an ordered collection of $n$ elements.",
                        "Elements can be numbers, lists, or other objects.",
                        "Two lists are equal if they have the same length, elements, and order.",
                        "Notation: $(z_1, \\dots, z_n)$"
                    ]
                },
                {
                    "title": "Vectors and Coordinates",
                    "bullets": [
                        "Fix a positive integer $n$ for context.",
                        "$\\mathbb{F}^n$ is the set of lists of $n$ elements from $\\mathbb{F}$.",
                        "Each element $x_k$ is the $k^{th}$ *coordinate* of the vector."
                    ]
                },
                {
                    "title": "Vector Addition in $\\mathbb{F}^n$",
                    "bullets": [
                        "Addition is done component-wise:",
                        "$(x_1, \\dots, x_n) + (y_1, \\dots, y_n) = (x_1 + y_1, \\dots, x_n + y_n)$",
                        "Commutativity: $x + y = y + x$ for any $x, y \\in \\mathbb{F}^n$"
                    ]
                },
                {
                    "title": "Zero Vector and Additive Inverse",
                    "bullets": [
                        "The zero vector: $0 = (0, \\dots, 0)$",
                        "For any $x \\in \\mathbb{F}^n$, the additive inverse $-x$ satisfies: $x + (-x) = 0$",
                        "If $x = (x_1, \\dots, x_n)$ then $-x = (-x_1, \\dots, -x_n)$"
                    ]
                },
                {
                    "title": "Scalar Multiplication",
                    "bullets": [
                        "Multiplying scalar $\\lambda \\in \\mathbb{F}$ with vector $(x_1, \\dots, x_n)$:",
                        "$\\lambda(x_1, \\dots, x_n) = (\\lambda x_1, \\dots, \\lambda x_n)$",
                        "Applies each scalar multiplication component-wise."
                    ]
                }
            ]
        }

        instructions = """
        You are a tutor, trained to generate high-quality Markdown slides. 
        You are provided with unstructured text from a textbook.
        Your task is to convert this text into a well-structured Markdown slide presentation.
        Each slide should be a self-sufficient study material, explaining all necessary concepts concisely.
        Rewrite the Heading provided by removing unecessary numbers
        """

        prompt = f"""
        Stick to the following guidelines for generating slides
        1. Use proper Markdown syntax for lists, headers, and code blocks (e.g., ``` for code),  
        2. ensure mathematical expressions are enclosed in `$...$` for inline math or `$$...$$` for block math.
        2. Each slide should have a title that reflects its content, helping the reader quickly understand the topic covered on that slide.
        3. Ensure that all slides are appropriately structured with bullet points.
        4. Make the slides clean, organized, and easy to read, without requiring any additional modifications.

        Example Slide output
        {json.dumps(example, ensure_ascii=False, indent=2)}

        Heading: 
        {heading}

        Text:
        {text}
        """

        response = self.client.responses.parse(
            model=self.model,
            instructions=instructions,
            input=prompt,
            text_format=SlideDeck
        )

        return response.output_parsed

    def process_book(self, book_id: int):
        with self.db.get_session() as session:
            chapters = session.query(BookContent).filter_by(book_id=book_id).all()
            
        for chapter in chapters:
            with self.db.get_session() as session:
                segments = session.query(ChapterContent).filter_by(chapter_id=chapter.id).all()
                
            for segment in segments:
                if not segment.content_text or len(segment.content_text.split()) < 20:
                    continue
                
                # Check if slides already exist for this segment
                with self.db.get_session() as session:
                    existing = session.query(GeneratedSlide).filter_by(content_id=segment.id).first()
                    if existing:
                        continue

                print(f"Generating slides for: {segment.heading_title}")
                slide_deck = self.generate_slides(segment.content_text, segment.heading_title)
                
                with self.db.get_session() as session:
                    slide = GeneratedSlide(
                        content_id=segment.id,
                        book_id=segment.book_id,
                        slides_json=json.dumps(slide_deck.model_dump()),
                        model_info=self.model
                    )
                    session.add(slide)
                        
        print("✅ Slide generation complete.")
