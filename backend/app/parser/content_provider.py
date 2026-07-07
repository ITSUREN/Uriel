# backend/app/parser/content_provider.py
from typing import Iterator
from backend.app.parser.pdf_parser import PDFParser
from backend.app.parser.txt_parser import TXTParser

class ContentProvider:
    """Single entry point for streaming a document's text, used by both
    the indexer (at index time) and the snippet builder (at query time),
    so there's one place that knows how to read a .pdf vs a .txt."""
    def __init__(self, pdf_parser: PDFParser, txt_parser: TXTParser):
        self.pdf_parser = pdf_parser
        self.txt_parser = txt_parser

    def iter_pages(self, path: str) -> Iterator[str]:
        lower = path.lower()
        if lower.endswith(".pdf"):
            yield from self.pdf_parser.iter_pages(path)
        elif lower.endswith(".txt"):
            yield from self.txt_parser.iter_pages(path)
        # else: unsupported extension, yield nothing