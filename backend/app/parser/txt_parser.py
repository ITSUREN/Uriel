# backend/app/parser/txt_parser.py
import logging

logger = logging.getLogger(__name__)

class TXTParser:
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