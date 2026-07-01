import fitz

class PDFParser:
    def parse(self, path: str) -> str:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += str(page.get_text("text"))
        return text