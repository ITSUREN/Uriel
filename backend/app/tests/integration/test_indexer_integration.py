# backend/app/tests/integration/test_indexer_integration.py
import pytest
from backend.app.index.indexer import Indexer

pytestmark = pytest.mark.integration


class TestIndexerIntegration:
    def test_indexes_all_files_in_directory(self, repos, sample_corpus_dir, preprocessing_config):
        """IT-011"""
        doc_repo, index_repo, *_ = repos
        Indexer(doc_repo, index_repo, preprocessing_config).index_directory(str(sample_corpus_dir))
        assert len(doc_repo.all()) == 2

    def test_indexed_terms_are_queryable(self, repos, sample_corpus_dir, preprocessing_config):
        """IT-012"""
        doc_repo, index_repo, *_ = repos
        Indexer(doc_repo, index_repo, preprocessing_config).index_directory(str(sample_corpus_dir))
        assert len(index_repo.get_postings("cat")) >= 1

    def test_reindexing_same_directory_does_not_duplicate(self, repos, sample_corpus_dir, preprocessing_config):
        """IT-013"""
        doc_repo, index_repo, *_ = repos
        indexer = Indexer(doc_repo, index_repo, preprocessing_config)
        indexer.index_directory(str(sample_corpus_dir))
        indexer.index_directory(str(sample_corpus_dir))
        assert len(doc_repo.all()) == 2

    def test_unparsable_file_is_skipped_without_crashing(self, repos, tmp_path, preprocessing_config):
        """IT-014 (R11)"""
        d = tmp_path / "mixed"
        d.mkdir()
        (d / "good.txt").write_text("valid content here")
        (d / "bad.pdf").write_bytes(b"not a real pdf")
        doc_repo, index_repo, *_ = repos
        Indexer(doc_repo, index_repo, preprocessing_config).index_directory(str(d))
        assert len(doc_repo.all()) == 1