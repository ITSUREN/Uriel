import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import get_index_service, get_search_service, get_config_service
from backend.app.index.indexer import Indexer
from backend.app.services.index_service import IndexService
from backend.app.services.search_service import SearchService
from backend.app.services.config_service import ConfigService
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory


@pytest.fixture
def client(repos, sample_corpus_dir, preprocessing_config):
    doc_repo, index_repo, config_repo, directory_repo = repos
    directory_repo.add(str(sample_corpus_dir))
    preprocessor = PreprocessingFactory.create(preprocessing_config)

    app.dependency_overrides[get_index_service] = lambda: IndexService(
        Indexer(doc_repo, index_repo, preprocessing_config), directory_repo
    )
    app.dependency_overrides[get_search_service] = lambda: SearchService(
        doc_repo, index_repo, preprocessor, config_repo
    )
    app.dependency_overrides[get_config_service] = lambda: ConfigService(
        config_repo, directory_repo, allowed_root=None
    )

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()