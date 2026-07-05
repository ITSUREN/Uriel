# backend/app/tests/integration/test_search_service_integration.py
import pytest
from backend.app.index.indexer import Indexer
from backend.app.services.search_service import SearchService
from backend.app.services.config_service import DEFAULT_CONFIG
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory
from backend.app.algorithms.ranking_factory import RankingAlgorithmType

pytestmark = pytest.mark.integration


def _build_service(repos, corpus_dir, preprocessing_config):
    doc_repo, index_repo, config_repo, _ = repos
    config_repo.save(DEFAULT_CONFIG)
    Indexer(doc_repo, index_repo, preprocessing_config).index_directory(str(corpus_dir))
    preprocessor = PreprocessingFactory.create(preprocessing_config)
    return SearchService(doc_repo, index_repo, preprocessor, config_repo)


class TestSearchServiceIntegration:
    def test_query_ranks_correct_document_first_bm25(self, repos, sample_corpus_dir, preprocessing_config):
        """IT-021"""
        svc = _build_service(repos, sample_corpus_dir, preprocessing_config)
        results = svc.search("cat", algorithm=RankingAlgorithmType.BM25)
        assert results[0].title == "cats.txt"

    def test_query_ranks_correct_document_first_tfidf(self, repos, sample_corpus_dir, preprocessing_config):
        """IT-022"""
        svc = _build_service(repos, sample_corpus_dir, preprocessing_config)
        results = svc.search("cat", algorithm=RankingAlgorithmType.TFIDF)
        assert results[0].title == "cats.txt"

    def test_feedback_measurably_changes_scores(self, repos, sample_corpus_dir, preprocessing_config):
        """IT-023 (R10)"""
        svc = _build_service(repos, sample_corpus_dir, preprocessing_config)
        docs = svc.doc_repo.all()
        cats_id = next(d.doc_id for d in docs.values() if d.title == "cats.txt")
        baseline = svc.search("pets", algorithm=RankingAlgorithmType.BM25)
        boosted = svc.search_with_feedback("pets", relevant_doc_ids=[cats_id], non_relevant_doc_ids=[], algorithm=RankingAlgorithmType.BM25)
        assert baseline[0].score != boosted[0].score