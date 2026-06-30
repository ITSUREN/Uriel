from collections import defaultdict
from backend.app.models.posting import Posting

class InvertedIndex:
    def __init__(self):
        self.index:defaultdict[str, list[Posting]] = defaultdict(list)

    def add_posting(self, term: str, posting: Posting):
        self.index[term].append(posting)
    
    def get_postings(self, term: str) -> list[Posting]:
        return self.index.get(term, [])
    
    def vocabulary_size(self) -> int:
        return len(self.index)