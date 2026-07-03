#backend/app/query_expansion/wodnet_expansion.py
import logging
from typing import Callable
from nltk.corpus import wordnet as wn 

logger = logging.getLogger(__name__)

class WordNetExpander:
    def __init__(self, max_synonyms_per_term: int = 2, synonym_weight: float = 0.5):
        self.max_synonyms_per_term = max_synonyms_per_term
        self.synonym_weight = synonym_weight

    def expand(self, query_terms: list[str], normalize: Callable[[str], list[str]]) -> dict[str, float]:
        """
        query_terms: already-preprocessed query terms.
        normalize: the preprocessing pipeline's term-extraction fn (e.g. preprocessor.process(s).terms),
                   used so raw WordNet lemma strings match the exact term form used in the index.
                   Multi-token results are dropped — the index is unigram-only, so phrase
                   synonyms ("large integer") can't match anything and are discarded rather
                   than silently broken into separate unrelated terms.
        """
        weights: dict[str, float] = {}
        for term in query_terms:
            weights[term] = weights.get(term, 0.0) + 1.0  # original query term weight

        for term in set(query_terms):
            for raw_synonym in self._raw_synonyms(term):
                normalized = normalize(raw_synonym)
                if len(normalized) !=1:
                    continue # skip multi-token synonyms, index is unigram-only and stopwords
                candidate =normalized[0]
                if candidate in weights:
                    continue # never downweight a term the user actually typed in the query
                weights[candidate] = self.synonym_weight 
        return weights
    
    def _raw_synonyms(self, term: str) -> list[str]:
        try:
            synsets = wn.synsets(term)
        except Exception:
            logger.exception("WordNet lookup failed for term: %s", term)
            return []
        
        found = []
        for synset in synsets:
            if synset is None:
                continue
            
            for lemma in synset.lemma_names():
                candidate = lemma.replace("_", " ")
                if candidate.lower() == term or candidate in found:
                    continue
                found.append(candidate)
                if len(found) >= self.max_synonyms_per_term:
                    return found
        return found
