from pydantic import BaseModel, Field


class Text(BaseModel):
    """
    Represents a text content extracted from a page.
    This is used to ensure that the text content is properly structured and validated.
    """

    page_number: int = Field(..., description="The page number of the text")
    page_text: str = Field(..., description="The actual text content of the page")


class TOCEntry(BaseModel):
    """
    Represents a Table of Contents (TOC) entry.
    This is used to structure the TOC entries with their hierarchy and page numbers."""

    level: int = Field(
        ...,
        description=("The level of the TOC entry (1 for main chapters, 2 for subsections, etc.)"),
    )
    title: str = Field(..., description="The title of the TOC entry")
    page: int = Field(..., description="The page number where this entry starts")


class Chapter(BaseModel):
    """
    Represents a chapter with its title, page range, and extracted text.
    This is used to structure the chapter content for further prfocessing or storage.
    """

    title: str = Field(..., description="The title of the chapter")
    start_page: int = Field(..., description="The starting page of the chapter")
    end_page: int = Field(..., description="The ending page of the chapter")


class Line(BaseModel):
    """
    Represents a mapping of lines to their corresponding page numbers.
    This is used to keep track of which lines belong to which pages in the book.
    """

    page_number: int = Field(..., description="The page number of the text")
    line_number: int = Field(..., description="The line number on that page")
    text: str = Field(..., description="The actual text content of that line")

    def __eq__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return (self.page_number, self.line_number) == (other.page_number, other.line_number)


class Heading(BaseModel):
    """
    Represents a heading in the chapter.
    This is used to structure the headings with their hierarchy and page numbers.
    """

    title: str = Field(..., description="The title of the heading")
    level: int = Field(
        ...,
        description=("The level of the heading (1 for main headings, 2 for subheadings, etc.)"),
    )
    page_number: int = Field(..., description="The page number where this heading starts")


class HeadingContent(BaseModel):
    """
    Represents the content associated with a heading.
    This is used to store the text content of a heading along with its title and level.
    """

    heading: Heading = Field(
        ...,
        description="The heading object containing title, level, and page number",
    )
    text: str = Field(..., description="The actual text content of the heading")


class Slide(BaseModel):
    """
    Represents a single slide in a slide deck.
    This is used to structure the content of each slide with a title and bullet points.
    """

    title: str = Field(..., description="The title of the slide")
    bullets: list[str] = Field(..., description="The bullet points or content of the slide")


class SlideDeck(BaseModel):
    """
    Represents a slide deck containing multiple slides.
    This is used to structure the slides for presentation or further processing.
    """

    heading: str = Field(..., description="The heading or title of the slide deck")
    slides: list[Slide] = Field(..., description="The list of slides in the deck")
