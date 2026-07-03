#backend/app/services/index_service.py
from backend.app.index.indexer import Indexer
from backend.app.storage.base import DirectoryRepository


class IndexService:
    def __init__(self, indexer: Indexer, directory_repo:DirectoryRepository):
        self.indexer = indexer
        self.directory_repo = directory_repo

    def build(self) -> dict:
        before = len(self.indexer.doc_repo.all())
        for d in self.directory_repo.list():
            self.indexer.index_directory(d["path"])
        after = len(self.indexer.doc_repo.all())
        return {"indexed": after - before, "total_documents": after}
    
    def rebuild(self) -> dict:
        self.indexer.index_repo.clear()
        for doc in self.directory_repo.list():
            self.indexer.index_directory(doc["path"])
        return {
            "reindexed": len(self.indexer.doc_repo.all())
        }
    
    def stats(self) -> dict:
        docs = self.indexer.doc_repo.all()
        return {
            "documents": len(docs),
            "vocabulary_size": self.indexer.index_repo.vocabulary_size(),
            "directories": self.directory_repo.list(),
        }
