#backend/app/index/indexer.py
import os
from datetime import datetime

from backend.app.index.inverted_index import InvertedIndex

from backend.app.models.document import Document
from backend.app.models.posting import Posting

from backend.app.preprocessing.config import PreprocessingConfig
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory
from backend.app.parser.pdf_parser import PDFParser
from backend.app.parser.txt_parser import TXTParser

class Indexer:
    def __init__(self, config: PreprocessingConfig = PreprocessingConfig()):
        self.index : InvertedIndex = InvertedIndex()
        self.preprocessor = PreprocessingFactory.create(config)

        self.pdf_parser : PDFParser = PDFParser()
        self.txt_parser : TXTParser = TXTParser()

        self.documents : dict[int, Document] = {}
        self.doc_id_counter : int = 0

    def index_directory (self, directory: str):
        # Probably will need a method to detect file updates and reindex them, but for now, just index everything
        for root, _, files in os.walk(directory):
            for file in files:
                path = os.path.join(root, file)

                if file.endswith(".pdf"):
                    text = self.pdf_parser.parse(path)
                elif file.endswith(".txt"):
                    text = self.txt_parser.parse(path)
                else:
                    continue

                self.index_document(path, file, text)

    def index_document(self, path:str, filename:str, text:str):
        doc_id = self.doc_id_counter
        self.doc_id_counter += 1

        processed_doc = self.preprocessor.process(text)
        tokens = processed_doc.terms

        self.documents[doc_id] = Document(
            doc_id = doc_id,
            path = path,
            title = filename,
            length = len(tokens),
            last_modified = datetime.fromtimestamp(os.path.getmtime(path))
        )

        positions_map : dict[str, list[int]] = {}

        for pos, token in enumerate(tokens):
            if token not in positions_map:
                positions_map[token] = []
            positions_map[token].append(pos)
        
        for term, positions in positions_map.items():
            posting = Posting(
                doc_id = doc_id,
                term_frequency = len(positions),
                positions = positions
            )

            self.index.add_posting(term, posting)