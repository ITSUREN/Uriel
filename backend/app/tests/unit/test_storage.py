import pytest
from datetime import datetime
from backend.app.models.document import Document
from backend.app.models.posting import Posting

pytestmark = pytest.mark.unit


class TestSQLiteDocumentRepository:
    def test_save_and_get_roundtrip(self, repos):
        """UT-061"""
        doc_repo, *_ = repos
        doc_repo.save(Document(0, "/a.txt", "a.txt", 5, datetime.now()))
        assert doc_repo.get(0).path == "/a.txt"

    def test_exists_by_path(self, repos):
        """UT-062"""
        doc_repo, *_ = repos
        assert doc_repo.exists_by_path("/missing.txt") is False
        doc_repo.save(Document(0, "/present.txt", "present.txt", 1, datetime.now()))
        assert doc_repo.exists_by_path("/present.txt") is True

    def test_next_id_increments_from_max(self, repos):
        """UT-063"""
        doc_repo, *_ = repos
        assert doc_repo.next_id() == 0
        doc_repo.save(Document(0, "/a.txt", "a.txt", 1, datetime.now()))
        assert doc_repo.next_id() == 1


class TestSQLiteIndexRepository:
    def test_add_and_get_postings(self, repos):
        """UT-071"""
        doc_repo, index_repo, *_ = repos
        doc_repo.save(Document(0, "/a.txt", "a.txt", 3, datetime.now()))
        index_repo.add_posting("cat", [Posting(0, 2, [0, 2])])
        assert index_repo.get_postings("cat")[0].term_frequency == 2

    def test_document_frequency_counts_distinct_docs(self, repos):
        """UT-072"""
        doc_repo, index_repo, *_ = repos
        for i in range(3):
            doc_repo.save(Document(i, f"/{i}.txt", f"{i}.txt", 1, datetime.now()))
        index_repo.add_posting("cat", [Posting(0, 1, [0])])
        index_repo.add_posting("cat", [Posting(1, 5, [0])])
        assert index_repo.document_frequency("cat") == 2

    def test_clear_removes_documents_and_postings(self, repos):
        """UT-073"""
        doc_repo, index_repo, *_ = repos
        doc_repo.save(Document(0, "/a.txt", "a.txt", 1, datetime.now()))
        index_repo.add_posting("cat", [Posting(0, 1, [0])])
        index_repo.clear()
        assert doc_repo.all() == {} and index_repo.get_postings("cat") == []

    def test_forward_index_roundtrip(self, repos):
        """UT-074: document_terms table backing Rocchio's per-doc vectors"""
        doc_repo, index_repo, *_ = repos
        doc_repo.save(Document(0, "/a.txt", "a.txt", 3, datetime.now()))
        index_repo.add_document_terms(0, {"cat": 2, "mat": 1})
        assert index_repo.get_document_terms(0) == {"cat": 2, "mat": 1}


class TestSQLiteDirectoryRepository:
    def test_default_directory_seeded_and_not_deletable(self, repos):
        """UT-081 (R7)"""
        *_, directory_repo = repos
        dirs = directory_repo.list()
        assert len(dirs) == 1 and dirs[0]["is_default"] is True
        with pytest.raises(PermissionError):
            directory_repo.delete(dirs[0]["id"])

    def test_add_and_delete_non_default_directory(self, repos):
        """UT-082 (R7)"""
        *_, directory_repo = repos
        added = directory_repo.add("/extra/dir")
        assert added["is_default"] is False
        directory_repo.delete(added["id"])
        assert len(directory_repo.list()) == 1

    def test_delete_unknown_id_raises(self, repos):
        """UT-083"""
        *_, directory_repo = repos
        with pytest.raises(ValueError):
            directory_repo.delete(9999)