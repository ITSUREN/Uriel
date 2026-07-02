# backend/app/parser/pdf_parser.py
import logging
import fitz

logger = logging.getLogger(__name__)

class PDFParser:
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