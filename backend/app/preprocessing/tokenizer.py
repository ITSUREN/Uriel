import re

class Tokenizer:
    def tokenize(self, text: str) -> list[str]:
        # Simple first revision
        return re.findall(r'\b\w+\b', text.lower())