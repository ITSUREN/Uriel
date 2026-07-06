#backend/app/index/inverted_index.py
from collections import defaultdict
from backend.app.models.posting import Posting
from backend.app.storage.base import IndexRepository

class InvertedIndex:
    def __init__(self):
        self.index: defaultdict[str, list[Posting]] = defaultdict(list)
        self.document_terms: dict[int, dict[str, int]] = {}

    def add_posting(self, term: str, postings: list[Posting]) -> None:
        self.index[term].extend(postings)

    def add_postings_bulk(self, entries: list[tuple[str, list[Posting]]]) -> None:
        for term, postings in entries:
            self.add_posting(term, postings)

    def get_postings(self, term: str) -> list[Posting]:
        return self.index.get(term, [])

    def vocabulary_size(self) -> int:
        return len(self.index)

    def document_frequency(self, term: str) -> int:
        return len(self.index.get(term, []))

    def clear(self) -> None:
        self.index.clear()
        self.document_terms.clear()

    def add_document_terms(self, doc_id: int, term_freqs: dict[str, int]) -> None:
        self.document_terms[doc_id] = term_freqs

    def get_document_terms(self, doc_id: int) -> dict[str, int]:
        return self.document_terms.get(doc_id, {})

    def get_vocabulary(self) -> list[str]:
        return list(self.index.keys())