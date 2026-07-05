from backend.app.storage.base import IndexRepository
from backend.app.models.posting import Posting


class FakeIndexRepo(IndexRepository):
    """
    In-memory stand-in for IndexRepository, shared by ranking-algorithm and
    Rocchio unit tests. Inherits the ABC (not just duck-typed) so pyright
    accepts it wherever `index_repo: IndexRepository` is declared, and so
    Python enforces at instantiation that every abstract method is actually
    implemented — an interface change breaks this fake loudly instead of
    letting it silently drift out of sync with the real repository.
    """
    def __init__(self, postings_by_term: dict[str, list[Posting]] | None = None,
                 doc_terms: dict[int, dict[str, int]] | None = None):
        self._postings = postings_by_term or {}
        self._doc_terms = doc_terms or {}

    def add_posting(self, term: str, postings: list[Posting]) -> None:
        self._postings.setdefault(term, []).extend(postings)

    def get_postings(self, term: str) -> list[Posting]:
        return self._postings.get(term, [])

    def vocabulary_size(self) -> int:
        return len(self._postings)

    def clear(self) -> None:
        self._postings.clear()
        self._doc_terms.clear()

    def document_frequency(self, term: str) -> int:
        return len(self._postings.get(term, []))

    def add_document_terms(self, doc_id: int, term_freqs: dict[str, int]) -> None:
        self._doc_terms[doc_id] = term_freqs

    def get_document_terms(self, doc_id: int) -> dict[str, int]:
        return self._doc_terms.get(doc_id, {})

    def get_vocabulary(self) -> list[str]:
        return list(self._postings.keys())