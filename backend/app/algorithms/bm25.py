#backend/app/algorithms/bm25.py
import math
from collections import defaultdict
from .base import RankingAlgorithm
from backend.app.models.search_result import SearchResult

class BM25Ranking(RankingAlgorithm):
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def score(self, query_terms: list[str], index, documents, top_k=10) -> list[SearchResult]:
        n_docs = len(documents)
        if n_docs == 0:
            return []

        avg_doc_length = sum(doc.length for doc in documents.values()) / n_docs
        scores: dict[int, float] = defaultdict(float)

        for term in set(query_terms):
            postings = index.get_postings(term)
            df = len(postings)
            if df == 0:
                continue
            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)

            for posting in postings:
                doc = documents[posting.doc_id]
                tf = posting.term_frequency
                score = idf * ((tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * (doc.length / avg_doc_length))))
                scores[posting.doc_id] += score

        results = []
        for doc_id, raw_score in scores.items():
            results.append(SearchResult(
                doc_id=doc_id,
                score=raw_score,
                snippet=""
            ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
