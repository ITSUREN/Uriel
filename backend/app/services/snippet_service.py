#backend/app/services/snippet_service.py
import re
import html
from dataclasses import dataclass

CHUNK_PATTERN = re.compile(r'[^.!?\n]+[.!?]?')
SNIPPET_TARGET_LENGTH = 200

@dataclass
class ScoredChunk:
    text: str
    start: int
    end: int
    score: float

class SnippetBuilder:
    """
    Picks the most query-relevant excerpt from a document's stored content
    and highlights matched terms: a single flat pass over sentence/line-sized
    chunks, not a two-stage paragraph-then-line rank. A two-stage rank can
    lock in a mediocre paragraph before ever inspecting its lines; scoring
    all chunks in one pass avoids that and is cheaper to boot.

    Only ever called on the already-ranked top_k results (see
    SearchService._enrich), so cost is bounded by top_k regardless of
    corpus size,  this never runs against the whole corpus.
    """
    
    def __init__(self, index_repo):
        self.index_repo = index_repo # for idf-weighting which matched term matters more

    def build(self, content: str, query_terms: set[str]) -> str:
        """
        Returns a snippet of the document's content that is most relevant to the query terms.
        Highlights matched terms in the snippet.
        """
        if not content:
            return ""
        if not query_terms:
            return html.escape(content[:SNIPPET_TARGET_LENGTH])
        
        # Split content into chunks
        chunks = self._split_into_chunks(content)

        if not chunks:
            return html.escape(content[:SNIPPET_TARGET_LENGTH])
        
        # Score each chunk based on query term matches
        term_weights = self._term_weights(query_terms)
        scored_chunks =[self._score_chunk(chunk, term_weights) for chunk in chunks]
        best_idx = max(range(len(scored_chunks)), key = lambda i: scored_chunks[i].score)
        
        # Select the best chunk
        if scored_chunks[best_idx].score == 0:
            # no chunk matched at all (e.g. a filename-only query): just show the start.
            return self._highlight(content[:SNIPPET_TARGET_LENGTH], term_weights)

        window_text, window_start, window_end = self._expand_window(chunks, best_idx)
        prefix = "..." if window_start > 0 else ""
        suffix = "..." if window_end < len(content) else ""
        return f"{prefix}{self._highlight(window_text, term_weights)}{suffix}"

    def _split_into_chunks(self, content: str) -> list[tuple[str, int, int]]:
        """Split content into chunks based on sentence/line boundaries."""
        chunks = []
        for match in CHUNK_PATTERN.finditer(content):
            chunk_text = match.group().strip()
            if chunk_text:
                chunks.append((chunk_text, match.start(), match.end()))
        return chunks
    
    def _term_weights(self, query_terms: set[str]) -> dict[str, float]:
        """Calculate IDF-weighted scores for each query term."""
        # Rarer terms (higher df-based weight) count more toward picking a chunk —
        # a chunk matching a distinctive term beats one matching only common words.
        return {term.lower(): 1.0 / (1 + self.index_repo.document_frequency(term)) for term in query_terms}

    def _score_chunk(self, chunk: tuple[str, int, int], term_weights: dict[str, float]) -> ScoredChunk:
        text, start, end = chunk
        lower = text.lower()
        score = sum(weight for term, weight in term_weights.items() if term in lower)
        return ScoredChunk(text=text, start=start, end=end, score=score)

    def _expand_window(self, chunks, best_idx: int) -> tuple[str, int, int]:
        """Expand the best chunk to a window of approximately SNIPPET_TARGET_LEN."""
        selected = [chunks[best_idx]]
        total_length = len(chunks[best_idx][0])
        left, right = best_idx - 1, best_idx + 1
        while total_length < SNIPPET_TARGET_LENGTH and (left >= 0 or right < len(chunks)):
            if right < len(chunks):
                selected.append(chunks[right]); total_length += len(chunks[right][0]); right += 1
            elif left >= 0:
                selected.insert(0, chunks[left]); total_length += len(chunks[left][0]); left -= 1
        window_start = min(c[1] for c in selected)
        window_end = max(c[2] for c in selected)
        text = " ".join(c[0] for c in sorted(selected, key=lambda c: c[1]))
        return text, window_start, window_end
    
    def _highlight(self, text: str, term_weights: dict[str, float]) -> str:
        escaped = html.escape(text)
        terms_sorted = sorted(term_weights, key=len, reverse=True)
        if not terms_sorted:
            return escaped
        pattern = re.compile(
            "|".join(re.escape(html.escape(t)) for t in terms_sorted),
            re.IGNORECASE,
        )
        return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", escaped)