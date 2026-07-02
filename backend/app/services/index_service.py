#backend/app/services/index_service.py
from backend.app.index.indexer import Indexer


class IndexService:
    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def build(self, directory: str) -> dict:
        before = self.indexer.doc_repo.all()
        self.indexer.index_directory(directory)
        after = self.indexer.doc_repo.all()
        return {
            "indexed": len(after) - len(before), 
            "total_documents": len(after),
        }
    
    def stats(self) -> dict:
        docs = self.indexer.doc_repo.all()
        return {
            "documents": len(docs),
            "vocabulary_size": self.indexer.index_repo.vocabulary_size(),
        }
