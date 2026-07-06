# backend/app/parser/txt_parser.py
import logging
from typing import Iterator

logger = logging.getLogger(__name__)

class TXTParser:
    CHUNK_CHAR_SIZE = 100_000  # keeps memory + spaCy calls bounded regardless of file size

    def iter_pages(self, path: str) -> Iterator[str]:
        """Yield the file in bounded-size chunks. Never holds the whole file in memory."""
        try:
            f = open(path, "r", encoding="utf-8", errors="replace")
        except OSError as e:
            logger.error("Could not open %s: %s", path, e)
            return

        any_text = False
        buf: list[str] = []
        buf_len = 0
        try:
            with f:
                for line in f:
                    buf.append(line)
                    buf_len += len(line)
                    if buf_len >= self.CHUNK_CHAR_SIZE:
                        chunk = "".join(buf)
                        if chunk.strip():
                            any_text = True
                        yield chunk
                        buf, buf_len = [], 0
                if buf:
                    chunk = "".join(buf)
                    if chunk.strip():
                        any_text = True
                    yield chunk
        finally:
            if not any_text:
                logger.warning("Empty text file: %s", path)

    def parse(self, path: str) -> str | None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            logger.warning("Not valid UTF-8, retrying with errors='replace': %s", path)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as file:
                    text = file.read()
            except OSError as e:
                logger.error("Failed to read %s: %s", path, e)
                return None
            
        except OSError as e:
            logger.error("Could not open %s: %s", path, e)
            return None

        if not text.strip():
            logger.warning("Empty text file: %s", path)
            return None
        
        return text