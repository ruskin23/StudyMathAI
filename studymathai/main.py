import os
import argparse
from dotenv import load_dotenv

from studymathai.db import DatabaseConnection
from studymathai.utils import TextCleaner
from studymathai.processor import BookProcessor, PageTextExtractor, BookContentExtractor, PageAwareChapterSegmentor
from studymathai.generator import SlideGenerator
from studymathai.chatbot import ChatBot
from studymathai.models import BookContent

def parse_args():
    parser = argparse.ArgumentParser(description="StudyMathAI pipeline runner")
    
    parser.add_argument("--file", 
                        type=str,
                        required=True, 
                        help="PDF filename")
    
    parser.add_argument("--data_dir", 
                        type=str,
                        required=True, 
                        help="Directory containing the PDF")
    
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()
    
    # === 1. Setup ===
    filename = args.file
    fileloc = args.data_dir
    filepath = os.path.join(fileloc, filename)
    print(f"Filepath = {filepath}")
    
    db = DatabaseConnection()
    text_cleaner = TextCleaner()

    # === 2. Book context ===
    processor = BookProcessor(filepath, db)

    # === 3. Extract page-level text ===
    page_extractor = PageTextExtractor(processor)
    page_extractor.extract_and_store_pages()

    # === 4. Extract chapters and TOC entries ===
    content_extractor = BookContentExtractor(processor)
    content_extractor.extract_and_save()

    # === 5. Segment each chapter into heading-text blocks
    with db.get_session() as session:
        chapters = session.query(BookContent).filter_by(book_id=processor.book.id).all()
        
    for chapter in chapters:
        print(f"Segmenting chapter: {chapter.chapter_title}")
        segmentor = PageAwareChapterSegmentor(processor, chapter, text_cleaner)
        segmentor.segment_and_store()

    # === 6. Generate slides for segments
    slidegen = SlideGenerator(db)
    slidegen.process_book(processor.book.id)

    print("✅ All processing complete.")



def bot():
    bot = ChatBot()
    print("🤖 ChatBot ready with retrieval. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower().strip() in {"exit", "quit"}:
            break

        reply = bot.get_response(user_input)
        print(f"Bot: {reply}")


if __name__ == '__main__':
    main()
