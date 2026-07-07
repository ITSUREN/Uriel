# backend/app/services/snippet_service.py
import re
import html
import logging
from dataclasses import dataclass
from backend.app.parser.content_provider import ContentProvider

logger = logging.getLogger(__name__)
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
    Picks the most query-relevant excerpt from a document, reading it
    page-by-page from disk on demand (never storing full content in the DB,
    never holding more than one page in memory at a time). Only ever called
    on the already-ranked top_k results, so cost is bounded by top_k
    regardless of corpus size or document size.
    """
    def __init__(self, index_repo, content_provider: ContentProvider):
        self.index_repo = index_repo
        self.content_provider = content_provider

    def build(self, path: str, query_terms: set[str]) -> str:
        term_weights = self._term_weights(query_terms) if query_terms else {}

        best_page_chunks: list[tuple[str, int, int]] | None = None
        best_page_len = 0
        best_idx = -1
        best_score = 0.0
        first_page_fallback = ""

        try:
            for page_text in self.content_provider.iter_pages(path):
                if not page_text or not page_text.strip():
                    continue
                if not first_page_fallback:
                    first_page_fallback = page_text[:SNIPPET_TARGET_LENGTH]
                if not term_weights:
                    continue  # no query terms — we'll just fall back below

                page_chunks = self._split_into_chunks(page_text)
                if not page_chunks:
                    continue
                scored = [self._score_chunk(c, term_weights) for c in page_chunks]
                local_best = max(range(len(scored)), key=lambda i: scored[i].score)
                if scored[local_best].score > best_score:
                    best_score = scored[local_best].score
                    best_page_chunks = page_chunks
                    best_page_len = len(page_text)
                    best_idx = local_best
        except Exception:
            logger.exception("Failed to build snippet for %s", path)
            return ""

        if not term_weights:
            return html.escape(first_page_fallback)
        if best_page_chunks is None or best_score == 0:
            return self._highlight(first_page_fallback, term_weights)

        window_text, window_start, window_end = self._expand_window(best_page_chunks, best_idx)
        prefix = "..." if window_start > 0 else ""
        suffix = "..." if window_end < best_page_len else ""
        return f"{prefix}{self._highlight(window_text, term_weights)}{suffix}"

    # --- unchanged from before ---
    def _split_into_chunks(self, content: str) -> list[tuple[str, int, int]]:
        chunks = []
        for match in CHUNK_PATTERN.finditer(content):
            chunk_text = match.group().strip()
            if chunk_text:
                chunks.append((chunk_text, match.start(), match.end()))
        return chunks

    def _term_weights(self, query_terms: set[str]) -> dict[str, float]:
        return {term.lower(): 1.0 / (1 + self.index_repo.document_frequency(term)) for term in query_terms}

    def _score_chunk(self, chunk, term_weights) -> ScoredChunk:
        text, start, end = chunk
        lower = text.lower()
        score = sum(weight for term, weight in term_weights.items() if term in lower)
        return ScoredChunk(text=text, start=start, end=end, score=score)

    def _expand_window(self, chunks, best_idx: int) -> tuple[str, int, int]:
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
        pattern = re.compile("|".join(re.escape(html.escape(t)) for t in terms_sorted), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", escaped)