# backend/analysis/corpus_walker.py
"""
Shadow indexing layer for analysis/graphing purposes only.

Mirrors what Indexer.index_directory() does (walk directory, parse
page-by-page, preprocess), but never touches the database or the real
index — exists purely so the analysis scripts can derive statistics
(term frequencies, vocabulary growth) without adding instrumentation to
backend/app/index/indexer.py.
"""
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterator

from backend.app.parser.pdf_parser import PDFParser
from backend.app.parser.txt_parser import TXTParser
from backend.app.preprocessing.config import PreprocessingConfig
from backend.app.preprocessing.preprocessing_factory import PreprocessingFactory


@dataclass
class FileTrace:
    path: str
    filename: str
    tokens_in_file: int          # tokens contributed by this file
    cumulative_tokens: int       # running total after this file (N)
    cumulative_vocab_size: int   # distinct terms seen so far (V) -- Heaps' law


@dataclass
class CorpusStats:
    term_frequencies: Counter = field(default_factory=Counter)
    total_tokens: int = 0
    files_processed: int = 0
    traces: list = field(default_factory=list)


def iter_indexable_files(directory: str) -> Iterator[str]:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".pdf") or file.endswith(".txt"):
                yield os.path.join(root, file)


def _iter_file_tokens(path: str, pdf_parser: PDFParser, txt_parser: TXTParser, preprocessor) -> Iterator[str]:
    pages = pdf_parser.iter_pages(path) if path.endswith(".pdf") else txt_parser.iter_pages(path)
    for page_text in pages:
        if not page_text or not page_text.strip():
            continue
        try:
            processed = preprocessor.process(page_text)
        except Exception:
            continue
        yield from processed.terms


def walk_corpus(
    directory: str,
    config: PreprocessingConfig | None = None,
    pdf_max_pages: int | None = None,
):
    """
    Walk `directory` exactly like Indexer.index_directory, yielding
    (FileTrace, CorpusStats) after each file finishes. Streams token-by-
    token per file rather than materializing the whole corpus, so this
    stays memory-safe on the same large PDFs the main indexer had to be
    fixed for.
    """
    stats = CorpusStats()
    pdf_parser = PDFParser(max_pages=pdf_max_pages)
    txt_parser = TXTParser()
    preprocessor = PreprocessingFactory.create(config or PreprocessingConfig())

    for path in iter_indexable_files(directory):
        file_token_count = 0
        for term in _iter_file_tokens(path, pdf_parser, txt_parser, preprocessor):
            stats.term_frequencies[term] += 1
            stats.total_tokens += 1
            file_token_count += 1
        stats.files_processed += 1
        trace = FileTrace(
            path=path,
            filename=os.path.basename(path),
            tokens_in_file=file_token_count,
            cumulative_tokens=stats.total_tokens,
            cumulative_vocab_size=len(stats.term_frequencies),
        )
        stats.traces.append(trace)
        yield trace, stats