import json

from openai import OpenAI

from studymathai.data_models import SlideDeck


def generate_slides(client: OpenAI, model: str, heading_title: str, heading_text: str) -> SlideDeck:
    example = {
        "heading": "Vectors in $\\mathbb{F}^n$",
        "slides": [
            {
                "title": "What is a List?",
                "bullets": [
                    "A *list* of length $n$ is an ordered collection of $n$ elements.",
                    "Elements can be numbers, lists, or other objects.",
                    "Two lists are equal if they have the same length, elements, and order.",
                    "Notation: $(z_1, \\dots, z_n)$",
                ],
            },
            {
                "title": "Vectors and Coordinates",
                "bullets": [
                    "Fix a positive integer $n$ for context.",
                    "$\\mathbb{F}^n$ is the set of lists of $n$ elements from $\\mathbb{F}$.",
                    "Each element $x_k$ is the $k^{th}$ *coordinate* of the vector.",
                ],
            },
            {
                "title": "Vector Addition in $\\mathbb{F}^n$",
                "bullets": [
                    "Addition is done component-wise:",
                    "$(x_1, \\dots, x_n) + (y_1, \\dots, y_n) = (x_1 + y_1, \\dots, x_n + y_n)$",
                    "Commutativity: $x + y = y + x$ for any $x, y \\in \\mathbb{F}^n$",
                ],
            },
            {
                "title": "Zero Vector and Additive Inverse",
                "bullets": [
                    "The zero vector: $0 = (0, \\dots, 0)$",
                    (
                        "For any $x \\in \\mathbb{F}^n$, the additive inverse $-x$ satisfies: "
                        "$x + (-x) = 0$"
                    ),
                    "If $x = (x_1, \\dots, x_n)$ then $-x = (-x_1, \\dots, -x_n)$",
                ],
            },
            {
                "title": "Scalar Multiplication",
                "bullets": [
                    (
                        "Multiplying scalar $\\lambda \\in \\mathbb{F}$ with vector $(x_1, "
                        "\\dots, x_n)$:"
                    ),
                    "$\\lambda(x_1, \\dots, x_n) = (\\lambda x_1, \\dots, \\lambda x_n)$",
                    "Applies each scalar multiplication component-wise.",
                ],
            },
        ],
    }

    instructions = """
    You are a tutor, trained to generate high-quality Markdown slides.
    You are provided with unstructured text from a textbook.
    Your task is to convert this text into a well-structured Markdown slide presentation.
    Each slide should be a self-sufficient study material,
    explaining all necessary concepts concisely.
    Rewrite the Heading provided by removing unecessary numbers
    """

    prompt = f"""
    Stick to the following guidelines for generating slides
    1. Use proper Markdown syntax for lists, headers, and code blocks (e.g., ``` for code),
    2. ensure mathematical expressions are enclosed in `$...$` for inline math or
       `$$...$$` for block math.
    2. Each slide should have a title that reflects its content, helping the reader quickly
       understand the topic covered on that slide.
    3. Ensure that all slides are appropriately structured with bullet points.
    4. Make the slides clean, organized, and easy to read, without requiring any additional
       modifications.

    Example Slide output
    {json.dumps(example, ensure_ascii=False, indent=2)}

    Heading:
    {heading_title}

    Text:
    {heading_text}
    """

    response = client.responses.parse(
        model=model, instructions=instructions, input=prompt, text_format=SlideDeck
    )

    return response.output_parsed
