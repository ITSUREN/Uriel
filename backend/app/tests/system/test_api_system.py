import pytest

pytestmark = pytest.mark.system


class TestSystemEndToEnd:
    def test_full_flow_add_directory_build_index_search(self, client):
        """ST-011: covers R1, R2, R3/R4, R5, R7 in one realistic flow"""
        dirs = client.get("/config/directories").json()
        assert len(dirs) == 2  # seeded default + the one added by the fixture

        build = client.post("/index/build")
        assert build.status_code == 200
        assert build.json()["total_documents"] == 2

        for algo in ("tfidf", "bm25"):
            resp = client.post("/search", json={"query": "cat", "algorithm": algo})
            assert resp.status_code == 200
            body = resp.json()
            assert body["results"][0]["title"] == "cats.txt"

    def test_default_directory_cannot_be_deleted(self, client):
        """ST-012 (R7)"""
        default_dir = next(d for d in client.get("/config/directories").json() if d["is_default"])
        resp = client.delete(f"/config/directories/{default_dir['id']}")
        assert resp.status_code == 403

    def test_adding_nonexistent_directory_is_rejected(self, client):
        """ST-013 (R7)"""
        resp = client.post("/config/directories", json={"path": "/definitely/does/not/exist"})
        assert resp.status_code == 400

    def test_preprocessing_update_flags_reindex_required(self, client):
        """ST-014 (R8)"""
        resp = client.put("/config/preprocessing", json={"use_stemming": True})
        assert resp.status_code == 200
        assert resp.json()["reindex_required"] is True

    def test_search_then_feedback_changes_ranking(self, client):
        """ST-015 (R10)"""
        client.post("/index/build")
        first = client.post("/search", json={"query": "pets"}).json()["results"]
        cats_id = next(r["doc_id"] for r in first if r["title"] == "cats.txt")

        second = client.post("/search/feedback", json={
            "query": "pets", "relevant_doc_ids": [cats_id],
        }).json()

        assert first[0]["score"] != second[0]["score"]

    def test_related_documents_returns_list_response(self, client):
        client.post("/index/build")
        related = client.get("/documents/1/related?top_k=5")

        assert related.status_code == 200
        body = related.json()
        assert isinstance(body, list)
        assert body
        assert all("doc_id" in item and "title" in item for item in body)