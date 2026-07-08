#backend/app/api/deps.py
from functools import lru_cache
from backend.app.config.settings import get_settings
from backend.app.parser.pdf_parser import PDFParser
from backend.app.parser.txt_parser import TXTParser
from backend.app.preprocessing.config import PreprocessingConfig
from backend.app.services.config_service import ConfigService
from backend.app.services.document_service import DocumentService
from backend.app.storage.factory import build_repositories
from backend.app.index.indexer import Indexer
from backend.app.index.progress import IndexProgressTracker
from backend.app.services.index_service import IndexService
from backend.app.services.search_service import SearchService
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory
from backend.app.query_expansion.spell_correction import SpellCorrector
from backend.app.parser.content_provider import ContentProvider

@lru_cache
def get_repositories():
    settings = get_settings()
    return build_repositories(settings.db_path, settings.data_dir)

@lru_cache
def get_spell_corrector() -> SpellCorrector:
    # Singleton so its shingle index survives across requests instead of being
    # rebuilt every call — get_search_service()/get_index_service() below are
    # NOT cached (a fresh service is built per request), so anything that
    # needs to persist has to live in its own cached provider like this one.
    return SpellCorrector()

@lru_cache
def get_index_progress_tracker() -> IndexProgressTracker:
    return IndexProgressTracker();

def _current_preprocessing_config(config_repo) -> PreprocessingConfig:
    _, _, _, directory_repo = get_repositories()
    return PreprocessingConfig(**ConfigService(config_repo, directory_repo).get()["preprocessing"])

def get_config_service() -> ConfigService:
    _, _, config_repo, directory_repo = get_repositories()
    return ConfigService(config_repo, directory_repo, allowed_root=get_settings().allowed_root)

def get_index_service() -> IndexService:
    doc_repo, index_repo, config_repo, directory_repo = get_repositories()
    indexer = Indexer(
        doc_repo, index_repo, _current_preprocessing_config(config_repo),
        pdf_max_pages=get_settings().pdf_max_pages,
    )
    return IndexService(
        indexer, directory_repo,
        spell_corrector=get_spell_corrector(),
        progress_tracker=get_index_progress_tracker(),
    )

def get_search_service() -> SearchService:
    doc_repo, index_repo, config_repo, directory_repo = get_repositories()
    preprocessor = PreprocessingFactory.create(_current_preprocessing_config(config_repo))
    content_provider = ContentProvider(PDFParser(), TXTParser())
    return SearchService(doc_repo, index_repo, preprocessor, config_repo,
                          spell_corrector=get_spell_corrector(),
                          content_provider=content_provider)

def get_document_service() -> DocumentService:
    doc_repo, index_repo, config_repo, directory_repo = get_repositories()
    return DocumentService(doc_repo, directory_repo)