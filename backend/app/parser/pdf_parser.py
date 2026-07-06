# backend/app/parser/pdf_parser.py
import logging
import fitz
from typing import Iterator, cast

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self, max_pages: int | None = None):
        # Optional escape hatch: if set, PDFs with more pages are skipped
        # entirely (logged, not crashed). None = no limit: page-by-page
        # streaming below means there generally shouldn't need to be one.
        self.max_pages = max_pages
    
    def iter_pages(self, path: str) -> Iterator[str]:
        """Yield page text lazily. Never holds more than one page in memory."""
        try:
            with fitz.open(path) as doc:
                if doc.is_encrypted and not doc.authenticate(""):
                    logger.warning("Skipping encrypted PDF: %s", path)
                    return
                if self.max_pages is not None and doc.page_count > self.max_pages:
                    logger.warning(
                        "Skipping %s: %d pages exceeds configured max_pages=%d",
                        path, doc.page_count, self.max_pages,
                    )
                    return
                any_text = False
                for page in doc:
                    text = cast(str, page.get_text("text"))
                    if text.strip():
                        any_text = True
                    yield text
                if not any_text:
                    logger.warning("No extractable text (likely scanned/image-only): %s", path)
        except fitz.FileDataError as e:
            logger.error("Corrupt or unreadable PDF %s: %s", path, e)
            return
        except Exception:
            logger.exception("Unexpected error parsing PDF %s", path)
            return

    def parse(self, path: str) -> str | None:
        try:
            text = ""
            with fitz.open(path) as doc:
                if doc.is_encrypted and not doc.authenticate(""):
                    logger.warning("Skipping encrypted PDF: %s", path)
                    return None
                for page in doc:
                    text += str(page.get_text("text"))
            if not text.strip():
                logger.warning("No extractable text (likely scanned/image-only): %s", path)
                return None
            return text
        except fitz.FileDataError as e:
            logger.error("Corrupt or unreadable PDF %s: %s", path, e)
            return None
        except Exception:
            logger.exception("Unexpected error parsing PDF %s", path)
            return None