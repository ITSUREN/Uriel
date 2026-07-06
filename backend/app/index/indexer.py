#backend/app/index/indexer.py
import os
from datetime import datetime

from logging import getLogger
from typing import Iterator
from collections import defaultdict

from backend.app.models.document import Document
from backend.app.models.posting import Posting

from backend.app.preprocessing.config import PreprocessingConfig
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory

from backend.app.storage.base import DocumentRepository, IndexRepository  
from backend.app.parser.pdf_parser import PDFParser
from backend.app.parser.txt_parser import TXTParser

logger = getLogger(__name__)

class Indexer:
    def __init__(self,doc_repo: DocumentRepository, index_repo: IndexRepository, config: PreprocessingConfig = PreprocessingConfig(), pdf_max_pages: int | None = None):
        self.doc_repo = doc_repo
        self.index_repo = index_repo
        self.preprocessor = PreprocessingFactory.create(config)

        self.pdf_parser : PDFParser = PDFParser(max_pages=pdf_max_pages)
        self.txt_parser : TXTParser = TXTParser()

    def index_directory(self, directory: str):
        for root, _, files in os.walk(directory):
            for file in files:
                path = os.path.join(root, file)
                if file.endswith(".pdf"):
                    pages = self.pdf_parser.iter_pages(path)
                elif file.endswith(".txt"):
                    pages = self.txt_parser.iter_pages(path)
                else:
                    continue
                # This try/except is the actual fix for the startup crash:
                # a failure on ONE document (spaCy limit, corrupt file,
                # OOM, whatever) is logged and skipped instead of taking
                # the whole indexing run (and app startup) down with it.
                try:
                    self.index_document(path, file, pages)
                except Exception:
                    logger.exception("Failed to index %s — skipping this document", path)
                    continue

    def index_document(self, path:str, filename:str, pages: Iterator[str]):
        if self.doc_repo.exists_by_path(path):
            return #or: reindex if mtime changed
        
        positions_map: dict[str, list[int]] = defaultdict(list)
        offset = 0
        for page_num, page_text in enumerate(pages):
            if not page_text or not page_text.strip():
                continue
            try:
                processed = self.preprocessor.process(page_text)
            except Exception:
                # Skip just this page/chunk, keep indexing the rest of the doc.
                logger.exception(
                    "Failed to preprocess page %d of %s — skipping that page",
                    page_num, path,
                )
                continue
            for i, term in enumerate(processed.terms):
                positions_map[term].append(offset + i)
            offset += len(processed.terms)

        if offset == 0:
            logger.warning("No indexable tokens produced for %s — skipping", path)
            return

        doc_id = self.doc_repo.next_id()
        doc = Document(
            doc_id=doc_id,
            path=path,
            title=filename,
            length=offset,
            last_modified=datetime.fromtimestamp(os.path.getmtime(path)),
            content="",  # no longer stored — see snippet_service.py
        )
        self.doc_repo.save(doc)

        entries = [
            (term, [Posting(doc_id=doc_id, term_frequency=len(positions), positions=positions)])
            for term, positions in positions_map.items()
        ]
        self.index_repo.add_postings_bulk(entries)
        self.index_repo.add_document_terms(doc_id, {t: len(p) for t, p in positions_map.items()})