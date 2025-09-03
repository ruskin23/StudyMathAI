from studymathai.data_models import Chapter, Text, TOCEntry
from studymathai.database import BookChapter, PageText, TableOfContents


def convert_text(entry: PageText) -> Text:
    return Text(page_number=entry.page_number, page_text=entry.page_text)


def convert_toc_entry(entry: TableOfContents) -> TOCEntry:
    return TOCEntry(
        level=entry.level,
        title=entry.title,
        page=entry.page_number,
    )


def convert_chapter_entry(entry: BookChapter) -> Chapter:
    return Chapter(title=entry.chapter_title, start_page=entry.start_page, end_page=entry.end_page)
