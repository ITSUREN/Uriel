#backend/app/services/index_service.py
from backend.app.index.indexer import Indexer
from backend.app.storage.base import DirectoryRepository
from backend.app.query_expansion.spell_correction import SpellCorrector


class IndexService:
    def __init__(self, indexer: Indexer, directory_repo:DirectoryRepository, spell_corrector: SpellCorrector | None = None):
        self.indexer = indexer
        self.directory_repo = directory_repo
        self.spell_corrector = spell_corrector

    def build(self) -> dict:
        before = len(self.indexer.doc_repo.all())
        for d in self.directory_repo.list():
            self.indexer.index_directory(d["path"])
        after = len(self.indexer.doc_repo.all())
        if self.spell_corrector:
            self.spell_corrector.invalidate()
        return {"indexed": after - before, "total_documents": after}
    
    def rebuild(self) -> dict:
        self.indexer.index_repo.clear()
        for doc in self.directory_repo.list():
            self.indexer.index_directory(doc["path"])
        if self.spell_corrector:
            self.spell_corrector.invalidate()
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
