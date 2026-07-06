#backend/app/index/indexer.py
import os
from datetime import datetime

from backend.app.models.document import Document
from backend.app.models.posting import Posting

from backend.app.preprocessing.config import PreprocessingConfig
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory

from backend.app.storage.base import DocumentRepository, IndexRepository  
from backend.app.parser.pdf_parser import PDFParser
from backend.app.parser.txt_parser import TXTParser

class Indexer:
    def __init__(self,doc_repo: DocumentRepository, index_repo: IndexRepository, config: PreprocessingConfig = PreprocessingConfig()):
        self.doc_repo = doc_repo
        self.index_repo = index_repo
        self.preprocessor = PreprocessingFactory.create(config)

        self.pdf_parser : PDFParser = PDFParser()
        self.txt_parser : TXTParser = TXTParser()

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

                if text is None:
                    continue  # parser already logged why
                
                self.index_document(path, file, text)

    def index_document(self, path:str, filename:str, text:str):
        if self.doc_repo.exists_by_path(path):
            return #or: reindex if mtime changed
        
        doc_id = self.doc_repo.next_id()
        processed_doc = self.preprocessor.process(text)
        tokens = processed_doc.terms
        doc = Document(
            doc_id = doc_id,
            path = path,
            title = filename,
            length = len(tokens),
            last_modified = datetime.fromtimestamp(os.path.getmtime(path)),
            content = text
        )
        self.doc_repo.save(doc)

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
            self.index_repo.add_posting(term, [posting])

        # Adding to the forward index, TODO: consider putting this inside the loop above to avoid iterating twice, but it may be cleaner this way
        entries = [(term, [Posting(doc_id=doc_id, term_frequency=len(positions), positions=positions)]) for term, positions in positions_map.items()]
        self.index_repo.add_postings_bulk(entries)