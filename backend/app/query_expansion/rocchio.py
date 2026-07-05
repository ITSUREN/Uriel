#backend/app/query_expansion/rocchio.py
import math
from dataclasses import dataclass
from backend.app.storage.base import IndexRepository

@dataclass
class RocchioParams:
    alpha: float = 1.0
    beta: float = 0.75
    gamma: float = 0.15

class RocchioFeedback:
    def __init__(self, index_repo: IndexRepository, params: RocchioParams = RocchioParams()):
        self.index_repo = index_repo
        self.params = params

    def _doc_vector(self, doc_id: int, n_docs: int) -> dict[str, float]:
        """Compute the term vector for a document"""
        term_freqs = self.index_repo.get_document_terms(doc_id)
        vector = {}

        for term, tf in term_freqs.items():
            df = self.index_repo.document_frequency(term)
            if df == 0:
                continue
            idf = math.log((1+n_docs)/(1+df))+1
            vector[term] = (math.log(tf)+1) * idf
        return vector
    
    def expand(self, query_weights: dict[str, float], relevant_doc_ids: list[int], non_relevant_doc_ids: list[int], n_docs: int) -> dict[str, float]:
        """Expand the query using Rocchio's algorithm"""
        new_query_weights = {}
        # Start with the original query weights scaled by alpha
        for term, weight in query_weights.items():
            new_query_weights[term] = self.params.alpha * weight

        # Add contributions from relevant documents
        if relevant_doc_ids:
            beta_factor = self.params.beta / len(relevant_doc_ids)
            for doc_id in relevant_doc_ids:
                for term, weight in self._doc_vector(doc_id, n_docs).items():
                    new_query_weights[term] = new_query_weights.get(term, 0.0) + beta_factor * weight

        # Add contributions from non-relevant documents
        if non_relevant_doc_ids:
            gamma_factor = self.params.gamma / len(non_relevant_doc_ids)
            for doc_id in non_relevant_doc_ids:
                for term, weight in self._doc_vector(doc_id, n_docs).items():
                    new_query_weights[term] = new_query_weights.get(term, 0.0) - gamma_factor * weight

        return {term: w for term, w in new_query_weights.items() if w > 0.0}
        