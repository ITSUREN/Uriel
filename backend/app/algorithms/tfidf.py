#backend/app/algorithms/tfidf.py
import math
from collections import defaultdict
from .base import RankingAlgorithm
from backend.app.models.search_result import SearchResult

class TFIDFRanking(RankingAlgorithm):
    """TF-IDF ranking algorithm implementation"""

    def score(self, query_terms: list[str], index, documents, top_k: int = 10) -> list[SearchResult]:
        n_docs = len(documents)
        if n_docs == 0:
            return []
        
        scores: dict[int, float] = defaultdict(float)
        # conversion of query_terms to a set to avoid duplicate scoring for the same term
        seen_terms = set(query_terms)

        for term in seen_terms:
            postings = index.get_postings(term)

            df = len(postings)
            if df == 0:
                continue
            # using smooothed idf, always positive
            idf = math.log((1+n_docs)/(1+df))+1

            for posting in postings:
                tf_weight = 1 + math.log(posting.term_frequency)
                scores[posting.doc_id] += tf_weight * idf

        
        # Normalize scores by document length (crude cosine-ish normalization)
        results = []
        for doc_id, raw_score in scores.items():
            doc = documents[doc_id]
            norm = math.sqrt(doc.length) if doc.length > 0 else 1
            results.append(SearchResult(
                doc_id=doc_id,
                score=raw_score / norm,
                snippet=""
            ))
        
        # Reversed here to sort in descending order of score i.e. highest score first
        results.sort(key=lambda r : r.score, reverse = True)
        return results[:top_k]