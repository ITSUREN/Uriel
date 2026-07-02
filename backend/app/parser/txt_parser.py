#backend/app/parser/txt_parser.py
class TXTParser:
    def parse(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()