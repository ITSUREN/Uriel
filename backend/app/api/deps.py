#backend/app/api/deps.py
from functools import lru_cache
from backend.app.config.settings import get_settings
from backend.app.storage.factory import build_repositories
from backend.app.index.indexer import Indexer
from backend.app.services.index_service import IndexService
from backend.app.services.search_service import SearchService
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory

@lru_cache
def _repos():
    settings = get_settings()
    return build_repositories(settings.db_path)

@lru_cache
def _indexer() -> Indexer:
    doc_repo, index_repo = _repos()
    return Indexer(doc_repo, index_repo)

def get_index_service() -> IndexService:
    return IndexService(_indexer())

def get_search_service() -> SearchService:
    doc_repo, index_repo = _repos()
    preprocessor = _indexer().preprocessor
    return SearchService(doc_repo, index_repo, preprocessor)